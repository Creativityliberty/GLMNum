"""
Unified Encoding API
====================

One function to rule them all: encode_anything()

Automatically detects content type and uses best encoding system.
"""

import logging
from typing import Union, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Import unified system
try:
    from core.unified_system import UnifiedGLM, UnifiedEmbedding, ContentType
    UNIFIED_AVAILABLE = True
except ImportError:
    UNIFIED_AVAILABLE = False


# ============================================================================
# GLOBAL SYSTEM INSTANCE
# ============================================================================

_global_glm: Optional[UnifiedGLM] = None


def get_glm() -> UnifiedGLM:
    """Get or create global GLM instance"""
    global _global_glm
    if _global_glm is None:
        from core.unified_system import create_unified_glm
        _global_glm = create_unified_glm(device="cpu")
    return _global_glm


# ============================================================================
# UNIFIED ENCODING API
# ============================================================================

def encode_anything(
    content: Union[str, bytes],
    domain: str = "auto",
    include_all: bool = True
) -> UnifiedEmbedding:
    """
    Encode ANY content type with all available systems
    
    This is the main entry point for encoding. It automatically:
    1. Detects content type (text, code, image, audio)
    2. Encodes with GLM symbolic engine
    3. Encodes with NumTriad multimodal system
    4. Fuses all representations
    
    Args:
        content: Text, code, image, or audio data
        domain: "auto", "text", "code", "image", "geometry"
        include_all: Include all encoding systems
    
    Returns:
        UnifiedEmbedding with all representations
    
    Examples:
        >>> # Encode text
        >>> emb = encode_anything("Hello world")
        >>> print(emb.fused_embedding.shape)
        
        >>> # Encode code
        >>> code = "def hello(): print('hi')"
        >>> emb = encode_anything(code, domain="code")
        
        >>> # Encode with specific domain
        >>> emb = encode_anything("content", domain="text")
    """
    glm = get_glm()
    return glm.encode_anything(content, domain=domain, include_glm=include_all, include_numtriad=include_all)


def encode_text(text: str, domain: str = "text") -> UnifiedEmbedding:
    """Encode text content"""
    return encode_anything(text, domain=domain)


def encode_code(code: str) -> UnifiedEmbedding:
    """Encode code content"""
    return encode_anything(code, domain="code")


def encode_image(image_data: bytes) -> UnifiedEmbedding:
    """Encode image content"""
    return encode_anything(image_data, domain="image")


def get_embedding_vector(content: Union[str, bytes]) -> np.ndarray:
    """Get just the embedding vector (no metadata)"""
    emb = encode_anything(content)
    return emb.fused_embedding if emb.fused_embedding is not None else np.array([])


def get_triad(content: Union[str, bytes]) -> Dict[str, float]:
    """Get triad scores (∆∞Θ) for content"""
    emb = encode_anything(content)
    if emb.numtriad_triad:
        return {
            "delta": emb.numtriad_triad.delta,
            "infinity": emb.numtriad_triad.infinity,
            "theta": emb.numtriad_triad.theta,
        }
    return {"delta": 0.0, "infinity": 0.0, "theta": 0.0}


# ============================================================================
# BATCH ENCODING
# ============================================================================

def encode_batch(
    contents: list,
    domain: str = "auto"
) -> list:
    """
    Encode multiple items
    
    Args:
        contents: List of content items
        domain: Domain for all items
    
    Returns:
        List of UnifiedEmbedding
    """
    return [encode_anything(content, domain=domain) for content in contents]


def get_embedding_vectors(contents: list) -> np.ndarray:
    """Get embedding vectors for multiple items"""
    embeddings = encode_batch(contents)
    vectors = [e.fused_embedding for e in embeddings if e.fused_embedding is not None]
    return np.array(vectors) if vectors else np.array([])


# ============================================================================
# SIMILARITY
# ============================================================================

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors"""
    if a.size == 0 or b.size == 0:
        return 0.0
    
    a_norm = a / (np.linalg.norm(a) + 1e-8)
    b_norm = b / (np.linalg.norm(b) + 1e-8)
    return float(np.dot(a_norm, b_norm))


def similarity(content1: Union[str, bytes], content2: Union[str, bytes]) -> float:
    """Compute similarity between two content items"""
    emb1 = encode_anything(content1)
    emb2 = encode_anything(content2)
    
    if emb1.fused_embedding is None or emb2.fused_embedding is None:
        return 0.0
    
    return cosine_similarity(emb1.fused_embedding, emb2.fused_embedding)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    logger.info("=" * 70)
    logger.info("Unified Encoding API - Examples")
    logger.info("=" * 70)
    
    # Example 1: Encode text
    logger.info("\n--- Example 1: Encode Text ---")
    emb = encode_text("Hello, world!")
    logger.info(f"Embedding shape: {emb.fused_embedding.shape if emb.fused_embedding is not None else 'N/A'}")
    
    # Example 2: Encode code
    logger.info("\n--- Example 2: Encode Code ---")
    code = "def hello():\n    print('Hello')"
    emb = encode_code(code)
    triad = get_triad(code)
    logger.info(f"Triad: {triad}")
    
    # Example 3: Similarity
    logger.info("\n--- Example 3: Similarity ---")
    sim = similarity("machine learning", "neural networks")
    logger.info(f"Similarity: {sim:.3f}")
    
    # Example 4: Batch encoding
    logger.info("\n--- Example 4: Batch Encoding ---")
    texts = ["AI", "ML", "DL"]
    embeddings = encode_batch(texts)
    logger.info(f"Encoded {len(embeddings)} items")
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ Unified Encoding API ready!")
    logger.info("=" * 70)
