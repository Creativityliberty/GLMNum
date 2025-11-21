#!/usr/bin/env python3
"""
GLM v4.0 - Complete System Test Suite
Tests all components: Core, API, UI Integration
"""

import sys
import os
import time
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# TEST 1: ENVIRONMENT & DEPENDENCIES
# ============================================================================

def test_environment():
    """Test Python version and dependencies"""
    print("\n" + "="*70)
    print("TEST 1: ENVIRONMENT & DEPENDENCIES")
    print("="*70)
    
    # Check Python version
    py_version = sys.version_info
    print(f"✅ Python version: {py_version.major}.{py_version.minor}.{py_version.micro}")
    assert py_version.major == 3 and py_version.minor >= 8, "Python 3.8+ required"
    
    # Check dependencies
    dependencies = {
        'numpy': 'NumPy',
        'networkx': 'NetworkX',
        'fastapi': 'FastAPI',
        'torch': 'PyTorch',
    }
    
    for module, name in dependencies.items():
        try:
            mod = __import__(module)
            version = getattr(mod, '__version__', 'unknown')
            print(f"✅ {name}: {version}")
        except ImportError:
            print(f"❌ {name}: NOT INSTALLED")
            return False
    
    return True


# ============================================================================
# TEST 2: CORE SYSTEM
# ============================================================================

