"""
Smart Search API
================

Intelligent search with automatic mode selection based on query analysis.
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

try:
    from core.unified_system import UnifiedGLM, SearchResult
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
# SMART SEARCH
# ============================================================================

def analyze_query_mode(query: str) -> str:
    """
    Analyze query and determine best search mode
    
    Returns: "abstract", "concrete", or "balanced"
    """
    glm = get_glm()
    
    # Encode query to get triad
    embedding = glm.encode_anything(query)
    
    if embedding.numtriad_triad:
        triad = embedding.numtriad_triad
        
        # High infinity -> abstract mode
        if triad.infinity > 0.6:
            logger.info(f"Query analysis: HIGH INFINITY ({triad.infinity:.3f}) -> abstract mode")
            return "abstract"
        
        # High theta -> concrete mode
        elif triad.theta > 0.6:
            logger.info(f"Query analysis: HIGH THETA ({triad.theta:.3f}) -> concrete mode")
            return "concrete"
        
        # Balanced
        else:
            logger.info(f"Query analysis: BALANCED -> balanced mode")
            return "balanced"
    
    return "balanced"


def smart_search(
    query: str,
    mode: str = "auto",
    k: int = 5,
    verbose: bool = True
) -> List[SearchResult]:
    """
    Intelligent search with automatic mode selection
    
    Args:
        query: Search query
        mode: "auto", "abstract", "concrete", "balanced"
        k: Number of results
        verbose: Print analysis
    
    Returns:
        List of SearchResult
    
    Examples:
        >>> # Auto-detect mode
        >>> results = smart_search("explain quantum mechanics")
        
        >>> # Force mode
        >>> results = smart_search("how to deploy", mode="concrete", k=10)
    """
    glm = get_glm()
    
    # Auto-detect mode if needed
    if mode == "auto":
        mode = analyze_query_mode(query)
        if verbose:
            logger.info(f"Auto-selected mode: {mode}")
    
    # Search
    results = glm.search(query, mode=mode, k=k)
    
    if verbose:
        logger.info(f"Found {len(results)} results in {mode} mode")
        for i, result in enumerate(results):
            logger.info(f"  {i+1}. {result.doc_id} (score={result.score:.3f})")
    
    return results


def search_abstract(query: str, k: int = 5) -> List[SearchResult]:
    """Search for abstract/theoretical content"""
    return smart_search(query, mode="abstract", k=k)


def search_concrete(query: str, k: int = 5) -> List[SearchResult]:
    """Search for concrete/practical content"""
    return smart_search(query, mode="concrete", k=k)


def search_balanced(query: str, k: int = 5) -> List[SearchResult]:
    """Search with balanced mode"""
    return smart_search(query, mode="balanced", k=k)


# ============================================================================
# ADVANCED SEARCH
# ============================================================================

def search_with_filters(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    mode: str = "auto",
    k: int = 5
) -> List[SearchResult]:
    """
    Search with metadata filters
    
    Args:
        query: Search query
        filters: Metadata filters (e.g., {"type": "tutorial"})
        mode: Search mode
        k: Number of results
    
    Returns:
        Filtered search results
    """
    results = smart_search(query, mode=mode, k=k*2)  # Get more to filter
    
    if filters:
        filtered = []
        for result in results:
            match = True
            for key, value in filters.items():
                if result.metadata.get(key) != value:
                    match = False
                    break
            if match:
                filtered.append(result)
        
        logger.info(f"Filtered {len(results)} -> {len(filtered)} results")
        return filtered[:k]
    
    return results[:k]


def search_by_triad(
    query: str,
    target_delta: Optional[float] = None,
    target_infinity: Optional[float] = None,
    target_theta: Optional[float] = None,
    k: int = 5
) -> List[SearchResult]:
    """
    Search with specific triad targets
    
    Args:
        query: Search query
        target_delta: Target delta value (0-1)
        target_infinity: Target infinity value (0-1)
        target_theta: Target theta value (0-1)
        k: Number of results
    
    Returns:
        Results matching triad targets
    """
    results = smart_search(query, mode="auto", k=k*2)
    
    # Score by triad distance
    def triad_distance(result: SearchResult) -> float:
        dist = 0.0
        if target_delta is not None:
            dist += abs(result.triad.delta - target_delta)
        if target_infinity is not None:
            dist += abs(result.triad.infinity - target_infinity)
        if target_theta is not None:
            dist += abs(result.triad.theta - target_theta)
        return dist
    
    # Sort by distance
    results_with_dist = [(r, triad_distance(r)) for r in results]
    results_with_dist.sort(key=lambda x: x[1])
    
    logger.info(f"Sorted by triad distance")
    return [r for r, _ in results_with_dist[:k]]


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    logger.info("=" * 70)
    logger.info("Smart Search API - Examples")
    logger.info("=" * 70)
    
    glm = get_glm()
    
    # Add sample documents
    logger.info("\n--- Adding Sample Documents ---")
    glm.add_document("doc1", "Abstract theory of machine learning and neural networks")
    glm.add_document("doc2", "How to deploy a machine learning model in production")
    glm.add_document("doc3", "Mathematical foundations of deep learning")
    glm.add_document("doc4", "Step-by-step tutorial: train your first neural network")
    glm.add_document("doc5", "Theoretical analysis of optimization algorithms")
    
    # Example 1: Auto-detect mode
    logger.info("\n--- Example 1: Auto-Detect Mode ---")
    results = smart_search("explain neural networks", verbose=True)
    
    # Example 2: Force abstract mode
    logger.info("\n--- Example 2: Abstract Mode ---")
    results = search_abstract("what is machine learning?", k=3)
    
    # Example 3: Force concrete mode
    logger.info("\n--- Example 3: Concrete Mode ---")
    results = search_concrete("how to train a model", k=3)
    
    # Example 4: Triad-based search
    logger.info("\n--- Example 4: Triad-Based Search ---")
    results = search_by_triad("learning", target_infinity=0.7, k=3)
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ Smart Search API ready!")
    logger.info("=" * 70)
