#!/usr/bin/env python3
"""
Example: Gemini Triad-Aware QA System
======================================

Demonstrates the complete pipeline:
1. NumTriadEmbeddingV3 (question encoding)
2. DeepTriadRAGIndex (triad-aware retrieval)
3. GeminiTriadWrapper (orchestration + LLM)

Author: GLM Research Team
Date: 2024-11-16
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from numtriad.config import NumTriadConfig
from numtriad.encoders.numtriad_v3 import NumTriadV3Config
from numtriad.rag.deeptriad_rag import DeepTriadRAGIndex
from numtriad.llm.gemini_triad_wrapper import GeminiTriadWrapper, GeminiConfig


def main():
    print("🚀 Gemini Triad-Aware QA System Example\n")
    
    # ============================================================================
    # 1. Configuration
    # ============================================================================
    
    print("📋 Step 1: Configuration...")
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

    gemini_cfg = GeminiConfig(
        model_name="gemini-2.0-flash",
        max_output_tokens=1024,
        temperature=0.3,
    )

    print("✅ Configuration created\n")

    # ============================================================================
    # 2. Create RAG Index
    # ============================================================================
    
    print("🔧 Step 2: Creating RAG Index...")
    index = DeepTriadRAGIndex(
        base_config=cfg,
        v3_config=v3_cfg,
        retrieval_mode="triad_weighted",
        triad_weight=0.3,
    )
    print("✅ RAG Index created\n")

    # ============================================================================
    # 3. Add Documents
    # ============================================================================
    
    print("📚 Step 3: Adding documents...")
    
    documents = [
        "L'intelligence artificielle générale (AGI) est un concept théorique représentant une IA capable de comprendre et d'effectuer n'importe quelle tâche intellectuelle qu'un humain peut faire. C'est un domaine de recherche actif avec des implications philosophiques profondes.",
        
        "Pour déployer une application FastAPI en production, vous devez : 1) Créer un fichier requirements.txt, 2) Utiliser un serveur ASGI comme Uvicorn, 3) Configurer un reverse proxy (Nginx), 4) Mettre en place des certificats SSL, 5) Monitorer les logs et les performances.",
        
        "La théorie des catégories est une branche abstraite des mathématiques qui étudie les structures mathématiques générales. Elle fournit un langage unifié pour décrire les relations entre différentes structures mathématiques.",
        
        "Docker est un outil de containerisation qui permet de packager une application avec toutes ses dépendances. Pour créer un container : 1) Écrire un Dockerfile, 2) Builder l'image, 3) Lancer le container avec docker run.",
        
        "La complexité algorithmique mesure l'efficacité d'un algorithme. La notation Big-O décrit comment le temps d'exécution croît avec la taille de l'entrée. Par exemple, O(n) est linéaire, O(n²) est quadratique.",
    ]

    metadata = [
        {"type": "theory", "domain": "AI", "level": "advanced"},
        {"type": "tutorial", "domain": "DevOps", "level": "intermediate"},
        {"type": "mathematics", "domain": "Category Theory", "level": "advanced"},
        {"type": "tutorial", "domain": "DevOps", "level": "beginner"},
        {"type": "computer_science", "domain": "Algorithms", "level": "intermediate"},
    ]

    index.add_documents(documents, metadatas=metadata)
    print(f"✅ Added {len(documents)} documents\n")

    # ============================================================================
    # 4. Create Gemini Wrapper
    # ============================================================================
    
    print("🤖 Step 4: Creating Gemini Wrapper...")
    # Note: gemini_client=None means we'll use fallback mode
    # To use real Gemini, pass: gemini_client=genai.GenerativeModel(...)
    wrapper = GeminiTriadWrapper(
        rag_index=index,
        gemini_client=None,  # Set to real client if available
        gemini_cfg=gemini_cfg,
    )
    print("✅ Wrapper created\n")

    # ============================================================================
    # 5. Test Queries with Different Triad Targets
    # ============================================================================
    
    print("="*70)
    print("🔍 TEST 1: Concrete Query (Practical)")
    print("="*70)
    
    result = wrapper.answer(
        query="Comment déployer une application en production ?",
        k=3,
        triad_target_mode="concrete",
    )
    
    print(f"\n📊 Question Triad: Δ={result['triad_question']['delta']:.2f}, "
          f"∞={result['triad_question']['infinity']:.2f}, "
          f"Θ={result['triad_question']['theta']:.2f}")
    print(f"🎯 Detected Style: {result['style']}")
    print(f"\n📄 Answer:\n{result['answer']}")
    print(f"\n📚 Retrieved {result['metadata']['num_documents']} documents")

    # ============================================================================
    # 6. Abstract Query
    # ============================================================================
    
    print("\n" + "="*70)
    print("🔍 TEST 2: Abstract Query (Theoretical)")
    print("="*70)
    
    result = wrapper.answer(
        query="Qu'est-ce que l'intelligence artificielle générale ?",
        k=3,
        triad_target_mode="abstract",
    )
    
    print(f"\n📊 Question Triad: Δ={result['triad_question']['delta']:.2f}, "
          f"∞={result['triad_question']['infinity']:.2f}, "
          f"Θ={result['triad_question']['theta']:.2f}")
    print(f"🎯 Detected Style: {result['style']}")
    print(f"\n📄 Answer:\n{result['answer']}")
    print(f"\n📚 Retrieved {result['metadata']['num_documents']} documents")

    # ============================================================================
    # 7. Balanced Query
    # ============================================================================
    
    print("\n" + "="*70)
    print("🔍 TEST 3: Balanced Query")
    print("="*70)
    
    result = wrapper.answer(
        query="Qu'est-ce qu'un algorithme efficace ?",
        k=3,
        triad_target_mode="balanced",
    )
    
    print(f"\n📊 Question Triad: Δ={result['triad_question']['delta']:.2f}, "
          f"∞={result['triad_question']['infinity']:.2f}, "
          f"Θ={result['triad_question']['theta']:.2f}")
    print(f"🎯 Detected Style: {result['style']}")
    print(f"\n📄 Answer:\n{result['answer']}")
    print(f"\n📚 Retrieved {result['metadata']['num_documents']} documents")

    # ============================================================================
    # 8. Auto Query
    # ============================================================================
    
    print("\n" + "="*70)
    print("🔍 TEST 4: Auto Query (Natural)")
    print("="*70)
    
    result = wrapper.answer(
        query="Comment utiliser Docker ?",
        k=3,
        triad_target_mode="auto",
    )
    
    print(f"\n📊 Question Triad: Δ={result['triad_question']['delta']:.2f}, "
          f"∞={result['triad_question']['infinity']:.2f}, "
          f"Θ={result['triad_question']['theta']:.2f}")
    print(f"🎯 Detected Style: {result['style']}")
    print(f"\n📄 Answer:\n{result['answer']}")
    print(f"\n📚 Retrieved {result['metadata']['num_documents']} documents")

    # ============================================================================
    # 9. Statistics
    # ============================================================================
    
    print("\n" + "="*70)
    print("📊 System Statistics")
    print("="*70)
    
    stats = wrapper.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "="*70)
    print("✅ Example completed!")
    print("="*70)


if __name__ == "__main__":
    main()
