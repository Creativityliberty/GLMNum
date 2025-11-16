# numtriad/encoders/numtriad_text_v2.py

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

import numpy as np
import torch

from .base_text_encoder import BaseTextEncoder
from ..models.triad_scorer_mlp_v2 import TriadScorerMLP_V2
from ..triad_types import Triad
from ..config import NumTriadConfig


def basic_linguistic_features(text: str) -> np.ndarray:
    """
    Features très simples pour commencer :
      - longueur en tokens (approx)
      - longueur en caractères
      - densité de ponctuation
      - densité de chiffres
      - ratio majuscules
      - etc. (ici on fait une version minimaliste)
    """
    t = text.strip()
    length_chars = len(t)
    tokens = t.split()
    length_tokens = len(tokens) or 1

    punct = sum(c in ".,;:!?…" for c in t)
    digits = sum(c.isdigit() for c in t)
    uppers = sum(c.isupper() for c in t)

    return np.array(
        [
            length_tokens,
            length_chars,
            punct / max(1, length_chars),
            digits / max(1, length_chars),
            uppers / max(1, length_chars),
        ],
        dtype=float,
    )


@dataclass
class NumTriadTextEmbeddingV2:
    """
    Conteneur résultat : embedding + triad + meta éventuelles.
    """
    embeddings: np.ndarray
    triads: List[Triad]
    meta: Optional[Dict[str, Any]] = None


class NumTriadTextEncoderV2:
    """
    Pipeline complet :
      texte -> v_text -> features (optionnel) -> triad -> concat final.

    E(x) = [ v_text | ∆̂ | ∞̂ | Θ̂ ]
    """

    def __init__(self, config: Optional[NumTriadConfig] = None):
        self.config = config or NumTriadConfig()
        self.text_encoder = BaseTextEncoder(self.config.base_text_model_name)

        feat_dim = self.config.linguistic_feature_dim if self.config.use_linguistic_features else 0

        self.triad_scorer = TriadScorerMLP_V2(
            base_dim=self.text_encoder.dim,
            feat_dim=feat_dim,
            hidden_dim=self.config.triad_hidden_dim,
            dropout=self.config.triad_dropout,
        )

        self.device = torch.device(self.config.device)
        self.triad_scorer.to(self.device)

    def _compute_features(self, texts: List[str]) -> Optional[np.ndarray]:
        if not self.config.use_linguistic_features:
            return None
        feats = [basic_linguistic_features(t) for t in texts]
        # Si moins de features réelles que config, on pad
        feats_arr = np.stack(feats, axis=0)  # (batch, feat_dim_actual)
        # Optionnel : normalisation
        return feats_arr

    @torch.no_grad()
    def encode(
        self,
        texts: List[str],
        return_full: bool = True,
    ) -> NumTriadTextEmbeddingV2:
        """
        Encode une liste de textes.

        Retourne :
          - embeddings NumPy (batch, dim + 3) si return_full
          - triads apprise
        """
        # 1. v_text
        v_text = self.text_encoder.encode(texts)  # (batch, dim)

        # 2. features linguistiques
        feats_np = self._compute_features(texts)
        if feats_np is not None:
            feats = torch.tensor(feats_np, dtype=torch.float32, device=self.device)
        else:
            feats = None

        # 3. triads
        emb_t = torch.tensor(v_text, dtype=torch.float32, device=self.device)
        triads = self.triad_scorer.predict_triad(emb_t, feats)

        if return_full:
            triad_array = np.stack([t.as_array() for t in triads], axis=0)  # (batch, 3)
            full = np.concatenate([v_text, triad_array], axis=-1)
        else:
            full = v_text

        return NumTriadTextEmbeddingV2(
            embeddings=full,
            triads=triads,
            meta={"base_embeddings": v_text},
        )
