# numtriad/encoders/numtriad_v3.py
"""
NumTriadEmbeddingV3 : Encodeur triadique avancé avec DeepTriad
=============================================================

Utilise BaseTextEncoder + DeepTriadTransformer pour produire des embeddings
enrichis avec triades prédites au niveau séquence.

Author: GLM Research Team
Date: 2024-11-16
"""

from dataclasses import dataclass
from typing import List, Optional, Literal, Tuple

import numpy as np
import torch

from ..triad_types import Triad
from ..config import NumTriadConfig
from .base_text_encoder import BaseTextEncoder
from ..models.deeptriad_transformer import DeepTriadTransformer, DeepTriadTransformerConfig


TriadTargetMode = Literal[
    "auto",         # triade prédit par DeepTriad
    "abstract",     # booster ∆, ∞
    "balanced",     # garder la triade équilibrée
    "concrete"      # booster Θ
]


@dataclass
class NumTriadV3Config:
    """
    Config locale pour NumTriadEmbeddingV3
    (par dessus NumTriadConfig global).
    """
    deeptriad_ckpt: str
    max_len: int = 16
    triad_target_mode: TriadTargetMode = "auto"
    triad_alpha: float = 1.0     # poids de la triade dans l'embedding concaténé


class NumTriadEmbeddingV3:
    """
    Encodeur triadique avancé :
      - utilise BaseTextEncoder pour les embeddings de base
      - utilise DeepTriadTransformer pour prédire un niveau d'abstraction global
      - retourne :
          * embeddings bruts
          * triade (∆,∞,Θ)
          * embedding enrichi [v | α * triad]
    """

    def __init__(
        self,
        config: NumTriadConfig,
        v3_config: NumTriadV3Config,
        device: Optional[str] = None,
    ):
        self.cfg = config
        self.v3_cfg = v3_config
        self.device = torch.device(device or config.device)

        # encodeur texte gelé
        self.base_encoder = BaseTextEncoder(config.base_text_model_name)

        # chargement DeepTriad
        try:
            ckpt = torch.load(self.v3_cfg.deeptriad_ckpt, map_location=self.device)
            dt_cfg = DeepTriadTransformerConfig(**ckpt["config"])
            input_dim = ckpt["input_dim"]

            self.deeptriad = DeepTriadTransformer(input_dim=input_dim, config=dt_cfg).to(self.device)
            self.deeptriad.load_state_dict(ckpt["model_state_dict"])
            self.deeptriad.eval()
            self.deeptriad_available = True
        except Exception as e:
            print(f"⚠️ DeepTriad checkpoint not found: {e}")
            print("   Using fallback: average embedding without DeepTriad")
            self.deeptriad = None
            self.deeptriad_available = False

        self.input_dim = self.base_encoder.dim
        self.max_len = self.v3_cfg.max_len

    # -----------------------
    # Helpers internes
    # -----------------------

    def _chunk_text(self, text: str) -> List[str]:
        """
        Version simple : split sur les points.
        Plus tard tu peux remplacer par un vrai tokenizer de phrases.
        """
        chunks = [s.strip() for s in text.split(".") if s.strip()]
        if not chunks:
            chunks = [text.strip()]
        return chunks[: self.max_len]

    def _encode_sequence(self, text: str) -> Tuple[np.ndarray, Triad]:
        """
        Encode un texte comme séquence de chunks, et retourne :
        - v_seq : embedding moyen des chunks (np.array dim)
        - triad : triade globale prédite par DeepTriad
        """
        chunks = self._chunk_text(text)
        embs = self.base_encoder.encode(chunks)  # (L,dim)
        L, D = embs.shape

        # embedding global = moyenne des chunks
        v_seq = embs.mean(axis=0)

        # prédire triade avec DeepTriad si disponible
        if self.deeptriad_available and self.deeptriad is not None:
            # préparation batch (1,L,dim)
            x = torch.tensor(embs, dtype=torch.float32, device=self.device).unsqueeze(0)
            mask = torch.zeros(1, L, dtype=torch.bool, device=self.device)

            with torch.no_grad():
                triads = self.deeptriad.predict_triad_global(
                    x,
                    triad_control=None,
                    src_key_padding_mask=mask,
                )
            triad = triads[0]
        else:
            # fallback : triade équilibrée
            triad = Triad.normalize([1/3, 1/3, 1/3])

        return v_seq, triad

    def _apply_triad_target(self, triad: Triad, mode: TriadTargetMode) -> Triad:
        """
        Pour le RAG / contrôle, on peut ajuster légèrement la triade cible
        en fonction du mode souhaité (à la volée).
        """
        arr = triad.as_array()

        if mode == "abstract":
            # booster ∆,∞ ; réduire Θ
            arr = arr.copy()
            arr[0] += 0.15  # ∆
            arr[1] += 0.15  # ∞
            arr[2] -= 0.15  # Θ
        elif mode == "concrete":
            # booster Θ ; réduire ∆,∞
            arr = arr.copy()
            arr[0] -= 0.15
            arr[1] -= 0.15
            arr[2] += 0.30
        elif mode == "balanced":
            # léger recentrage
            arr = 0.5 * arr + 0.5 * np.array([1/3, 1/3, 1/3], dtype="float32")
        else:
            # "auto" → on garde la triade telle quelle
            pass

        return Triad.normalize(arr)

    # -----------------------
    # API publique
    # -----------------------

    def encode(
        self,
        texts: List[str],
        triad_mode: TriadTargetMode = "auto",
        return_raw: bool = False,
    ):
        """
        Encode une liste de textes avec DeepTriad comme head avancée.
        Retourne par défaut :
          - enriched : np.ndarray (N, dim+3)
          - triads   : List[Triad]
        Si return_raw=True :
          - base_emb : (N,dim)
          - enriched : (N,dim+3)
          - triads   : List[Triad]
        """
        base_vecs = []
        triads = []

        for t in texts:
            v_seq, triad = self._encode_sequence(t)
            triad_adj = self._apply_triad_target(triad, triad_mode)
            base_vecs.append(v_seq)
            triads.append(triad_adj)

        base_arr = np.stack(base_vecs, axis=0)                 # (N,dim)
        triad_arr = np.stack([tr.as_array() for tr in triads], axis=0)  # (N,3)

        # embedding enrichi
        enriched = np.concatenate(
            [base_arr, self.v3_cfg.triad_alpha * triad_arr],
            axis=1,
        )  # (N, dim+3)

        if return_raw:
            return base_arr, enriched, triads
        return enriched, triads