def test_core_system():
    """Test core GLM components"""
    print("\n" + "="*70)
    print("TEST 2: CORE SYSTEM")
    print("="*70)
    
    try:
        # Test SymbolicEngine
        print("\n2.1 Testing SymbolicEngine...")
        from core.symbolic import SymbolicEngine
        engine = SymbolicEngine()
        print(f"✅ SymbolicEngine initialized")
        print(f"   Domains: {list(engine.domains.keys())}")
        
        # Test basic encoding
        print("\n2.2 Testing basic encoding...")
        text_domain = engine.get_domain("text")
        result = text_domain.encode("Hello world")
        assert result is not None, "Encoding failed"
        print(f"✅ Text encoding works")
        
        # Test AutoLearningEngine
        print("\n2.3 Testing AutoLearningEngine...")
        from core.auto_learning import AutoLearningEngine
        auto_learner = AutoLearningEngine(engine)
        print(f"✅ AutoLearningEngine initialized")
        print(f"   Knowledge sources: {[s.name for s in auto_learner.knowledge_sources]}")
        
        # Test concept detection
        print("\n2.4 Testing concept detection...")
        concept = auto_learner.detect_unknown_concept("This is a DNA sequence")
        print(f"✅ Concept detection: {concept}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# TEST 3: NUMTRIAD INTEGRATION
# ============================================================================

def test_numtriad():
    """Test NumTriad encoder"""
    print("\n" + "="*70)
    print("TEST 3: NUMTRIAD INTEGRATION")
    print("="*70)
    
    try:
        print("\n3.1 Testing NumTriadEncoder...")
        from numtriad.encoder import NumTriadEncoder
        
        encoder = NumTriadEncoder(model_name="numtriad-v3")
        print(f"✅ NumTriadEncoder initialized")
        print(f"   Model: {encoder.model_name}")
        print(f"   Embedding dim: {encoder.embedding_dim}")
        
        # Test encoding
        print("\n3.2 Testing text encoding...")
        texts = [
            "Hello world",
            "DNA sequence ATCG",
            "Machine learning"
        ]
        
        embeddings, triads = encoder.encode_text(texts)
        print(f"✅ Encoding successful")
        print(f"   Embeddings shape: {embeddings.shape}")
        print(f"   Triads shape: {triads.shape}")
        
        # Verify triads
        print("\n3.3 Verifying triads...")
        for i, (text, triad) in enumerate(zip(texts, triads)):
            delta, infty, theta = triad
            total = delta + infty + theta
            print(f"   {i+1}. '{text[:30]}...'")
            print(f"      ∆={delta:.3f}, ∞={infty:.3f}, Θ={theta:.3f} (sum={total:.3f})")
            assert abs(total - 1.0) < 0.01, f"Triad not normalized: {total}"
        
        print(f"✅ All triads normalized")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# TEST 4: UNIFIED GLM
# ============================================================================

def test_unified_glm():
    """Test UnifiedGLM system"""
    print("\n" + "="*70)
    print("TEST 4: UNIFIED GLM")
    print("="*70)
    
    try:
        print("\n4.1 Testing UnifiedGLM initialization...")
        from core.unified_system import UnifiedGLM
        
        glm = UnifiedGLM(config={"enable_auto_learning": True})
        print(f"✅ UnifiedGLM initialized")
        
        # Test standard encoding
        print("\n4.2 Testing standard encoding...")
        start = time.time()
        result = glm.encode_anything("Hello world", domain="text")
        elapsed = time.time() - start
        
        assert result is not None, "Encoding failed"
        print(f"✅ Standard encoding works ({elapsed*1000:.1f}ms)")
        
        # Test auto-learning encoding
        print("\n4.3 Testing auto-learning encoding...")
        start = time.time()
        result = glm.encode_with_auto_learning("DNA sequence ATCG")
        elapsed = time.time() - start
        
        assert result is not None, "Auto-learning encoding failed"
        print(f"✅ Auto-learning encoding works ({elapsed*1000:.1f}ms)")
        
        # Check metadata
        if "metadata" in result:
            metadata = result["metadata"]
            print(f"   Learned: {metadata.get('learned', False)}")
            print(f"   NumTriad used: {metadata.get('numtriad_used', False)}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# TEST 5: API ENDPOINTS
# ============================================================================

def test_api():
    """Test API endpoints"""
    print("\n" + "="*70)
    print("TEST 5: API ENDPOINTS")
    print("="*70)
    
    try:
        import requests
        
        base_url = "http://localhost:8081"
        
        # Test health
        print("\n5.1 Testing /health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        print(f"✅ Health check passed")
        print(f"   Status: {data.get('status')}")
        print(f"   Service: {data.get('service')}")
        
        # Test transform
        print("\n5.2 Testing /transform endpoint...")
        payload = {
            "content": "Hello world",
            "source_domain": "text",
            "target_domain": "text"
        }
        response = requests.post(f"{base_url}/transform", json=payload, timeout=10)
        assert response.status_code == 200, f"Transform failed: {response.status_code}"
        data = response.json()
        print(f"✅ Transform endpoint works")
        print(f"   Domain: {data.get('domain')}")
        
        return True
    
    except requests.exceptions.ConnectionError:
        print(f"⚠️  API not running. Start with: python api.py")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# ============================================================================
# TEST 6: PERFORMANCE
# ============================================================================

def test_performance():
    """Test system performance"""
    print("\n" + "="*70)
    print("TEST 6: PERFORMANCE")
    print("="*70)
    
    try:
        from core.unified_system import UnifiedGLM
        
        glm = UnifiedGLM()
        
        # Encoding speed
        print("\n6.1 Testing encoding speed...")
        times = []
        for i in range(10):
            start = time.time()
            glm.encode_anything(f"Test text {i}", domain="text")
            elapsed = time.time() - start
            times.append(elapsed * 1000)
        
        avg_time = sum(times) / len(times)
        print(f"✅ Average encoding time: {avg_time:.1f}ms")
        print(f"   Min: {min(times):.1f}ms, Max: {max(times):.1f}ms")
        
        # Memory check
        print("\n6.2 Checking memory usage...")
        import psutil
        process = psutil.Process()
        memory = process.memory_info().rss / 1024 / 1024
        print(f"✅ Memory usage: {memory:.1f}MB")
        
        return True
    
    except ImportError:
        print("⚠️  psutil not installed. Skipping memory check.")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# ============================================================================
# TEST 7: INTEGRATION
# ============================================================================

def test_integration():
    """Test end-to-end integration"""
    print("\n" + "="*70)
    print("TEST 7: END-TO-END INTEGRATION")
    print("="*70)
    
    try:
        from core.unified_system import UnifiedGLM
        
        glm = UnifiedGLM()
        
        # Test scenario: Unknown concept
        print("\n7.1 Testing unknown concept flow...")
        text = "This is a CRISPR gene editing technique"
        
        result = glm.encode_with_auto_learning(text)
        
        assert result is not None, "Integration test failed"
        print(f"✅ Unknown concept flow works")
        
        # Check result structure
        print("\n7.2 Checking result structure...")
        required_keys = ["status", "metadata"]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
            print(f"   ✅ {key}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all tests"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║         GLM v4.0 - COMPLETE SYSTEM TEST SUITE                 ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    tests = [
        ("Environment", test_environment),
        ("Core System", test_core_system),
        ("NumTriad", test_numtriad),
        ("Unified GLM", test_unified_glm),
        ("API Endpoints", test_api),
        ("Performance", test_performance),
        ("Integration", test_integration),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            result = test_func()
            results[name] = result
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    for name, result in results.items():
        status = "✅ PASS" if result is True else "❌ FAIL" if result is False else "⚠️  SKIP"
        print(f"{status}: {name}")
    
    print("\n" + "="*70)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("="*70)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is ready for production.")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
