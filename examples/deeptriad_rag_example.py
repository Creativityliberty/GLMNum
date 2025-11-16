#!/usr/bin/env python3
"""
Exemple complet d'utilisation de DeepTriad RAG
===============================================

Démontre comment :
1. Créer un index RAG triad-aware
2. Ajouter des documents
3. Rechercher avec différents niveaux d'abstraction
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from numtriad.config import NumTriadConfig
from numtriad.encoders.numtriad_v3 import NumTriadV3Config
from numtriad.rag.deeptriad_rag import DeepTriadRAGIndex


def main():
    print("🚀 DeepTriad RAG Example\n")
    
    # ============================================================================
    # 1. Configuration
    # ============================================================================
    
    print("📋 Configuration...")
    cfg = NumTriadConfig(
        base_text_model_name="sentence-transformers/all-MiniLM-L6-v2",
        device="cpu",
    )

    v3_cfg = NumTriadV3Config(
        deeptriad_ckpt="checkpoints/deeptriad_transformer_v1.pt",
        max_len=16,
        triad_target_mode="auto",
        triad_alpha=1.0,
    )

    print("✅ Config created")

    # ============================================================================
    # 2. Créer l'index
    # ============================================================================
    
    print("\n🔧 Creating RAG Index...")
    index = DeepTriadRAGIndex(
        base_config=cfg,
        v3_config=v3_cfg,
        retrieval_mode="triad_weighted",
        triad_weight=0.3,
    )
    print("✅ Index created")

    # ============================================================================
    # 3. Ajouter des documents
    # ============================================================================
    
    print("\n📚 Adding documents...")
    
    docs = [
        "Ce papier propose une théorie générale de l'intelligence basée sur ∆∞Ο. Les concepts abstraits sont formalisés mathématiquement.",
        "Tutoriel pratique : comment déployer un service FastAPI avec Docker. Étapes concrètes et exemples de configuration.",
        "Analyse économique concrète d'un marché local en Afrique. Données empiriques et cas d'étude spécifiques.",
        "Introduction philosophique à la conscience et aux systèmes complexes. Discussion théorique des concepts fondamentaux.",
        "Guide d'installation de Python et des dépendances. Instructions pas à pas pour les débutants.",
        "Formalisation mathématique de la théorie des catégories. Définitions rigoureuses et théorèmes.",
    ]

    metas = [
        {"type": "theory", "domain": "AI"},
        {"type": "tutorial", "domain": "DevOps"},
        {"type": "case-study", "domain": "Economics"},
        {"type": "philosophy", "domain": "Consciousness"},
        {"type": "guide", "domain": "Setup"},
        {"type": "mathematics", "domain": "Category Theory"},
    ]

    index.add_documents(docs, metadatas=metas)
    
    print(f"\n📊 Index stats: {index.get_stats()}")

    # ============================================================================
    # 4. Recherche avec différents niveaux d'abstraction
    # ============================================================================
    
    print("\n" + "="*70)
    print("🔍 SEARCH TEST 1: Concrete Query")
    print("="*70)
    
    results = index.search(
        query="Comment déployer une API en production concrètement ?",
        k=3,
        triad_target="concrete",
    )

    print("\nQuery: 'Comment déployer une API en production concrètement ?'")
    print("Triad Target: CONCRETE\n")
    
    for i, (doc, score) in enumerate(results, 1):
        print(f"{i}. [{doc.doc_id}] Score: {score:.4f}")
        print(f"   Type: {doc.meta.get('type', 'unknown')}")
        print(f"   Text: {doc.text[:100]}...")
        print(f"   Triad: Δ={doc.triad.delta:.3f}, ∞={doc.triad.infinity:.3f}, Θ={doc.triad.theta:.3f}")
        print()

    # ============================================================================
    # 5. Recherche très conceptuelle
    # ============================================================================
    
    print("="*70)
    print("🔍 SEARCH TEST 2: Abstract Query")
    print("="*70)
    
    results = index.search(
        query="Quelle est une bonne définition générale de l'intelligence ?",
        k=3,
        triad_target="abstract",
    )

    print("\nQuery: 'Quelle est une bonne définition générale de l'intelligence ?'")
    print("Triad Target: ABSTRACT\n")
    
    for i, (doc, score) in enumerate(results, 1):
        print(f"{i}. [{doc.doc_id}] Score: {score:.4f}")
        print(f"   Type: {doc.meta.get('type', 'unknown')}")
        print(f"   Text: {doc.text[:100]}...")
        print(f"   Triad: Δ={doc.triad.delta:.3f}, ∞={doc.triad.infinity:.3f}, Θ={doc.triad.theta:.3f}")
        print()

    # ============================================================================
    # 6. Recherche équilibrée
    # ============================================================================
    
    print("="*70)
    print("🔍 SEARCH TEST 3: Balanced Query")
    print("="*70)
    
    results = index.search(
        query="Qu'est-ce qu'un système complexe ?",
        k=3,
        triad_target="balanced",
    )

    print("\nQuery: 'Qu'est-ce qu'un système complexe ?'")
    print("Triad Target: BALANCED\n")
    
    for i, (doc, score) in enumerate(results, 1):
        print(f"{i}. [{doc.doc_id}] Score: {score:.4f}")
        print(f"   Type: {doc.meta.get('type', 'unknown')}")
        print(f"   Text: {doc.text[:100]}...")
        print(f"   Triad: Δ={doc.triad.delta:.3f}, ∞={doc.triad.infinity:.3f}, Θ={doc.triad.theta:.3f}")
        print()

    # ============================================================================
    # 7. Recherche auto
    # ============================================================================
    
    print("="*70)
    print("🔍 SEARCH TEST 4: Auto Query (Natural)")
    print("="*70)
    
    results = index.search(
        query="Comment installer Python ?",
        k=3,
        triad_target="auto",
    )

    print("\nQuery: 'Comment installer Python ?'")
    print("Triad Target: AUTO\n")
    
    for i, (doc, score) in enumerate(results, 1):
        print(f"{i}. [{doc.doc_id}] Score: {score:.4f}")
        print(f"   Type: {doc.meta.get('type', 'unknown')}")
        print(f"   Text: {doc.text[:100]}...")
        print(f"   Triad: Δ={doc.triad.delta:.3f}, ∞={doc.triad.infinity:.3f}, Θ={doc.triad.theta:.3f}")
        print()

    # ============================================================================
    # 8. Comparaison des modes de retrieval
    # ============================================================================
    
    print("="*70)
    print("🔍 SEARCH TEST 5: Retrieval Mode Comparison")
    print("="*70)
    
    query = "Qu'est-ce que la théorie ?"
    
    print(f"\nQuery: '{query}'\n")
    
    # Mode cosine
    results_cosine = index.search(
        query=query,
        k=3,
        retrieval_mode="cosine",
    )
    
    print("Mode: COSINE (semantic similarity only)")
    for i, (doc, score) in enumerate(results_cosine, 1):
        print(f"  {i}. [{doc.doc_id}] Score: {score:.4f}")
    
    print()
    
    # Mode triad_weighted
    results_triad = index.search(
        query=query,
        k=3,
        retrieval_mode="triad_weighted",
    )
    
    print("Mode: TRIAD_WEIGHTED (semantic + triad distance)")
    for i, (doc, score) in enumerate(results_triad, 1):
        print(f"  {i}. [{doc.doc_id}] Score: {score:.4f}")

    print("\n" + "="*70)
    print("✅ Example completed!")
    print("="*70)


if __name__ == "__main__":
    main()
