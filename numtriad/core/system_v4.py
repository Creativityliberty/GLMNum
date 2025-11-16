#!/usr/bin/env python3
"""
NumTriad System V4 - Complete Integration
==========================================

Integration of 4 pillars:

- Pillar A: NumTriadMultimodalV4 (multimodal embedding ∆∞Θ + T_cross)
- Pillar B: VisionTransformationEngine (VTE, G_vis, T_vis)
- Pillar C: DeepTriadTransformer (sequence triad-aware)
- Pillar D: NumTriadRAGIndexV4 (triad-aware RAG)

High-level facade providing:
  - encode_sample(...)      -> embedding + triad
  - add_document(...)       -> triad-aware indexing
  - query_documents(...)    -> controlled search (abstract/concrete/balanced)
  - add_image_to_graph(...) -> VTE integration
  - visual_path(...)        -> visual transformation path

Usage:
    from numtriad.core.system_v4 import NumTriadSystemV4, NumTriadSystemConfig
    
    cfg = NumTriadSystemConfig(...)
    system = NumTriadSystemV4(cfg)
    
    system.add_document("doc1", texts=["..."])
    results = system.query_documents("query", mode="abstract", k=5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Literal, Tuple
import logging

import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    F = None

# Configure logging
logger = logging.getLogger(__name__)

# Type definitions
TriadMode = Literal["auto", "abstract", "concrete", "balanced"]


# ============================================================================
# IMPORTS - Internal NumTriad modules
# ============================================================================

try:
    from numtriad.multimodal_v4 import NumTriadMultimodalV4, MultimodalV4Config
    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False
    logger.warning("NumTriadMultimodalV4 not available - some features disabled")

try:
    from numtriad.vision.vte import (
        VisionTransformationEngine,
        VisualNode,
        VisualTransform,
    )
    VTE_AVAILABLE = True
except ImportError:
    VTE_AVAILABLE = False
    logger.warning("VisionTransformationEngine not available - vision features disabled")


# ============================================================================
# PILLAR C: DeepTriadTransformer
# ============================================================================

@dataclass
class DeepTriadTransformerConfig:
    """Configuration for DeepTriadTransformer"""
    dim_in: int = 256
    dim_model: int = 256
    num_layers: int = 2
    num_heads: int = 4
    dim_ff: int = 512
    dropout: float = 0.1
    device: str = "cpu"


class DeepTriadTransformer(nn.Module if TORCH_AVAILABLE else object):
    """
    Pillar C: Sequence-level triad-aware transformer.
    
    Input: sequences of vectors (e.g., embeddings of sentences/chunks)
    Outputs:
      - logits_global (B,3) -> global document triad
      - logits_steps (B,L,3) -> triad per step (optional)
    """

    def __init__(self, cfg: DeepTriadTransformerConfig):
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is required for DeepTriadTransformer")
        
        super().__init__()
        self.cfg = cfg

        self.in_proj = nn.Linear(cfg.dim_in, cfg.dim_model)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=cfg.dim_model,
            nhead=cfg.num_heads,
            dim_feedforward=cfg.dim_ff,
            dropout=cfg.dropout,
            activation="gelu",
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=cfg.num_layers,
        )

        self.global_head = nn.Sequential(
            nn.Linear(cfg.dim_model, cfg.dim_model),
            nn.ReLU(),
            nn.Dropout(cfg.dropout),
            nn.Linear(cfg.dim_model, 3),
        )

        self.steps_head = nn.Sequential(
            nn.Linear(cfg.dim_model, cfg.dim_model),
            nn.ReLU(),
            nn.Dropout(cfg.dropout),
            nn.Linear(cfg.dim_model, 3),
        )

        self.to(torch.device(cfg.device))

    def forward(
        self,
        x: torch.Tensor,
        padding_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x: (B,L,dim_in) - input sequence
            padding_mask: (B,L) bool, True = token to ignore
            
        Returns:
            logits_global: (B,3)
            logits_steps: (B,L,3)
        """
        h = self.in_proj(x)  # (B,L,dim_model)
        h_enc = self.encoder(h, src_key_padding_mask=padding_mask)  # (B,L,dim_model)

        # Global pooling
        if padding_mask is not None:
            mask = (~padding_mask).float().unsqueeze(-1)  # (B,L,1)
            h_masked = h_enc * mask
            denom = mask.sum(dim=1).clamp_min(1.0)
            h_global = (h_masked.sum(dim=1) / denom)  # (B,dim_model)
        else:
            h_global = h_enc.mean(dim=1)  # (B,dim_model)

        logits_global = self.global_head(h_global)         # (B,3)
        logits_steps = self.steps_head(h_enc)              # (B,L,3)
        return logits_global, logits_steps


