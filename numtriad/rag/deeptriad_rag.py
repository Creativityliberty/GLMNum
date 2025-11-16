# numtriad/rag/deeptriad_rag.py
"""
DeepTriad RAG Index - Moteur de recherche triad-aware
=====================================================

Indexe des documents avec NumTriadEmbeddingV3 et permet une recherche
tenant compte de la similarité sémantique ET du niveau d'abstraction.

Author: GLM Research Team
Date: 2024-11-16
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Literal, Tuple

import numpy as np

from ..triad_types import Triad
from ..config import NumTriadConfig
from ..encoders.numtriad_v3 import NumTriadEmbeddingV3, NumTriadV3Config, TriadTargetMode


RetrievalMode = Literal["cosine", "triad_weighted"]


@dataclass
class DeepTriadDocument:
    """Représentation d'un document indexé"""
    doc_id: str
    text: str
    meta: Dict[str, Any]
    embedding: np.ndarray    # (dim+3,)
    triad: Triad


class DeepTriadRAGIndex:
    """
    Moteur RAG triad-aware :
      - indexe des documents avec NumTriadEmbeddingV3
      - recherche par similarité + distance triadique
      - permet de contrôler le niveau d'abstraction de la réponse
    """

    def __init__(
        self,
        base_config: NumTriadConfig,
        v3_config: NumTriadV3Config,
        retrieval_mode: RetrievalMode = "triad_weighted",
        triad_weight: float = 0.3,
    ):
        self.cfg = base_config
        self.v3_cfg = v3_config
        self.encoder = NumTriadEmbeddingV3(base_config, v3_config)
        self.retrieval_mode = retrieval_mode
        self.triad_weight = triad_weight

        self.docs: List[DeepTriadDocument] = []
        self.emb_matrix: Optional[np.ndarray] = None  # (N,dim+3)

    # -----------------------
    # gestion index
    # -----------------------

    def _rebuild_matrix(self):
        """Reconstruit la matrice d'embeddings"""
        if not self.docs:
            self.emb_matrix = None
            return
        self.emb_matrix = np.stack([d.embedding for d in self.docs], axis=0)

    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        triad_mode: TriadTargetMode = "auto",
    ):
        """Ajoute des documents à l'index"""
        N = len(texts)
        if metadatas is None:
            metadatas = [{} for _ in range(N)]
        if ids is None:
            ids = [f"doc_{len(self.docs) + i}" for i in range(N)]

        enriched, triads = self.encoder.encode(
            texts,
            triad_mode=triad_mode,
            return_raw=False,
        )  # enriched: (N,dim+3)

        for i in range(N):
            self.docs.append(
                DeepTriadDocument(
                    doc_id=ids[i],
                    text=texts[i],
                    meta=metadatas[i],
                    embedding=enriched[i],
                    triad=triads[i],
                )
            )

        self._rebuild_matrix()
        print(f"✅ Added {N} documents. Index size: {len(self.docs)}")

    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de l'index"""
        if not self.docs:
            return {"num_docs": 0, "embedding_dim": 0}
        
        return {
            "num_docs": len(self.docs),
            "embedding_dim": self.docs[0].embedding.shape[0],
            "retrieval_mode": self.retrieval_mode,
            "triad_weight": self.triad_weight,
        }

    # -----------------------
    # métriques
    # -----------------------

    @staticmethod
    def _cosine_sim(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Calcule la similarité cosinus entre a et chaque ligne de b"""
        # a: (d,), b: (N,d)
        a_norm = a / (np.linalg.norm(a) + 1e-8)
        b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-8)
        return (b_norm @ a_norm)

    @staticmethod
    def _triad_distance(tq: Triad, td: Triad) -> float:
        """Calcule la distance L1 entre deux triades"""
        a = tq.as_array()
        b = td.as_array()
        return float(np.abs(a - b).sum())

    # -----------------------
    # recherche
    # -----------------------

    def search(
        self,
        query: str,
        k: int = 5,
        triad_target: TriadTargetMode = "auto",
        retrieval_mode: Optional[RetrievalMode] = None,
    ) -> List[Tuple[DeepTriadDocument, float]]:
        """
        Recherche triad-aware :

          - encode la question avec NumTriadEmbeddingV3
          - calcule similarité cosinus
          - ajuste le score avec la distance triadique (si mode triad_weighted)

        triad_target :
          - "abstract" : favorisera les documents plus abstraits
          - "concrete" : favorisera les documents plus concrets
          - "balanced" : recentre la triade
          - "auto"     : garde la triade naturelle de la question
        """
        if self.emb_matrix is None or not len(self.docs):
            return []

        # encode la question
        q_enriched, [q_triad] = self.encoder.encode(
            [query],
            triad_mode=triad_target,
            return_raw=False,
        )  # (1,dim+3), [Triad]
        q_vec = q_enriched[0]

        mode = retrieval_mode or self.retrieval_mode

        # similarité cosinus
        sims = self._cosine_sim(q_vec, self.emb_matrix)  # (N,)

        if mode == "cosine":
            # top-k sur sims
            idxs = np.argsort(-sims)[:k]
            return [(self.docs[i], float(sims[i])) for i in idxs]

        # sinon mode triad_weighted
        scores = []
        for i, d in enumerate(self.docs):
            triad_dist = self._triad_distance(q_triad, d.triad)
            score = float(sims[i]) - self.triad_weight * triad_dist
            scores.append(score)

        scores = np.asarray(scores)
        idxs = np.argsort(-scores)[:k]

        return [(self.docs[i], float(scores[i])) for i in idxs]

    def search_batch(
        self,
        queries: List[str],
        k: int = 5,
        triad_target: TriadTargetMode = "auto",
    ) -> List[List[Tuple[DeepTriadDocument, float]]]:
        """Recherche batch"""
        return [self.search(q, k=k, triad_target=triad_target) for q in queries]
