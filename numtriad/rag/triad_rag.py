# numtriad/rag/triad_rag.py

from dataclasses import dataclass
from typing import List, Tuple, Optional

import numpy as np

from ..encoders.numtriad_text_v2 import NumTriadTextEncoderV2
from ..triad_types import Triad
from ..config import NumTriadConfig


@dataclass
class TriadIndexedDoc:
    doc_id: str
    text: str
    embedding: np.ndarray  # E(x) complet
    triad: Triad


class TriadRAGEngine:
    """
    RAG simple triad-aware en mémoire.
    """

    def __init__(self, config: Optional[NumTriadConfig] = None):
        self.config = config or NumTriadConfig()
        self.encoder = NumTriadTextEncoderV2(self.config)
        self.docs: List[TriadIndexedDoc] = []

    def index(self, doc_ids: List[str], texts: List[str]) -> None:
        """
        Indexer une liste de docs en mémoire.
        """
        enc = self.encoder.encode(texts)
        for i, doc_id in enumerate(doc_ids):
            emb = enc.embeddings[i]
            triad = enc.triads[i]
            self.docs.append(
                TriadIndexedDoc(
                    doc_id=doc_id,
                    text=texts[i],
                    embedding=emb,
                    triad=triad,
                )
            )

    def _cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        na = np.linalg.norm(a) or 1.0
        nb = np.linalg.norm(b) or 1.0
        return float(a.dot(b) / (na * nb))

    def _triad_cosine(self, t1: Triad, t2: Triad) -> float:
        a = t1.as_array()
        b = t2.as_array()
        return self._cosine(a, b)

    def search(
        self,
        query: str,
        k: int = 5,
        triad_bias: Optional[Triad] = None,
    ) -> List[Tuple[TriadIndexedDoc, float]]:
        """
        Recherche triad-aware sur l'index interne.

        triad_bias : optionnel, pour forcer vers +abstrait/+concret, etc.
        """
        q_enc = self.encoder.encode([query])
        q_emb = q_enc.embeddings[0]
        q_triad = q_enc.triads[0]

        results: List[Tuple[TriadIndexedDoc, float]] = []

        for doc in self.docs:
            # split embedding : base + triad
            v_dim = len(q_emb) - 3
            q_v = q_emb[:v_dim]
            d_v = doc.embedding[:v_dim]

            cos_sem = self._cosine(q_v, d_v)
            cos_tri = self._triad_cosine(q_triad, doc.triad)

            # si triad_bias fourni, on ajoute une "tension"
            if triad_bias is not None:
                bias_cos = self._triad_cosine(triad_bias, doc.triad)
            else:
                bias_cos = 0.0

            score = (
                self.config.alpha_semantic * cos_sem
                + self.config.beta_triad * cos_tri
                + 0.1 * bias_cos
            )

            results.append((doc, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]
