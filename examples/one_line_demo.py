#!/usr/bin/env python3
"""
One-Line Demo - GLM v4.0
=========================

Complete system in one line. Show the power of unified API.
"""

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# ONE-LINE EXAMPLES
# ============================================================================

def demo_encoding():
    """One-line encoding"""
    from core.unified_encoding import encode_anything
    
    logger.info("=" * 70)
    logger.info("ONE-LINE DEMO: Encoding")
    logger.info("=" * 70)
    
    # One line to encode
    emb = encode_anything("Hello, world!")
    logger.info(f"✅ Encoded: shape={emb.fused_embedding.shape if emb.fused_embedding is not None else 'N/A'}")


def demo_search():
    """One-line search"""
    from core.smart_search import smart_search
    from core.unified_system import create_unified_glm
    
    logger.info("\n" + "=" * 70)
    logger.info("ONE-LINE DEMO: Search")
    logger.info("=" * 70)
    
    # Setup
    glm = create_unified_glm()
    glm.add_document("doc1", "Machine learning is AI")
    glm.add_document("doc2", "Neural networks learn patterns")
    
    # One line to search
    results = smart_search("what is machine learning?")
    logger.info(f"✅ Found {len(results)} results")


def demo_answer():
    """One-line Q&A"""
    from core.unified_system import create_unified_glm
    
    logger.info("\n" + "=" * 70)
    logger.info("ONE-LINE DEMO: Q&A")
    logger.info("=" * 70)
    
    # Setup
    glm = create_unified_glm()
    glm.add_document("doc1", "Machine learning is a subset of AI")
    glm.add_document("doc2", "Neural networks are inspired by the brain")
    
    # One line to answer
    qa = glm.answer("what is machine learning?")
    logger.info(f"✅ Answer: {qa.answer[:50]}...")


def demo_similarity():
    """One-line similarity"""
    from core.unified_encoding import similarity
    
    logger.info("\n" + "=" * 70)
    logger.info("ONE-LINE DEMO: Similarity")
    logger.info("=" * 70)
    
    # One line to compute similarity
    sim = similarity("machine learning", "neural networks")
    logger.info(f"✅ Similarity: {sim:.3f}")


def demo_batch():
    """One-line batch encoding"""
    from core.unified_encoding import encode_batch, get_embedding_vectors
    
    logger.info("\n" + "=" * 70)
    logger.info("ONE-LINE DEMO: Batch Encoding")
    logger.info("=" * 70)
    
    # One line to encode multiple items
    embeddings = encode_batch(["AI", "ML", "DL"])
    logger.info(f"✅ Encoded {len(embeddings)} items")
    
    # One line to get vectors
    vectors = get_embedding_vectors(["AI", "ML", "DL"])
    logger.info(f"✅ Got vectors: shape={vectors.shape}")


def demo_triad():
    """One-line triad extraction"""
    from core.unified_encoding import get_triad
    
    logger.info("\n" + "=" * 70)
    logger.info("ONE-LINE DEMO: Triad Extraction")
    logger.info("=" * 70)
    
    # One line to get triad
    triad = get_triad("explain quantum mechanics")
    logger.info(f"✅ Triad: {triad}")


def demo_all_in_one():
    """Complete pipeline in one script"""
    from core.unified_system import create_unified_glm
    from core.smart_search import smart_search
    from core.unified_encoding import encode_anything, similarity
    
    logger.info("\n" + "=" * 70)
    logger.info("ONE-LINE DEMO: Complete Pipeline")
    logger.info("=" * 70)
    
    # Initialize
    glm = create_unified_glm()
    
    # Add documents
    glm.add_document("doc1", "Machine learning is a subset of artificial intelligence")
    glm.add_document("doc2", "Neural networks are inspired by biological neurons")
    glm.add_document("doc3", "Deep learning uses multiple layers of neural networks")
    
    # Encode
    emb = encode_anything("What is machine learning?")
    logger.info(f"1️⃣  Encoded query: shape={emb.fused_embedding.shape if emb.fused_embedding is not None else 'N/A'}")
    
    # Search
    results = smart_search("explain machine learning")
    logger.info(f"2️⃣  Found {len(results)} results")
    
    # Answer
    qa = glm.answer("what is machine learning?", k=3)
    logger.info(f"3️⃣  Generated answer: {qa.answer[:50]}...")
    
    # Similarity
    sim = similarity("machine learning", "neural networks")
    logger.info(f"4️⃣  Similarity: {sim:.3f}")
    
    # Status
    status = glm.get_status()
    logger.info(f"5️⃣  System status: {status['version']}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("\n")
    logger.info("╔" + "=" * 68 + "╗")
    logger.info("║" + " " * 15 + "GLM v4.0 - ONE-LINE DEMO" + " " * 29 + "║")
    logger.info("╚" + "=" * 68 + "╝")
    
    # Run demos
    demo_encoding()
    demo_search()
    demo_answer()
    demo_similarity()
    demo_batch()
    demo_triad()
    demo_all_in_one()
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ All demos completed!")
    logger.info("=" * 70)
    logger.info("\nKey takeaways:")
    logger.info("  - encode_anything() for universal encoding")
    logger.info("  - smart_search() for intelligent search")
    logger.info("  - glm.answer() for Q&A")
    logger.info("  - similarity() for semantic comparison")
    logger.info("  - All systems integrated seamlessly")
    logger.info("=" * 70)
