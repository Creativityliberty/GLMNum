"""
GLM v3.0 - Complete Test Suite
===============================

Comprehensive testing of all v3.0 features:
- Image Domain
- Web UI API
- Neural Encoders
- Integration

Author: GLM Research Team
Date: 2024-11-15
"""

import sys
import os
import time
import numpy as np
from typing import Dict, List, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.symbolic import SymbolicEngine
from domains.geometric import GeometricDomain
from domains.text import TextDomain
from domains.code import CodeDomain
from domains.image import ImageDomain
from encoders.neural import NomicTextEncoder, NomicImageEncoder
from encoders.integration import EnhancedTextDomainWithNomic, EnhancedImageDomainWithNomic


# ============================================================================
# TEST UTILITIES
# ============================================================================

class TestResults:
    """Track test results"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_pass(self, name: str, duration: float = 0):
        self.passed += 1
        self.tests.append((name, "PASS", duration))
    
    def add_fail(self, name: str, error: str, duration: float = 0):
        self.failed += 1
        self.tests.append((name, "FAIL", duration, error))
    
    def print_summary(self):
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        for test in self.tests:
            name = test[0]
            status = test[1]
            duration = test[2]
            
            if status == "PASS":
                print(f"✅ {name:<50} {duration*1000:>6.2f}ms")
            else:
                error = test[3]
                print(f"❌ {name:<50} {error}")
        
        print("="*70)
        print(f"Total: {self.passed} passed, {self.failed} failed")
        print(f"Success rate: {self.passed/(self.passed+self.failed)*100:.1f}%")
        print("="*70)


def print_header(title: str):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


# ============================================================================
# TEST SUITES
# ============================================================================

class TestImageDomain:
    """Test Image Domain"""
    
    def __init__(self):
        self.results = TestResults()
        self.domain = ImageDomain(embedding_dim=128)
    
    def run_all(self):
        print_header("TEST SUITE 1: IMAGE DOMAIN")
        
        self.test_simple_image()
        self.test_multi_color_image()
        self.test_image_similarity()
        self.test_round_trip_fidelity()
        
        return self.results
    
    def test_simple_image(self):
        """Test simple image encoding"""
        try:
            start = time.time()
            
            # Create simple red square
            image = np.zeros((100, 100, 3), dtype=np.uint8)
            image[20:80, 20:80] = [255, 0, 0]
            
            sym = self.domain.encode(image)
            
            assert sym.delta.shape == (128,), f"Delta shape mismatch: {sym.delta.shape}"
            assert sym.omega.shape == (128,), f"Omega shape mismatch: {sym.omega.shape}"
            assert sym.infinity.number_of_nodes() > 0, "No nodes in graph"
            
            duration = time.time() - start
            self.results.add_pass("Image: Simple Red Square", duration)
        except Exception as e:
            self.results.add_fail("Image: Simple Red Square", str(e))
    
    def test_multi_color_image(self):
        """Test multi-color image"""
        try:
            start = time.time()
            
            image = np.zeros((100, 100, 3), dtype=np.uint8)
            image[0:50, 0:50] = [255, 0, 0]      # Red
            image[0:50, 50:100] = [0, 255, 0]    # Green
            image[50:100, 0:50] = [0, 0, 255]    # Blue
            image[50:100, 50:100] = [255, 255, 0]  # Yellow
            
            sym = self.domain.encode(image)
            description = self.domain.decode(sym)
            
            assert len(description) > 0, "Empty description"
            assert "Image" in description, "Missing 'Image' in description"
            
            duration = time.time() - start
            self.results.add_pass("Image: Multi-color Quadrants", duration)
        except Exception as e:
            self.results.add_fail("Image: Multi-color Quadrants", str(e))
    
    def test_image_similarity(self):
        """Test image similarity"""
        try:
            start = time.time()
            
            # Similar images
            img1 = np.zeros((100, 100, 3), dtype=np.uint8)
            img1[20:80, 20:80] = [255, 0, 0]
            
            img2 = np.zeros((100, 100, 3), dtype=np.uint8)
            img2[25:75, 25:75] = [255, 0, 0]
            
            sym1 = self.domain.encode(img1)
            sym2 = self.domain.encode(img2)
            
            similarity = np.dot(sym1.omega, sym2.omega)
            
            assert 0 <= similarity <= 1, f"Invalid similarity: {similarity}"
            assert similarity > 0.5, f"Similarity too low: {similarity}"
            
            duration = time.time() - start
            self.results.add_pass("Image: Similarity Calculation", duration)
        except Exception as e:
            self.results.add_fail("Image: Similarity Calculation", str(e))
    
    def test_round_trip_fidelity(self):
        """Test round-trip fidelity"""
        try:
            start = time.time()
            
            image = np.full((50, 50, 3), [128, 64, 192], dtype=np.uint8)
            
            sym1 = self.domain.encode(image)
            decoded = self.domain.decode(sym1)
            sym2 = self.domain.encode(image)  # Re-encode
            
            fidelity = np.dot(sym1.omega, sym2.omega)
            
            assert fidelity > 0.95, f"Low fidelity: {fidelity}"
            
            duration = time.time() - start
            self.results.add_pass("Image: Round-trip Fidelity", duration)
        except Exception as e:
            self.results.add_fail("Image: Round-trip Fidelity", str(e))


class TestNeuralEncoders:
    """Test Neural Encoders"""
    
    def __init__(self):
        self.results = TestResults()
        self.text_encoder = NomicTextEncoder(embedding_dim=768)
        self.image_encoder = NomicImageEncoder(embedding_dim=768)
    
    def run_all(self):
        print_header("TEST SUITE 2: NEURAL ENCODERS")
        
        self.test_text_encoding()
        self.test_image_encoding()
        self.test_text_similarity()
        self.test_image_similarity()
        
        return self.results
    
    def test_text_encoding(self):
        """Test text encoding"""
        try:
            start = time.time()
            
            text = "Artificial intelligence is transforming the world"
            embedding = self.text_encoder.encode(text)
            
            assert embedding.shape == (768,), f"Wrong shape: {embedding.shape}"
            assert np.linalg.norm(embedding) > 0, "Zero embedding"
            
            duration = time.time() - start
            self.results.add_pass("Neural: Text Encoding", duration)
        except Exception as e:
            self.results.add_fail("Neural: Text Encoding", str(e))
    
    def test_image_encoding(self):
        """Test image encoding"""
        try:
            start = time.time()
            
            image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            embedding = self.image_encoder.encode(image)
            
            assert embedding.shape == (768,), f"Wrong shape: {embedding.shape}"
            assert np.linalg.norm(embedding) > 0, "Zero embedding"
            
            duration = time.time() - start
            self.results.add_pass("Neural: Image Encoding", duration)
        except Exception as e:
            self.results.add_fail("Neural: Image Encoding", str(e))
    
    def test_text_similarity(self):
        """Test text similarity"""
        try:
            start = time.time()
            
            texts = [
                "The cat sat on the mat",
                "A feline rested on the rug",
                "Machine learning is powerful"
            ]
            
            embeddings = self.text_encoder.encode(texts)
            
            sim_1_2 = np.dot(embeddings[0], embeddings[1])
            sim_1_3 = np.dot(embeddings[0], embeddings[2])
            
            assert 0 <= sim_1_2 <= 1, f"Invalid similarity: {sim_1_2}"
            assert 0 <= sim_1_3 <= 1, f"Invalid similarity: {sim_1_3}"
            
            duration = time.time() - start
            self.results.add_pass("Neural: Text Similarity", duration)
        except Exception as e:
            self.results.add_fail("Neural: Text Similarity", str(e))
    
    def test_image_similarity(self):
        """Test image similarity"""
        try:
            start = time.time()
            
            img1 = np.zeros((100, 100, 3), dtype=np.uint8)
            img1[20:80, 20:80] = [255, 0, 0]
            
            img2 = np.zeros((100, 100, 3), dtype=np.uint8)
            img2[20:80, 20:80] = [0, 255, 0]
            
            emb1 = self.image_encoder.encode(img1)
            emb2 = self.image_encoder.encode(img2)
            
            similarity = np.dot(emb1, emb2)
            
            assert 0 <= similarity <= 1, f"Invalid similarity: {similarity}"
            
            duration = time.time() - start
            self.results.add_pass("Neural: Image Similarity", duration)
        except Exception as e:
            self.results.add_fail("Neural: Image Similarity", str(e))


class TestEnhancedDomains:
    """Test Enhanced Domains with Neural Encoders"""
    
    def __init__(self):
        self.results = TestResults()
        self.text_domain = EnhancedTextDomainWithNomic(embedding_dim=768)
        self.image_domain = EnhancedImageDomainWithNomic(embedding_dim=768)
    
    def run_all(self):
        print_header("TEST SUITE 3: ENHANCED DOMAINS")
        
        self.test_enhanced_text()
        self.test_enhanced_image()
        self.test_cross_domain()
        
        return self.results
    
    def test_enhanced_text(self):
        """Test enhanced text domain"""
        try:
            start = time.time()
            
            text = "Natural language processing with neural networks"
            sym = self.text_domain.encode(text)
            
            assert sym.delta.shape == (768,), f"Delta shape: {sym.delta.shape}"
            assert sym.omega.shape == (768,), f"Omega shape: {sym.omega.shape}"
            assert sym.infinity.number_of_nodes() > 0, "No nodes"
            
            decoded = self.text_domain.decode(sym)
            assert len(decoded) > 0, "Empty decoded"
            
            duration = time.time() - start
            self.results.add_pass("Enhanced: Text Domain", duration)
        except Exception as e:
            self.results.add_fail("Enhanced: Text Domain", str(e))
    
    def test_enhanced_image(self):
        """Test enhanced image domain"""
        try:
            start = time.time()
            
            image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            sym = self.image_domain.encode(image)
            
            assert sym.delta.shape == (768,), f"Delta shape: {sym.delta.shape}"
            assert sym.omega.shape == (768,), f"Omega shape: {sym.omega.shape}"
            assert sym.infinity.number_of_nodes() > 0, "No nodes"
            
            decoded = self.image_domain.decode(sym)
            assert len(decoded) > 0, "Empty decoded"
            
            duration = time.time() - start
            self.results.add_pass("Enhanced: Image Domain", duration)
        except Exception as e:
            self.results.add_fail("Enhanced: Image Domain", str(e))
    
    def test_cross_domain(self):
        """Test cross-domain operations"""
        try:
            start = time.time()
            
            # Encode text
            text = "Red square on white background"
            text_sym = self.text_domain.encode(text)
            
            # Encode image
            image = np.zeros((100, 100, 3), dtype=np.uint8)
            image[20:80, 20:80] = [255, 0, 0]
            image_sym = self.image_domain.encode(image)
            
            # Compare
            similarity = np.dot(text_sym.omega, image_sym.omega)
            assert 0 <= similarity <= 1, f"Invalid similarity: {similarity}"
            
            duration = time.time() - start
            self.results.add_pass("Enhanced: Cross-domain", duration)
        except Exception as e:
            self.results.add_fail("Enhanced: Cross-domain", str(e))


class TestIntegration:
    """Test full integration"""
    
    def __init__(self):
        self.results = TestResults()
    
    def run_all(self):
        print_header("TEST SUITE 4: FULL INTEGRATION")
        
        self.test_engine_with_all_domains()
        self.test_transformations()
        self.test_performance()
        
        return self.results
    
    def test_engine_with_all_domains(self):
        """Test engine with all domains"""
        try:
            start = time.time()
            
            engine = SymbolicEngine(embedding_dim=128)
            engine.register_domain(GeometricDomain())
            engine.register_domain(TextDomain())
            engine.register_domain(CodeDomain())
            engine.register_domain(ImageDomain())
            
            domains = engine.list_domains()
            assert len(domains) == 4, f"Wrong domain count: {len(domains)}"
            
            duration = time.time() - start
            self.results.add_pass("Integration: Engine Setup", duration)
        except Exception as e:
            self.results.add_fail("Integration: Engine Setup", str(e))
    
    def test_transformations(self):
        """Test transformations"""
        try:
            start = time.time()
            
            engine = SymbolicEngine(embedding_dim=128)
            engine.register_domain(TextDomain())
            engine.register_domain(CodeDomain())
            
            # Transform text to code
            result = engine.transform(
                "function to add two numbers",
                "text",
                "code"
            )
            
            assert result is not None, "Null result"
            assert len(str(result)) > 0, "Empty result"
            
            duration = time.time() - start
            self.results.add_pass("Integration: Transformations", duration)
        except Exception as e:
            self.results.add_fail("Integration: Transformations", str(e))
    
    def test_performance(self):
        """Test performance metrics"""
        try:
            start = time.time()
            
            engine = SymbolicEngine(embedding_dim=128)
            engine.register_domain(TextDomain())
            
            # Multiple transformations
            for i in range(5):
                engine.abstract("Test text", "text")
            
            stats = engine.get_stats()
            assert stats['total_transformations'] > 0, "No transformations"
            
            duration = time.time() - start
            self.results.add_pass("Integration: Performance", duration)
        except Exception as e:
            self.results.add_fail("Integration: Performance", str(e))


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all test suites"""
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  GLM v3.0 - COMPLETE TEST SUITE".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝")
    
    all_results = []
    
    # Run test suites
    suite1 = TestImageDomain()
    all_results.append(suite1.run_all())
    
    suite2 = TestNeuralEncoders()
    all_results.append(suite2.run_all())
    
    suite3 = TestEnhancedDomains()
    all_results.append(suite3.run_all())
    
    suite4 = TestIntegration()
    all_results.append(suite4.run_all())
    
    # Print combined summary
    print("\n" + "="*70)
    print("OVERALL TEST SUMMARY")
    print("="*70)
    
    total_passed = sum(r.passed for r in all_results)
    total_failed = sum(r.failed for r in all_results)
    total_tests = total_passed + total_failed
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"Success Rate: {total_passed/total_tests*100:.1f}%")
    
    print("\n" + "="*70)
    if total_failed == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {total_failed} test(s) failed")
    print("="*70)
    
    return total_passed, total_failed


if __name__ == "__main__":
    passed, failed = run_all_tests()
    sys.exit(0 if failed == 0 else 1)