# ============================================================================
# PILLAR D: NumTriadRAGIndexV4
# ============================================================================

@dataclass
class IndexedDoc:
    """Document indexed in RAG"""
    doc_id: str
    embedding: np.ndarray   # (D,)
    triad: np.ndarray       # (3,) - ∆, ∞, Θ
    metadata: Dict[str, Any] = field(default_factory=dict)


class NumTriadRAGIndexV4:
    """
    Pillar D: Triad-aware RAG index.
    
    - Stores NumTriad embeddings (E = [v_sem | triad | T_cross])
    - Keeps explicit copy of triad (3 dims)
    - Enables triad-aware queries:
        * mode "abstract"    -> favor high ∞, low Θ
        * mode "concrete"    -> favor high Θ
        * mode "balanced"    -> neutral mix
        * mode "auto"        -> use query triad
    """

    def __init__(self):
        self.docs: List[IndexedDoc] = []
        self.dim: Optional[int] = None

    @staticmethod
    def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity"""
        num = float(np.dot(a, b))
        den = float(np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)
        return num / den

    def add_document(self, doc: IndexedDoc) -> None:
        """Add document to index"""
        if self.dim is None:
            self.dim = doc.embedding.shape[0]
        else:
            if doc.embedding.shape[0] != self.dim:
                raise ValueError(
                    f"Embedding dimension mismatch: {doc.embedding.shape[0]} != {self.dim}"
                )
        self.docs.append(doc)
        logger.debug(f"Added document {doc.doc_id} to RAG index")

    def _triad_target_from_mode(
        self,
        mode: TriadMode,
        query_triad: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Get target triad distribution based on mode"""
        if mode == "auto":
            if query_triad is None:
                return np.asarray([1/3, 1/3, 1/3], dtype="float32")
            return query_triad.astype("float32")

        if mode == "abstract":
            # More weight on ∞ (infinity), less on Θ (theta)
            return np.asarray([0.2, 0.6, 0.2], dtype="float32")  # ∆,∞,Θ
        if mode == "concrete":
            # More weight on Θ
            return np.asarray([0.1, 0.2, 0.7], dtype="float32")
        if mode == "balanced":
            return np.asarray([1/3, 1/3, 1/3], dtype="float32")

        return np.asarray([1/3, 1/3, 1/3], dtype="float32")

    def _triad_alignment_score(
        self,
        doc_triad: np.ndarray,
        target_triad: np.ndarray,
    ) -> float:
        """Score alignment between doc triad and target triad"""
        d = float(np.sum(np.abs(doc_triad - target_triad)))
        # max possible = 2 (when [1,0,0] vs [0,0,1])
        return 1.0 - d / 2.0

    def query(
        self,
        query_embedding: np.ndarray,
        query_triad: Optional[np.ndarray] = None,
        k: int = 5,
        mode: TriadMode = "auto",
        alpha_semantic: float = 0.7,
        alpha_triad: float = 0.3,
    ) -> List[Tuple[IndexedDoc, float]]:
        """
        Query with triad-aware scoring.
        
        score = alpha_semantic * cos_sim + alpha_triad * triad_alignment
        """
        if self.dim is None or len(self.docs) == 0:
            logger.warning("RAG index is empty")
            return []

        query_embedding = query_embedding.astype("float32")
        target_triad = self._triad_target_from_mode(mode, query_triad)

        scored: List[Tuple[IndexedDoc, float]] = []
        for doc in self.docs:
            cos_sim = self._cosine_sim(query_embedding, doc.embedding)
            triad_score = self._triad_alignment_score(doc.triad, target_triad)
            score = alpha_semantic * cos_sim + alpha_triad * triad_score
            scored.append((doc, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]


# ============================================================================
# SYSTEM CONFIG
# ============================================================================

@dataclass
class NumTriadSystemConfig:
    """Global configuration for NumTriadSystemV4"""
    multimodal: Optional[MultimodalV4Config] = None
    deeptriad: Optional[DeepTriadTransformerConfig] = None
    device: str = "cpu"


# ============================================================================
# MAIN SYSTEM: NumTriadSystemV4
# ============================================================================

class NumTriadSystemV4:
    """
    Unified facade for 4 pillars:
    
      - embedder  : NumTriadMultimodalV4 (Pillar A)
      - vte       : VisionTransformationEngine (Pillar B)
      - deeptriad : DeepTriadTransformer (Pillar C)
      - rag       : NumTriadRAGIndexV4 (Pillar D)
    
    Main methods:
      - encode_sample(...)      -> multimodal embedding + triad
      - add_document(...)       -> triad-aware indexing
      - query_documents(...)    -> triad-aware search
      - add_image_to_graph(...) -> visual integration
      - visual_path(...)        -> visual transformation path
      - triad_sequence_analysis(...) -> sequence-level triad analysis
    """

    def __init__(self, cfg: NumTriadSystemConfig):
        self.cfg = cfg
        self.device = torch.device(cfg.device) if TORCH_AVAILABLE else None

        # Pillar A: Multimodal Embedder
        self.embedder = None
        if MULTIMODAL_AVAILABLE and cfg.multimodal:
            self.embedder = NumTriadMultimodalV4(cfg.multimodal)
            if self.device:
                self.embedder.to(self.device)
            logger.info("✅ Pillar A (NumTriadMultimodalV4) initialized")
        else:
            logger.warning("⚠️ Pillar A (NumTriadMultimodalV4) not available")

        # Pillar B: Vision Transformation Engine
        self.vte = None
        if VTE_AVAILABLE and cfg.multimodal:
            self.vte = VisionTransformationEngine(
                dim_embedding=cfg.multimodal.dim_proj,
                use_triad_head=True,
                device=cfg.device,
            )
            logger.info("✅ Pillar B (VisionTransformationEngine) initialized")
        else:
            logger.warning("⚠️ Pillar B (VisionTransformationEngine) not available")

        # Pillar C: DeepTriad Transformer
        self.deeptriad = None
        if TORCH_AVAILABLE and cfg.deeptriad:
            self.deeptriad = DeepTriadTransformer(cfg.deeptriad)
            logger.info("✅ Pillar C (DeepTriadTransformer) initialized")
        else:
            logger.warning("⚠️ Pillar C (DeepTriadTransformer) not available")

        # Pillar D: RAG Index
        self.rag_index = NumTriadRAGIndexV4()
        logger.info("✅ Pillar D (NumTriadRAGIndexV4) initialized")

    # =====================================================================
    # PILLAR A: Multimodal Encoding
    # =====================================================================

    def encode_sample(
        self,
        texts: Optional[List[str]] = None,
        images: Optional[torch.Tensor] = None,
        codes: Optional[List[str]] = None,
        audio_feats: Optional[torch.Tensor] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        High-level multimodal encoding.
        
        Returns:
          - embedding_np : (B, D_total)
          - triad_np     : (B, 3) - ∆, ∞, Θ probabilities
        """
        if not self.embedder:
            raise RuntimeError("Embedder (Pillar A) not initialized")

        self.embedder.eval()
        with torch.no_grad():
            emb, triad_probs = self.embedder(
                texts=texts,
                images=images,
                codes=codes,
                audio_feats=audio_feats,
                return_triad_objects=False,
            )
        emb_np = emb.cpu().numpy().astype("float32")
        triad_np = triad_probs.cpu().numpy().astype("float32")
        return emb_np, triad_np

    # =====================================================================
    # PILLAR D: RAG Indexing & Querying
    # =====================================================================

    def add_document(
        self,
        doc_id: str,
        texts: Optional[List[str]] = None,
        images: Optional[torch.Tensor] = None,
        codes: Optional[List[str]] = None,
        audio_feats: Optional[torch.Tensor] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Index a document (or chunk) in triad-aware RAG.
        """
        if metadata is None:
            metadata = {}

        emb_np, triad_np = self.encode_sample(
            texts=texts,
            images=images,
            codes=codes,
            audio_feats=audio_feats,
        )
        # Assume B=1 (single chunk)
        e = emb_np[0]
        t = triad_np[0]
        doc = IndexedDoc(
            doc_id=doc_id,
            embedding=e,
            triad=t,
            metadata=metadata,
        )
        self.rag_index.add_document(doc)

    def query_documents(
        self,
        query_text: str,
        mode: TriadMode = "auto",
        k: int = 5,
    ) -> List[Tuple[IndexedDoc, float]]:
        """
        Simple text query with triad-aware RAG.
        
        - Encodes query text
        - Uses query triad if mode="auto"
        - Otherwise applies specified triad mode
        """
        emb_np, triad_np = self.encode_sample(texts=[query_text])
        e = emb_np[0]
        t = triad_np[0]
        return self.rag_index.query(
            query_embedding=e,
            query_triad=t,
            k=k,
            mode=mode,
        )

    # =====================================================================
    # PILLAR B: Vision Transformation Engine
    # =====================================================================

    def add_image_to_graph(
        self,
        node_id: str,
        image: torch.Tensor,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[VisualNode]:
        """
        Add image to visual graph G_vis (VTE).
        """
        if not self.vte:
            raise RuntimeError("VTE (Pillar B) not initialized")

        return self.vte.add_image(
            node_id=node_id,
            image=image,
            metadata=metadata or {}
        )

    def connect_vision_graph_knn(
        self,
        k: int = 5,
        use_triad_weighting: bool = True,
        kind: str = "knn",
    ) -> None:
        """
        KNN visual connection to build morphisms.
        """
        if not self.vte:
            raise RuntimeError("VTE (Pillar B) not initialized")

        self.vte.connect_knn(
            k=k,
            use_triad_weighting=use_triad_weighting,
            kind=kind
        )

    def visual_path(
        self,
        source_id: str,
        target_id: str,
    ) -> Tuple[List[str], np.ndarray]:
        """
        Visual transformation path + aggregated T_vis.
        """
        if not self.vte:
            raise RuntimeError("VTE (Pillar B) not initialized")

        return self.vte.shortest_transform_path(source_id, target_id)

    # =====================================================================
    # PILLAR C: Sequence-level Triad Analysis
    # =====================================================================

    def triad_sequence_analysis(
        self,
        embeddings_seq: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Triad analysis on sequence (e.g., multiple chunks).
        
        Args:
            embeddings_seq: (L, dim_in) - sequence of embeddings
            
        Returns:
            - triad_global: (3,) - global triad
            - triad_steps : (L, 3) - per-step triads
        """
        if not self.deeptriad:
            raise RuntimeError("DeepTriad (Pillar C) not initialized")

        x = torch.tensor(
            embeddings_seq,
            dtype=torch.float32,
            device=self.device
        ).unsqueeze(0)  # (1, L, D)

        padding_mask = None
        self.deeptriad.eval()
        with torch.no_grad():
            logits_global, logits_steps = self.deeptriad(x, padding_mask=padding_mask)
            probs_global = F.softmax(logits_global, dim=-1)[0].cpu().numpy().astype("float32")
            probs_steps = F.softmax(logits_steps, dim=-1)[0].cpu().numpy().astype("float32")

        return probs_global, probs_steps

    # =====================================================================
    # System Status
    # =====================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "pillar_a_multimodal": MULTIMODAL_AVAILABLE and self.embedder is not None,
            "pillar_b_vte": VTE_AVAILABLE and self.vte is not None,
            "pillar_c_deeptriad": TORCH_AVAILABLE and self.deeptriad is not None,
            "pillar_d_rag": True,
            "rag_documents": len(self.rag_index.docs),
            "device": str(self.device) if self.device else "cpu",
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Quick config
    if MULTIMODAL_AVAILABLE:
        mm_cfg = MultimodalV4Config(
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
    else:
        mm_cfg = None

    if TORCH_AVAILABLE:
        dt_cfg = DeepTriadTransformerConfig(
            dim_in=192,
            dim_model=192,
            num_layers=2,
            num_heads=4,
            dim_ff=384,
            dropout=0.1,
            device="cpu",
        )
    else:
        dt_cfg = None

    sys_cfg = NumTriadSystemConfig(
        multimodal=mm_cfg,
        deeptriad=dt_cfg,
        device="cpu",
    )

    system = NumTriadSystemV4(sys_cfg)
    print("\n✅ NumTriad System V4 initialized")
    print("Status:", system.get_status())

    if MULTIMODAL_AVAILABLE:
        # 1) Index 2 documents
        print("\n[1] Indexing documents...")
        system.add_document(
            doc_id="doc_theory",
            texts=["General intelligence, ∆∞Θ, transformation of abstractions."],
            metadata={"type": "theory"},
        )
        system.add_document(
            doc_id="doc_concrete",
            texts=["Concrete tutorial: deploy FastAPI on Ubuntu server."],
            metadata={"type": "howto"},
        )

        # 2) Query in "abstract" mode
        print("\n[2] Querying (abstract mode)...")
        results = system.query_documents(
            query_text="explain general theory of intelligence",
            mode="abstract",
            k=2,
        )
        for doc, score in results:
            print(f"  {doc.doc_id}: score={score:.3f}, triad={doc.triad}, meta={doc.metadata}")

        # 3) Query in "concrete" mode
        print("\n[3] Querying (concrete mode)...")
        results = system.query_documents(
            query_text="how to deploy on server",
            mode="concrete",
            k=2,
        )
        for doc, score in results:
            print(f"  {doc.doc_id}: score={score:.3f}, triad={doc.triad}, meta={doc.metadata}")

    if VTE_AVAILABLE and TORCH_AVAILABLE:
        # 4) Vision: 2 images + path
        print("\n[4] Vision transformation...")
        imgs = torch.randn(2, 3, 64, 64)
        system.add_image_to_graph("img_A", imgs[0], metadata={"label": "abstract"})
        system.add_image_to_graph("img_B", imgs[1], metadata={"label": "concrete"})
        system.connect_vision_graph_knn(k=1)
        path, T = system.visual_path("img_A", "img_B")
        print(f"  Path A->B: {path}")
        print(f"  T_vis shape: {T.shape if isinstance(T, np.ndarray) else 'N/A'}")

    print("\n✅ Example complete!")
