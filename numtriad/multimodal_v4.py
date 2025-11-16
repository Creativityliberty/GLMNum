# numtriad/multimodal_v4.py
"""
NumTriad Multimodal V4 - Pillar A
==================================

Unified multimodal embedding system combining:
- Text, Vision, Code, Audio encoders
- Common projection space (dim_proj)
- Triad prediction head (∆∞Θ)
- Cross-modal coherence vector (T_cross)

Final embedding:
E(x) = [ v_semantic | triad_probs(∆,∞,Θ) | T_cross ]

Author: GLM Research Team
Date: 2024-11-16
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict, Literal, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# ============================================================================
# 1. TYPES & CONFIGURATION
# ============================================================================

Modality = Literal["text", "vision", "code", "audio"]


@dataclass
class MultimodalV4Config:
    """
    Configuration for NumTriad Multimodal V4.
    
    Customize dimensions based on your real models.
    """
    # Raw input dimensions per modality
    dim_text_in: int = 768
    dim_vision_in: int = 768
    dim_code_in: int = 512
    dim_audio_in: int = 512

    # Common projection dimension
    dim_proj: int = 384

    # Cross-modal coherence vector dimension
    dim_t_cross: int = 32

    # Fusion encoder depth
    fusion_hidden_dim: int = 512
    fusion_num_layers: int = 2

    # Global dropout
    dropout: float = 0.1

    # Default device
    device: str = "cpu"


# ============================================================================
# 2. TRIAD (∆∞Θ)
# ============================================================================

class Triad:
    """
    Triadic representation (∆, ∞, Θ) with softmax normalization.
    
    ∆ (Delta): Complexity
    ∞ (Infinity): Generality
    Θ (Theta): Concreteness
    """

    def __init__(self, delta: float, infinity: float, theta: float):
        arr = np.asarray([delta, infinity, theta], dtype="float32")
        arr = np.maximum(arr, 1e-8)
        arr = arr / np.sum(arr)
        self.delta = float(arr[0])
        self.infinity = float(arr[1])
        self.theta = float(arr[2])

    def as_array(self) -> np.ndarray:
        """Returns triad as numpy array."""
        return np.asarray([self.delta, self.infinity, self.theta], dtype="float32")

    def __repr__(self) -> str:
        return f"Triad(Δ={self.delta:.3f}, ∞={self.infinity:.3f}, Θ={self.theta:.3f})"

    @staticmethod
    def from_logits(logits: torch.Tensor) -> "Triad":
        """
        Create Triad from logits.
        
        Args:
            logits: Tensor of shape (3,)
        """
        probs = F.softmax(logits.float(), dim=-1).detach().cpu().numpy()
        return Triad(float(probs[0]), float(probs[1]), float(probs[2]))


# ============================================================================
# 3. BASE ENCODERS (Stubs / Light)
# ============================================================================

class SimpleTextEncoder(nn.Module):
    """
    Stub text encoder.
    
    In production, replace with: BGE, Jina, Nomic, SentenceTransformer, etc.
    """

    def __init__(self, dim_out: int):
        super().__init__()
        self.dim_out = dim_out
        self.proj = nn.Linear(128, dim_out)

    def forward(self, texts: List[str]) -> torch.Tensor:
        """
        Args:
            texts: List of strings
            
        Returns:
            Tensor of shape (N, dim_out)
        """
        batch = []
        for t in texts:
            v = np.zeros(128, dtype="float32")
            for c in t[:256]:
                v[ord(c) % 128] += 1.0
            v = v / (np.linalg.norm(v) + 1e-8)
            batch.append(v)
        arr = torch.tensor(np.stack(batch, axis=0), dtype=torch.float32)
        return self.proj(arr)


class SimpleCodeEncoder(nn.Module):
    """
    Stub code encoder.
    
    In production, replace with: CodeBERT, StarCoder, etc.
    """

    def __init__(self, dim_out: int):
        super().__init__()
        self.dim_out = dim_out
        self.proj = nn.Linear(128, dim_out)

    def forward(self, codes: List[str]) -> torch.Tensor:
        """
        Args:
            codes: List of code strings
            
        Returns:
            Tensor of shape (N, dim_out)
        """
        batch = []
        for t in codes:
            v = np.zeros(128, dtype="float32")
            for c in t[:512]:
                v[ord(c) % 128] += 1.0
            v = v / (np.linalg.norm(v) + 1e-8)
            batch.append(v)
        arr = torch.tensor(np.stack(batch, axis=0), dtype=torch.float32)
        return self.proj(arr)


class SimpleVisionEncoder(nn.Module):
    """
    Stub vision encoder.
    
    In production, replace with: CLIP, ViT, Nomic Vision, etc.
    """

    def __init__(self, dim_out: int):
        super().__init__()
        self.dim_out = dim_out
        self.conv = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.pool = nn.AdaptiveAvgPool2d((4, 4))
        self.fc = nn.Linear(16 * 4 * 4, dim_out)

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        """
        Args:
            images: Tensor of shape (N, 3, H, W) normalized
            
        Returns:
            Tensor of shape (N, dim_out)
        """
        x = F.relu(self.conv(images))
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)


class SimpleAudioEncoder(nn.Module):
    """
    Stub audio encoder.
    
    In production, replace with: wav2vec2, Whisper, etc.
    """

    def __init__(self, dim_out: int):
        super().__init__()
        self.dim_out = dim_out
        self.fc1 = nn.Linear(128, 256)
        self.fc2 = nn.Linear(256, dim_out)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        """
        Args:
            features: Tensor of shape (N, 128) - e.g., MFCC features
            
        Returns:
            Tensor of shape (N, dim_out)
        """
        x = F.relu(self.fc1(features))
        x = self.fc2(x)
        return x


# ============================================================================
# 4. PROJECTIONS & FUSION
# ============================================================================

class ModalityProjector(nn.Module):
    """
    Projects each modality to a common space (dim_proj).
    """

    def __init__(self, dim_in: int, dim_proj: int, dropout: float):
        super().__init__()
        self.linear = nn.Linear(dim_in, dim_proj)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.dropout(F.relu(self.linear(x)))


class FusionEncoder(nn.Module):
    """
    Multimodal fusion encoder.
    
    Takes stacked modality vectors and produces fused semantic embedding.
    """

    def __init__(self, dim_proj: int, hidden_dim: int, num_layers: int, dropout: float):
        super().__init__()
        layers = []
        in_dim = dim_proj
        for _ in range(num_layers):
            layers.append(nn.Linear(in_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            in_dim = hidden_dim
        self.mlp = nn.Sequential(*layers)
        self.out = nn.Linear(hidden_dim, dim_proj)

    def forward(self, stacked: torch.Tensor) -> torch.Tensor:
        """
        Args:
            stacked: Tensor of shape (N, dim_proj)
            
        Returns:
            Tensor of shape (N, dim_proj)
        """
        x = self.mlp(stacked)
        return self.out(x)


class CrossModalHead(nn.Module):
    """
    Produces cross-modal coherence vector T_cross.
    
    Measures consistency between modalities.
    """

    def __init__(self, dim_proj: int, dim_t_cross: int, dropout: float):
        super().__init__()
        self.dim_proj = dim_proj
        self.dim_t_cross = dim_t_cross

        # Input: 4 embeddings (dim_proj each) + 4 presence masks
        in_dim = 4 * dim_proj + 4
        self.fc1 = nn.Linear(in_dim, 2 * dim_t_cross)
        self.fc2 = nn.Linear(2 * dim_t_cross, dim_t_cross)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        v_text: Optional[torch.Tensor],
        v_vision: Optional[torch.Tensor],
        v_code: Optional[torch.Tensor],
        v_audio: Optional[torch.Tensor],
    ) -> torch.Tensor:
        """
        Args:
            v_text: Text embedding (B, dim_proj) or None
            v_vision: Vision embedding (B, dim_proj) or None
            v_code: Code embedding (B, dim_proj) or None
            v_audio: Audio embedding (B, dim_proj) or None
            
        Returns:
            T_cross: Tensor of shape (B, dim_t_cross)
        """
        # Determine batch size
        B = None
        device = None
        for v in [v_text, v_vision, v_code, v_audio]:
            if v is not None:
                B = v.size(0)
                device = v.device
                break
        if B is None:
            raise ValueError("At least one modality must be present")

        def ensure_tensor(v: Optional[torch.Tensor]) -> Tuple[torch.Tensor, torch.Tensor]:
            """
            Returns:
                - embedding (B, dim_proj)
                - mask (B, 1) - 1 if present, 0 if absent
            """
            if v is None:
                return (
                    torch.zeros(B, self.dim_proj, device=device),
                    torch.zeros(B, 1, device=device),
                )
            if v.size(1) != self.dim_proj:
                raise ValueError(f"Embedding size {v.size(1)}, expected {self.dim_proj}")
            return v, torch.ones(B, 1, device=device)

        t, mt = ensure_tensor(v_text)
        im, mi = ensure_tensor(v_vision)
        c, mc = ensure_tensor(v_code)
        a, ma = ensure_tensor(v_audio)

        emb_concat = torch.cat([t, im, c, a], dim=1)      # (B, 4*dim_proj)
        mask_concat = torch.cat([mt, mi, mc, ma], dim=1)  # (B, 4)

        x = torch.cat([emb_concat, mask_concat], dim=1)   # (B, 4*dim_proj + 4)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x  # (B, dim_t_cross)


class TriadHead(nn.Module):
    """
    Triad prediction head: produces logits for (∆, ∞, Θ).
    """

    def __init__(self, dim_in: int, dropout: float):
        super().__init__()
        self.fc1 = nn.Linear(dim_in, dim_in)
        self.fc2 = nn.Linear(dim_in, 3)
        self.dropout = nn.Dropout(dropout)

    def forward(self, v: torch.Tensor) -> torch.Tensor:
        """
        Args:
            v: Semantic embedding (B, dim_in)
            
        Returns:
            Triad logits (B, 3)
        """
        x = F.relu(self.fc1(v))
        x = self.dropout(x)
        return self.fc2(x)


# ============================================================================
# 5. COMPLETE MODEL: NumTriadMultimodalV4
# ============================================================================

class NumTriadMultimodalV4(nn.Module):
    """
    Complete multimodal model combining all components.
    
    Pipeline:
    1. Encode each modality (text, vision, code, audio)
    2. Project to common space (dim_proj)
    3. Fuse -> v_semantic
    4. TriadHead -> triad probabilities
    5. CrossModalHead -> T_cross
    6. Concatenate: [v_semantic | triad_probs | T_cross]
    
    Final embedding shape: (B, dim_proj + 3 + dim_t_cross)
    """

    def __init__(self, config: MultimodalV4Config):
        super().__init__()
        self.cfg = config

        # Base encoders (replace with real models in production)
        self.text_encoder = SimpleTextEncoder(dim_out=config.dim_text_in)
        self.code_encoder = SimpleCodeEncoder(dim_out=config.dim_code_in)
        self.vision_encoder = SimpleVisionEncoder(dim_out=config.dim_vision_in)
        self.audio_encoder = SimpleAudioEncoder(dim_out=config.dim_audio_in)

        # Projectors to common space
        self.text_proj = ModalityProjector(config.dim_text_in, config.dim_proj, config.dropout)
        self.code_proj = ModalityProjector(config.dim_code_in, config.dim_proj, config.dropout)
        self.vision_proj = ModalityProjector(config.dim_vision_in, config.dim_proj, config.dropout)
        self.audio_proj = ModalityProjector(config.dim_audio_in, config.dim_proj, config.dropout)

        # Fusion and heads
        self.fusion = FusionEncoder(
            dim_proj=config.dim_proj,
            hidden_dim=config.fusion_hidden_dim,
            num_layers=config.fusion_num_layers,
            dropout=config.dropout,
        )
        self.triad_head = TriadHead(config.dim_proj, dropout=config.dropout)
        self.cross_head = CrossModalHead(
            dim_proj=config.dim_proj,
            dim_t_cross=config.dim_t_cross,
            dropout=config.dropout,
        )

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    def _encode_text(self, texts: Optional[List[str]]) -> Optional[torch.Tensor]:
        """Encode text modality."""
        if texts is None or len(texts) == 0:
            return None
        return self.text_proj(self.text_encoder(texts))

    def _encode_code(self, codes: Optional[List[str]]) -> Optional[torch.Tensor]:
        """Encode code modality."""
        if codes is None or len(codes) == 0:
            return None
        return self.code_proj(self.code_encoder(codes))

    def _encode_vision(self, images: Optional[torch.Tensor]) -> Optional[torch.Tensor]:
        """Encode vision modality."""
        if images is None:
            return None
        return self.vision_proj(self.vision_encoder(images))

    def _encode_audio(self, audio_feats: Optional[torch.Tensor]) -> Optional[torch.Tensor]:
        """Encode audio modality."""
        if audio_feats is None:
            return None
        return self.audio_proj(self.audio_encoder(audio_feats))

    # -----------------------------------------------------------------------
    # Main API
    # -----------------------------------------------------------------------

    def forward(
        self,
        texts: Optional[List[str]] = None,
        images: Optional[torch.Tensor] = None,
        codes: Optional[List[str]] = None,
        audio_feats: Optional[torch.Tensor] = None,
        return_triad_objects: bool = False,
    ):
        """
        Main forward pass.
        
        Args:
            texts: List of text strings or None
            images: Tensor (B, 3, H, W) or None
            codes: List of code strings or None
            audio_feats: Tensor (B, 128) or None
            return_triad_objects: If True, return Triad objects
            
        Returns:
            - embedding: Tensor (B, dim_proj + 3 + dim_t_cross)
            - triad_probs: Tensor (B, 3)
            - triad_objs: List[Triad] (if return_triad_objects=True)
        """
        device = torch.device(self.cfg.device)
        self.to(device)

        # 1. Encode each modality
        v_text = self._encode_text(texts)
        v_code = self._encode_code(codes)
        v_vision = self._encode_vision(images)
        v_audio = self._encode_audio(audio_feats)

        # Determine batch size
        B = None
        for v in [v_text, v_code, v_vision, v_audio]:
            if v is not None:
                B = v.size(0)
                break
        if B is None:
            raise ValueError("NumTriadMultimodalV4: at least one modality must be provided")

        # 2. Fuse modalities -> v_semantic
        sum_vec = torch.zeros(B, self.cfg.dim_proj, device=device)
        count = 0
        for v in [v_text, v_code, v_vision, v_audio]:
            if v is not None:
                sum_vec = sum_vec + v
                count += 1
        v_mean = sum_vec / max(count, 1)
        v_semantic = self.fusion(v_mean)  # (B, dim_proj)

        # 3. Predict triad
        triad_logits = self.triad_head(v_semantic)       # (B, 3)
        triad_probs = F.softmax(triad_logits, dim=-1)    # (B, 3)

        # 4. Cross-modal coherence
        T_cross = self.cross_head(v_text, v_vision, v_code, v_audio)  # (B, dim_t_cross)

        # 5. Final embedding concatenation
        embedding = torch.cat([v_semantic, triad_probs, T_cross], dim=-1)
        # Shape: (B, dim_proj + 3 + dim_t_cross)

        triad_objs = None
        if return_triad_objects:
            triad_objs = [
                Triad.from_logits(triad_logits[i]) for i in range(B)
            ]

        if return_triad_objects:
            return embedding, triad_probs, triad_objs
        return embedding, triad_probs

    def get_embedding_dim(self) -> int:
        """Returns the total embedding dimension."""
        return self.cfg.dim_proj + 3 + self.cfg.dim_t_cross


# ============================================================================
# 6. QUICK EXAMPLE
# ============================================================================

if __name__ == "__main__":
    print("🚀 NumTriad Multimodal V4 Example\n")
    
    cfg = MultimodalV4Config(
        dim_text_in=256,
        dim_vision_in=256,
        dim_code_in=256,
        dim_audio_in=128,
        dim_proj=192,
        dim_t_cross=32,
        fusion_hidden_dim=256,
        fusion_num_layers=2,
        dropout=0.1,
        device="cpu",
    )
    
    print(f"📊 Config: {cfg}\n")
    
    model = NumTriadMultimodalV4(cfg)
    print(f"✅ Model created\n")

    # Example data
    texts = [
        "Théorie générale de l'intelligence ∆∞Ο",
        "Exemple concret: déployer une API FastAPI"
    ]
    codes = [
        "def add(a,b): return a+b",
        "docker run -p 8000:8000 api"
    ]
    images = torch.randn(2, 3, 64, 64)       # Fake images
    audio_feats = torch.randn(2, 128)        # Fake audio MFCC

    # Forward pass
    emb, triad_probs, triads = model(
        texts=texts,
        images=images,
        codes=codes,
        audio_feats=audio_feats,
        return_triad_objects=True,
    )

    print(f"📈 Results:")
    print(f"  Embedding shape: {emb.shape}")
    print(f"  Total embedding dim: {model.get_embedding_dim()}")
    print(f"  Triad probs shape: {triad_probs.shape}")
    print(f"  Triad objects: {triads}")
    print(f"\n✅ Example completed!")
