# numtriad/encoders/numtriad_multimodal_v3.py

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple

import numpy as np
import torch

from .base_text_encoder import BaseTextEncoder
from .vision_encoder import VisionEncoder
from ..models.triad_fusion_head_v3 import TriadFusionHeadV3
from ..triad_types import Triad
from ..config import NumTriadConfig
from .numtriad_text_v2 import basic_linguistic_features


@dataclass
class NumTriadMultimodalEmbeddingV3:
    """
    Conteneur pour embedding multimodal.
    """
    embeddings: np.ndarray       # (B, dim_text + dim_vis + 3)
    triads: List[Triad]
    meta: Optional[Dict[str, Any]] = None


class NumTriadMultimodalEncoderV3:
    """
    Encoder multimodal :
      - texte (optionnel)
      - image (optionnelle)
    E_V3(x) = [ v_text | v_vision | ∆̂ | ∞̂ | Θ̂ ]

    Cas possibles :
      - texte seul
      - image seule
      - texte + image
    """

    def __init__(self, config: Optional[NumTriadConfig] = None):
        self.config = config or NumTriadConfig()
        self.device = torch.device(self.config.device)

        # Encoders
        self.text_encoder = BaseTextEncoder(self.config.base_text_model_name)
        self.vision_encoder = VisionEncoder(device=self.config.device)

        text_dim = self.text_encoder.dim
        vision_dim = self.vision_encoder.dim

        feat_dim = 0
        if self.config.use_linguistic_features:
            feat_dim = self.config.linguistic_feature_dim

        self.triad_head = TriadFusionHeadV3(
            text_dim=text_dim,
            vision_dim=vision_dim,
            feat_dim=feat_dim,
            hidden_dim=max(512, self.config.triad_hidden_dim),
            dropout=self.config.triad_dropout,
        ).to(self.device)

    def _encode_text(
        self,
        texts: Optional[List[str]],
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        if texts is None:
            # batch size = à définir plus tard
            return None, None
        v_text = self.text_encoder.encode(texts)  # (B, text_dim)
        if self.config.use_linguistic_features:
            feats = np.stack([basic_linguistic_features(t) for t in texts], axis=0)
        else:
            feats = None
        return v_text, feats

    def _encode_images(
        self,
        images: Optional[List["PIL.Image.Image"]],
    ) -> Optional[np.ndarray]:
        if images is None:
            return None
        v_vis = self.vision_encoder.encode(images)  # (B, vision_dim)
        return v_vis

    @torch.no_grad()
    def encode(
        self,
        texts: Optional[List[str]] = None,
        images: Optional[List["PIL.Image.Image"]] = None,
        return_full: bool = True,
    ) -> NumTriadMultimodalEmbeddingV3:
        """
        Encode un batch multimodal.
        On suppose :
          - soit len(texts) = B
          - soit len(images) = B
          - soit les deux, mêmes tailles
        """

        if texts is None and images is None:
            raise ValueError("Au moins textes ou images doivent être fournis.")

        batch_size = None
        if texts is not None:
            batch_size = len(texts)
        if images is not None:
            if batch_size is None:
                batch_size = len(images)
            else:
                assert len(images) == batch_size, "Taille textes/images mismatch."

        # 1) Encode text
        if texts is not None:
            v_text, feats_np = self._encode_text(texts)
        else:
            v_text = np.zeros((batch_size, self.text_encoder.dim), dtype=float)
            feats_np = None

        # 2) Encode images
        if images is not None:
            v_vis = self._encode_images(images)
        else:
            v_vis = np.zeros((batch_size, self.vision_encoder.dim), dtype=float)

        # 3) Triad from fusion
        text_t = torch.tensor(v_text, dtype=torch.float32, device=self.device)
        vis_t = torch.tensor(v_vis, dtype=torch.float32, device=self.device)

        if feats_np is not None:
            feats_t = torch.tensor(feats_np, dtype=torch.float32, device=self.device)
        else:
            feats_t = None

        triads = self.triad_head.predict_triad(text_t, vis_t, feats_t)
        triad_array = np.stack([t.as_array() for t in triads], axis=0)  # (B, 3)

        if return_full:
            full = np.concatenate([v_text, v_vis, triad_array], axis=-1)
        else:
            full = np.concatenate([v_text, v_vis], axis=-1)

        meta = {
            "text_embeddings": v_text,
            "vision_embeddings": v_vis,
        }

        return NumTriadMultimodalEmbeddingV3(
            embeddings=full,
            triads=triads,
            meta=meta,
        )
