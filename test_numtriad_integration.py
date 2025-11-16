#!/usr/bin/env python3
"""
Test d'intégration NumTriad avec système hybride.
Valide le fonctionnement en mode neuronal et heuristique.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_compatibility_detection():
    """Test la détection de compatibilité des dépendances."""
    print("🔍 Test de détection de compatibilité...")
    
    from numtriad.compatibility import get_compatibility_status
    status = get_compatibility_status()
    
    print(f"Python version: {status['python_version']}")
    print(f"Torch available: {status['torch_available']}")
    print(f"Sentence-transformers available: {status['sentence_transformers_available']}")
    print(f"Scipy available: {status['scipy_available']}")
    print(f"NumTriad mode: {status['numtriad_mode']}")
    
    assert isinstance(status, dict)
    assert 'numtriad_mode' in status
    print("✅ Détection de compatibilité fonctionnelle")
    return True

def test_fallback_encoder():
    """Test l'encodeur fallback."""
    print("\n🧪 Test de l'encodeur fallback...")
    
    from numtriad.compatibility import get_encoder
    
    encoder = get_encoder()
    test_texts = [
        "L'intelligence artificielle transforme les données",
        "Un exemple de code Python simple",
        "Concept théorique abstrait"
    ]
    
    try:
        result = encoder.encode(test_texts)
        
        print(f"Embeddings shape: {result.embeddings.shape}")
        print(f"Number of triads: {len(result.triads)}")
        
        for i, (text, triad) in enumerate(zip(test_texts, result.triads)):
            print(f"  {i+1}. '{text[:30]}...' → {triad}")
        
        # Validation
        assert result.embeddings.shape[0] == len(test_texts)
        assert len(result.triads) == len(test_texts)
        assert all(0 <= t.delta <= 1 for t in result.triads)
        assert all(0 <= t.infinity <= 1 for t in result.triads)
        assert all(0 <= t.theta <= 1 for t in result.triads)
        
        print("✅ Encodeur fallback fonctionnel")
        return True
        
    except Exception as e:
        print(f"❌ Erreur encodeur fallback: {e}")
        return False

def test_triad_operations():
    """Test les opérations sur les triades."""
    print("\n🔢 Test des opérations triadiques...")
    
    from numtriad.triad_types import Triad
    from numtriad.utils.metrics import triad_distance, triad_cosine
    
    # Créer des triades de test
    triad1 = Triad(delta=0.8, infinity=0.1, theta=0.1)  # Concret
    triad2 = Triad(delta=0.1, infinity=0.8, theta=0.1)  # Abstrait
    triad3 = Triad(delta=0.3, infinity=0.4, theta=0.3)  # Intermédiaire
    
    print(f"Triad1 (concret): {triad1}")
    print(f"Triad2 (abstrait): {triad2}")
    print(f"Triad3 (intermédiaire): {triad3}")
    
    # Test distance
    dist_12 = triad_distance(triad1, triad2)
    dist_13 = triad_distance(triad1, triad3)
    print(f"Distance concret-abstrait: {dist_12:.3f}")
    print(f"Distance concret-intermédiaire: {dist_13:.3f}")
    
    # Test similarité
    sim_12 = triad_cosine(triad1, triad2)
    sim_13 = triad_cosine(triad1, triad3)
    print(f"Similarité concret-abstrait: {sim_12:.3f}")
    print(f"Similarité concret-intermédiaire: {sim_13:.3f}")
    
    # Validation
    assert 0 <= dist_12 <= 3
    assert -1 <= sim_12 <= 1
    print("✅ Opérations triadiques fonctionnelles")
    return True

def test_glm_integration():
    """Test l'intégration avec GLM v3.0."""
    print("\n🔗 Test d'intégration GLM v3.0...")
    
    try:
        # Importer les composants GLM
        from core.symbolic import SymbolicEngine
        from domains.text import TextDomain
        from domains.code import CodeDomain
        
        # Créer le moteur GLM avec tous les domaines
        engine = SymbolicEngine()
        engine.register_domain(TextDomain())
        engine.register_domain(CodeDomain())
        
        # Test transformation avec le système existant
        text = "L'intelligence artificielle révolutionne la technologie"
        result = engine.transform(text, 'text', 'code')
        
        print(f"Transformation GLM: {type(result)}")
        print(f"Résultat: {str(result)[:100]}...")
        
        # Test avec la nouvelle API enrichie
        enriched_result = engine.transform_with_symbolic(text, 'text', 'code')
        
        print(f"Scores ∆∞Ó source: {enriched_result['source_symbolic']['metadata'].get('delta_score', 'N/A')}")
        print(f"Scores ∆∞Ó cible: {enriched_result['target_symbolic']['metadata'].get('delta_score', 'N/A')}")
        
        print("✅ Intégration GLM fonctionnelle")
        return True
        
    except Exception as e:
        print(f"❌ Erreur intégration GLM: {e}")
        return False

def test_hybrid_embedding_manager():
    """Test le gestionnaire d'embeddings hybride."""
    print("\n🎛️ Test du gestionnaire hybride...")
    
    try:
        from numtriad.compatibility import get_encoder
        
        # Créer le gestionnaire hybride
        encoder = get_encoder()
        
        # Test avec différents types de texte
        test_cases = [
            ("Concept abstrait", "L'intelligence artificielle est un concept théorique"),
            ("Code concret", "def calculate_sum(a, b): return a + b"),
            ("Texte mixte", "Le système utilise des algorithmes pour traiter les données")
        ]
        
        for category, text in test_cases:
            result = encoder.encode([text])
            triad = result.triads[0]
            
            print(f"  {category}: ∆={triad.delta:.3f}, ∞={triad.infinity:.3f}, Θ={triad.theta:.3f}")
        
        print("✅ Gestionnaire hybride fonctionnel")
        return True
        
    except Exception as e:
        print(f"❌ Erreur gestionnaire hybride: {e}")
        return False

def main():
    """Fonction principale de test."""
    print("🚀 Démarrage des tests d'intégration NumTriad...\n")
    
    tests = [
        test_compatibility_detection,
        test_fallback_encoder,
        test_triad_operations,
        test_glm_integration,
        test_hybrid_embedding_manager
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erreur dans {test.__name__}: {e}")
            results.append(False)
    
    # Résumé
    print(f"\n📊 Résumé des tests: {sum(results)}/{len(results)} réussis")
    
    if all(results):
        print("🎉 Tous les tests réussis! NumTriad est intégré avec succès.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les dépendances.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
