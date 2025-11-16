# numtriad/system_integration.py
"""
Complete System Integration
============================

Unifies all components:
- GLM v3.0 (Symbolic Engine)
- NumTriad (3 Pillars)
- DeepTriad (Transformer)
- NumTriad V3 + RAG
- Gemini Wrapper
- Pillar A (Multimodal V4)

Single entry point for the entire system.

Author: GLM Research Team
Date: 2024-11-16
"""

from typing import Optional, Dict, Any, List
import torch

from .config import NumTriadConfig
from .encoders.numtriad_v3 import NumTriadV3Config, NumTriadEmbeddingV3
from .rag.deeptriad_rag import DeepTriadRAGIndex
from .llm.gemini_triad_wrapper import GeminiTriadWrapper, GeminiConfig
from .multimodal_v4 import NumTriadMultimodalV4, MultimodalV4Config
from .vision.vte import VisionTransformationEngine


class UnifiedGLMSystem:
    """
    Complete unified system combining all components.
    
    Provides single API for:
    - Symbolic transformation (GLM v3.0)
    - Triad-aware embeddings (NumTriad)
    - Sequence prediction (DeepTriad)
    - Advanced retrieval (V3 + RAG)
    - LLM orchestration (Gemini)
    - Multimodal encoding (Pillar A)
    """

    def __init__(
        self,
        base_config: Optional[NumTriadConfig] = None,
        v3_config: Optional[NumTriadV3Config] = None,
        gemini_config: Optional[GeminiConfig] = None,
        multimodal_config: Optional[MultimodalV4Config] = None,
        gemini_client: Optional[Any] = None,
    ):
        """
        Initialize the unified system.
        
        Args:
            base_config: NumTriad base configuration
            v3_config: NumTriad V3 configuration
            gemini_config: Gemini LLM configuration
            multimodal_config: Multimodal V4 configuration
            gemini_client: Gemini API client (optional)
        """
        # Configurations
        self.base_config = base_config or NumTriadConfig(device="cpu")
        self.v3_config = v3_config or NumTriadV3Config(
            deeptriad_ckpt="checkpoints/deeptriad_transformer_v1.pt",
            max_len=16,
        )
        self.gemini_config = gemini_config or GeminiConfig()
        self.multimodal_config = multimodal_config or MultimodalV4Config()

        # Components
        self.rag_index = DeepTriadRAGIndex(
            base_config=self.base_config,
            v3_config=self.v3_config,
            retrieval_mode="triad_weighted",
            triad_weight=0.3,
        )

        self.gemini_wrapper = GeminiTriadWrapper(
            rag_index=self.rag_index,
            gemini_client=gemini_client,
            gemini_cfg=self.gemini_config,
        )

        self.multimodal_model = NumTriadMultimodalV4(self.multimodal_config)

        # Vision Transformation Engine (Pillar B)
        try:
            self.vte = VisionTransformationEngine(
                dim_embedding=256,
                use_triad_head=True,
                device=self.base_config.device,
            )
        except Exception as e:
            print(f"⚠️ VTE initialization failed: {e}")
            self.vte = None

        print("✅ Unified GLM System initialized")

    # =========================================================================
    # DOCUMENT INDEXING
    # =========================================================================

    def index_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """
        Index documents for retrieval.
        
        Args:
            texts: List of document texts
            metadatas: Optional metadata per document
            ids: Optional document IDs
        """
        self.rag_index.add_documents(texts, metadatas=metadatas, ids=ids)
        print(f"✅ Indexed {len(texts)} documents")

    # =========================================================================
    # RETRIEVAL
    # =========================================================================

    def search(
        self,
        query: str,
        k: int = 5,
        triad_target: str = "auto",
    ) -> List[Dict[str, Any]]:
        """
        Search documents with triad-aware ranking.
        
        Args:
            query: Search query
            k: Number of results
            triad_target: "auto", "abstract", "concrete", or "balanced"
            
        Returns:
            List of ranked documents with scores
        """
        results = self.rag_index.search(
            query=query,
            k=k,
            triad_target=triad_target,
        )
        
        return [
            {
                "id": doc.doc_id,
                "text": doc.text,
                "score": score,
                "triad": {
                    "delta": doc.triad.delta,
                    "infinity": doc.triad.infinity,
                    "theta": doc.triad.theta,
                },
                "meta": doc.meta,
            }
            for doc, score in results
        ]

    # =========================================================================
    # QA WITH GEMINI
    # =========================================================================

    def answer(
        self,
        query: str,
        k: int = 5,
        triad_target_mode: str = "auto",
    ) -> Dict[str, Any]:
        """
        Generate answer using Gemini with triad-aware context.
        
        Args:
            query: User question
            k: Number of context documents
            triad_target_mode: Triad control mode
            
        Returns:
            Complete answer with metadata
        """
        return self.gemini_wrapper.answer(
            query=query,
            k=k,
            triad_target_mode=triad_target_mode,
        )

    # =========================================================================
    # MULTIMODAL ENCODING
    # =========================================================================

    def encode_multimodal(
        self,
        texts: Optional[List[str]] = None,
        images: Optional[torch.Tensor] = None,
        codes: Optional[List[str]] = None,
        audio_feats: Optional[torch.Tensor] = None,
        return_triads: bool = False,
    ) -> Dict[str, Any]:
        """
        Encode multimodal content.
        
        Args:
            texts: List of text strings
            images: Tensor of images (B, 3, H, W)
            codes: List of code strings
            audio_feats: Tensor of audio features (B, 128)
            return_triads: If True, return Triad objects
            
        Returns:
            Embeddings and triads
        """
        if return_triads:
            embedding, triad_probs, triads = self.multimodal_model(
                texts=texts,
                images=images,
                codes=codes,
                audio_feats=audio_feats,
                return_triad_objects=True,
            )
            return {
                "embedding": embedding,
                "triad_probs": triad_probs,
                "triads": triads,
            }
        else:
            embedding, triad_probs = self.multimodal_model(
                texts=texts,
                images=images,
                codes=codes,
                audio_feats=audio_feats,
                return_triad_objects=False,
            )
            return {
                "embedding": embedding,
                "triad_probs": triad_probs,
            }

    # =========================================================================
    # VISION TRANSFORMATION ENGINE (PILLAR B)
    # =========================================================================

    def add_visual_images(
        self,
        node_ids: List[str],
        images: torch.Tensor,
        metadata_list: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Add images to the visual transformation graph.
        
        Args:
            node_ids: List of image identifiers
            images: Tensor (B, 3, H, W)
            metadata_list: Optional metadata per image
        """
        if not self.vte:
            raise RuntimeError("VTE not available")
        
        self.vte.add_images_batch(node_ids, images, metadata_list)
        print(f"✅ Added {len(node_ids)} images to visual graph")

    def connect_visual_graph(
        self,
        k: int = 5,
        use_triad_weighting: bool = True,
    ) -> None:
        """
        Build visual transformation graph with KNN connectivity.
        
        Args:
            k: Number of nearest neighbors
            use_triad_weighting: Weight by triad distance
        """
        if not self.vte:
            raise RuntimeError("VTE not available")
        
        self.vte.connect_knn(k=k, use_triad_weighting=use_triad_weighting)
        print(f"✅ Visual graph connected with k={k}")

    def find_visual_transform_path(
        self,
        source_id: str,
        target_id: str,
    ) -> Dict[str, Any]:
        """
        Find transformation path between two images.
        
        Args:
            source_id: Source image ID
            target_id: Target image ID
            
        Returns:
            Dict with path and T_vis vector
        """
        if not self.vte:
            raise RuntimeError("VTE not available")
        
        path, T_vis = self.vte.shortest_transform_path(source_id, target_id)
        
        return {
            "path": path,
            "T_vis": {
                "d_emb": float(T_vis[0]),
                "d_triad": float(T_vis[1]),
                "d_scale": float(T_vis[2]),
                "d_position": float(T_vis[3]),
            },
            "num_steps": len(path) - 1,
        }

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        stats = {
            "rag_index": self.rag_index.get_stats(),
            "gemini_wrapper": self.gemini_wrapper.get_stats(),
            "multimodal_model": {
                "embedding_dim": self.multimodal_model.get_embedding_dim(),
                "config": {
                    "dim_proj": self.multimodal_config.dim_proj,
                    "dim_t_cross": self.multimodal_config.dim_t_cross,
                },
            },
        }
        
        if self.vte:
            stats["vte"] = {
                "num_nodes": len(list(self.vte.graph.all_nodes())),
                "num_edges": self.vte.graph.G.number_of_edges(),
                "status": "ready",
            }
        
        return stats


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_system_instance: Optional[UnifiedGLMSystem] = None


def get_unified_system(
    base_config: Optional[NumTriadConfig] = None,
    v3_config: Optional[NumTriadV3Config] = None,
    gemini_config: Optional[GeminiConfig] = None,
    multimodal_config: Optional[MultimodalV4Config] = None,
    gemini_client: Optional[Any] = None,
) -> UnifiedGLMSystem:
    """
    Get or create the unified system singleton.
    
    Args:
        base_config: NumTriad base configuration
        v3_config: NumTriad V3 configuration
        gemini_config: Gemini LLM configuration
        multimodal_config: Multimodal V4 configuration
        gemini_client: Gemini API client (optional)
        
    Returns:
        UnifiedGLMSystem instance
    """
    global _system_instance
    
    if _system_instance is None:
        _system_instance = UnifiedGLMSystem(
            base_config=base_config,
            v3_config=v3_config,
            gemini_config=gemini_config,
            multimodal_config=multimodal_config,
            gemini_client=gemini_client,
        )
    
    return _system_instance


# ============================================================================
# QUICK API
# ============================================================================

def index_documents(
    texts: List[str],
    metadatas: Optional[List[Dict[str, Any]]] = None,
    ids: Optional[List[str]] = None,
) -> None:
    """Quick API: Index documents."""
    system = get_unified_system()
    system.index_documents(texts, metadatas=metadatas, ids=ids)


def search(
    query: str,
    k: int = 5,
    triad_target: str = "auto",
) -> List[Dict[str, Any]]:
    """Quick API: Search documents."""
    system = get_unified_system()
    return system.search(query, k=k, triad_target=triad_target)


def answer(
    query: str,
    k: int = 5,
    triad_target_mode: str = "auto",
) -> Dict[str, Any]:
    """Quick API: Generate answer with Gemini."""
    system = get_unified_system()
    return system.answer(query, k=k, triad_target_mode=triad_target_mode)


def encode_multimodal(
    texts: Optional[List[str]] = None,
    images: Optional[torch.Tensor] = None,
    codes: Optional[List[str]] = None,
    audio_feats: Optional[torch.Tensor] = None,
    return_triads: bool = False,
) -> Dict[str, Any]:
    """Quick API: Encode multimodal content."""
    system = get_unified_system()
    return system.encode_multimodal(
        texts=texts,
        images=images,
        codes=codes,
        audio_feats=audio_feats,
        return_triads=return_triads,
    )
