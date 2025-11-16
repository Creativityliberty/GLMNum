#!/usr/bin/env python3
"""
Test Suite for NumTriad System V4
==================================

Comprehensive tests for all 4 pillars:
- Pillar A: NumTriadMultimodalV4
- Pillar B: VisionTransformationEngine
- Pillar C: DeepTriadTransformer
- Pillar D: NumTriadRAGIndexV4
"""

import sys
import logging
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check PyTorch availability
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available - some tests will be skipped")

# Import system
try:
    from numtriad.core.system_v4 import (
        NumTriadSystemV4,
        NumTriadSystemConfig,
        DeepTriadTransformerConfig,
        NumTriadRAGIndexV4,
        IndexedDoc,
    )
    SYSTEM_AVAILABLE = True
except ImportError as e:
    SYSTEM_AVAILABLE = False
    logger.error(f"Cannot import NumTriad system: {e}")

# Try importing multimodal
try:
    from numtriad.multimodal_v4 import MultimodalV4Config
    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False
    logger.warning("NumTriadMultimodalV4 not available")


# ============================================================================
# TEST SUITE
# ============================================================================

class TestNumTriadV4:
    """Test suite for NumTriad System V4"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.system = None

    def log_test(self, name, status, message=""):
        """Log test result"""
        if status == "PASS":
            self.passed += 1
            logger.info(f"✅ {name}")
        elif status == "FAIL":
            self.failed += 1
            logger.error(f"❌ {name}: {message}")
        elif status == "SKIP":
            self.skipped += 1
            logger.warning(f"⏭️  {name}: {message}")

    def test_system_initialization(self):
        """Test 1: System initialization"""
        if not SYSTEM_AVAILABLE:
            self.log_test("System Initialization", "SKIP", "System not available")
            return

        try:
            if MULTIMODAL_AVAILABLE and TORCH_AVAILABLE:
                mm_cfg = MultimodalV4Config(
                    dim_text_in=256,
                    dim_vision_in=256,
                    dim_code_in=256,
                    dim_audio_in=128,
                    dim_proj=192,
                    dim_t_cross=32,
                    device="cpu"
                )
                dt_cfg = DeepTriadTransformerConfig(
                    dim_in=192,
                    dim_model=192,
                    num_layers=2,
                    num_heads=4,
                    dim_ff=384,
                    device="cpu"
                )
            else:
                mm_cfg = None
                dt_cfg = None

            sys_cfg = NumTriadSystemConfig(
                multimodal=mm_cfg,
                deeptriad=dt_cfg,
                device="cpu"
            )
            self.system = NumTriadSystemV4(sys_cfg)
            self.log_test("System Initialization", "PASS")
        except Exception as e:
            self.log_test("System Initialization", "FAIL", str(e))

    def test_rag_index_basic(self):
        """Test 2: RAG Index basic operations"""
        try:
            rag = NumTriadRAGIndexV4()

            # Create test documents
            doc1 = IndexedDoc(
                doc_id="doc1",
                embedding=np.random.randn(192).astype("float32"),
                triad=np.array([0.2, 0.6, 0.2], dtype="float32"),
                metadata={"type": "abstract"}
            )
            doc2 = IndexedDoc(
                doc_id="doc2",
                embedding=np.random.randn(192).astype("float32"),
                triad=np.array([0.1, 0.2, 0.7], dtype="float32"),
                metadata={"type": "concrete"}
            )

            # Add documents
            rag.add_document(doc1)
            rag.add_document(doc2)

            assert len(rag.docs) == 2, "Documents not added"
            self.log_test("RAG Index - Add Documents", "PASS")
        except Exception as e:
            self.log_test("RAG Index - Add Documents", "FAIL", str(e))

    def test_rag_query_modes(self):
        """Test 3: RAG query modes"""
        try:
            rag = NumTriadRAGIndexV4()

            # Add test documents
            for i in range(3):
                doc = IndexedDoc(
                    doc_id=f"doc{i}",
                    embedding=np.random.randn(192).astype("float32"),
                    triad=np.array([0.3, 0.3, 0.4], dtype="float32"),
                    metadata={"index": i}
                )
                rag.add_document(doc)

            # Test query
            query_emb = np.random.randn(192).astype("float32")
            query_triad = np.array([0.2, 0.6, 0.2], dtype="float32")

            # Test different modes
            for mode in ["auto", "abstract", "concrete", "balanced"]:
                results = rag.query(
                    query_embedding=query_emb,
                    query_triad=query_triad,
                    k=2,
                    mode=mode
                )
                assert len(results) <= 2, f"Query returned too many results for mode {mode}"

            self.log_test("RAG Query Modes", "PASS")
        except Exception as e:
            self.log_test("RAG Query Modes", "FAIL", str(e))

    def test_triad_alignment_scoring(self):
        """Test 4: Triad alignment scoring"""
        try:
            rag = NumTriadRAGIndexV4()

            # Test alignment scoring
            doc_triad = np.array([0.2, 0.6, 0.2], dtype="float32")
            target_triad = np.array([0.2, 0.6, 0.2], dtype="float32")

            score = rag._triad_alignment_score(doc_triad, target_triad)
            assert score > 0.99, f"Perfect alignment should score ~1.0, got {score}"

            # Test misalignment
            doc_triad = np.array([1.0, 0.0, 0.0], dtype="float32")
            target_triad = np.array([0.0, 0.0, 1.0], dtype="float32")

            score = rag._triad_alignment_score(doc_triad, target_triad)
            assert score < 0.1, f"Perfect misalignment should score ~0.0, got {score}"

            self.log_test("Triad Alignment Scoring", "PASS")
        except Exception as e:
            self.log_test("Triad Alignment Scoring", "FAIL", str(e))

    def test_cosine_similarity(self):
        """Test 5: Cosine similarity computation"""
        try:
            rag = NumTriadRAGIndexV4()

            # Test identical vectors
            a = np.array([1.0, 0.0, 0.0], dtype="float32")
            b = np.array([1.0, 0.0, 0.0], dtype="float32")
            sim = rag._cosine_sim(a, b)
            assert abs(sim - 1.0) < 0.01, f"Identical vectors should have sim=1.0, got {sim}"

            # Test orthogonal vectors
            a = np.array([1.0, 0.0, 0.0], dtype="float32")
            b = np.array([0.0, 1.0, 0.0], dtype="float32")
            sim = rag._cosine_sim(a, b)
            assert abs(sim) < 0.01, f"Orthogonal vectors should have sim=0.0, got {sim}"

            self.log_test("Cosine Similarity", "PASS")
        except Exception as e:
            self.log_test("Cosine Similarity", "FAIL", str(e))

    def test_system_status(self):
        """Test 6: System status reporting"""
        if not self.system:
            self.log_test("System Status", "SKIP", "System not initialized")
            return

        try:
            status = self.system.get_status()
            assert isinstance(status, dict), "Status should be a dict"
            assert "pillar_a_multimodal" in status, "Missing pillar A status"
            assert "pillar_b_vte" in status, "Missing pillar B status"
            assert "pillar_c_deeptriad" in status, "Missing pillar C status"
            assert "pillar_d_rag" in status, "Missing pillar D status"
            self.log_test("System Status", "PASS")
        except Exception as e:
            self.log_test("System Status", "FAIL", str(e))

    def test_multimodal_encoding(self):
        """Test 7: Multimodal encoding (if available)"""
        if not self.system or not MULTIMODAL_AVAILABLE:
            self.log_test("Multimodal Encoding", "SKIP", "Multimodal not available")
            return

        try:
            emb, triad = self.system.encode_sample(texts=["test"])
            assert emb.shape[0] == 1, "Batch size should be 1"
            assert triad.shape == (1, 3), "Triad shape should be (1, 3)"
            assert np.allclose(triad.sum(axis=1), 1.0, atol=0.01), "Triad should sum to 1"
            self.log_test("Multimodal Encoding", "PASS")
        except Exception as e:
            self.log_test("Multimodal Encoding", "FAIL", str(e))

    def test_document_indexing(self):
        """Test 8: Document indexing (if available)"""
        if not self.system or not MULTIMODAL_AVAILABLE:
            self.log_test("Document Indexing", "SKIP", "Multimodal not available")
            return

        try:
            self.system.add_document(
                "doc1",
                texts=["Test document"],
                metadata={"type": "test"}
            )
            assert len(self.system.rag_index.docs) == 1, "Document not added"
            self.log_test("Document Indexing", "PASS")
        except Exception as e:
            self.log_test("Document Indexing", "FAIL", str(e))

    def test_document_querying(self):
        """Test 9: Document querying (if available)"""
        if not self.system or not MULTIMODAL_AVAILABLE:
            self.log_test("Document Querying", "SKIP", "Multimodal not available")
            return

        try:
            # Add documents
            self.system.add_document("doc1", texts=["Abstract theory"])
            self.system.add_document("doc2", texts=["Concrete tutorial"])

            # Query
            results = self.system.query_documents("theory", mode="abstract", k=2)
            assert len(results) <= 2, "Query returned too many results"
            self.log_test("Document Querying", "PASS")
        except Exception as e:
            self.log_test("Document Querying", "FAIL", str(e))

    def test_sequence_analysis(self):
        """Test 10: Sequence analysis (if available)"""
        if not self.system or not TORCH_AVAILABLE or not self.system.deeptriad:
            self.log_test("Sequence Analysis", "SKIP", "DeepTriad not available")
            return

        try:
            # Create sequence
            seq = np.random.randn(5, 192).astype("float32")
            triad_global, triad_steps = self.system.triad_sequence_analysis(seq)

            assert triad_global.shape == (3,), "Global triad shape incorrect"
            assert triad_steps.shape == (5, 3), "Steps triad shape incorrect"
            assert np.allclose(triad_global.sum(), 1.0, atol=0.01), "Global triad should sum to 1"
            self.log_test("Sequence Analysis", "PASS")
        except Exception as e:
            self.log_test("Sequence Analysis", "FAIL", str(e))

    def run_all_tests(self):
        """Run all tests"""
        logger.info("=" * 70)
        logger.info("NumTriad System V4 - Test Suite")
        logger.info("=" * 70)

        self.test_system_initialization()
        self.test_rag_index_basic()
        self.test_rag_query_modes()
        self.test_triad_alignment_scoring()
        self.test_cosine_similarity()
        self.test_system_status()
        self.test_multimodal_encoding()
        self.test_document_indexing()
        self.test_document_querying()
        self.test_sequence_analysis()

        logger.info("=" * 70)
        logger.info(f"Results: ✅ {self.passed} passed, ❌ {self.failed} failed, ⏭️  {self.skipped} skipped")
        logger.info("=" * 70)

        return self.failed == 0


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    tester = TestNumTriadV4()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
