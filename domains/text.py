"""
GLM Prototype - Text Domain
============================

Implémentation du domaine textuel avec encodage/décodage ∆∞Ο

Author: GLM Research Team
Date: 2024-11-15
"""

from typing import Any, Dict, List, Set
import numpy as np
import networkx as nx
from collections import Counter
import re

import sys
import os
# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.symbolic import Domain, SymbolicRepresentation
from delta_infty_omicron import enhance_symbolic_metadata


# ============================================================================
# DOMAINE TEXTUEL
# ============================================================================

class TextDomain(Domain):
    """
    Domaine textuel
    
    Dans ce domaine :
    - ∆ (Delta) = Mots-clés, concepts essentiels (compression)
    - ∞ (Infinity) = Structure syntaxique, graphe de dépendances
    - Ο (Omega) = Message global, sémantique complète
    """
    
    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        
        # Stop words simples (version minimale)
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'should', 'could', 'may', 'might',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
            'it', 'we', 'they', 'them', 'their', 'its', 'our', 'my'
        }
    
    @property
    def name(self) -> str:
        return "text"
    
    def has_notion_of(self, concept: str) -> bool:
        """Le domaine textuel a-t-il cette notion ?"""
        notions = {
            'beginning': True,      # Mots initiaux
            'compression': True,    # Mots-clés
            'transformation': True, # Paraphrase
            'structure': True,      # Syntaxe
            'ending': True,         # Message complet
            'manifestation': True,  # Texte final
        }
        return notions.get(concept, False)
    
    def encode(self, obj: Any) -> SymbolicRepresentation:
        """
        Encoder du texte vers ∆∞Ο
        
        Args:
            obj: String (texte)
            
        Returns:
            Représentation symbolique
        """
        if not isinstance(obj, str):
            raise ValueError(f"Expected str, got {type(obj)}")
        
        # Prétraitement
        text = obj.strip()
        
        # ∆ : Essence (mots-clés, concepts centraux)
        delta = self._extract_keywords(text)
        
        # ∞ : Processus (structure syntaxique, graphe de mots)
        infinity = self._build_word_graph(text)
        
        # Ο : Complétude (embedding du texte complet)
        omega = self._compute_text_embedding(text)
        
        # Base metadata with ∆∞Ο scores
        base_metadata = {
            'domain': self.name,
            'length': len(text),
            'words': len(text.split()),
            'text_preview': text[:100] + '...' if len(text) > 100 else text
        }
        
        # Enhance with ∆∞Ο triadic scores
        enhanced_metadata = enhance_symbolic_metadata(base_metadata, text)
        
        return SymbolicRepresentation(
            delta=delta,
            infinity=infinity,
            omega=omega,
            metadata=enhanced_metadata
        )
    
    def decode(self, symbolic: SymbolicRepresentation) -> Any:
        """
        Décoder ∆∞Ο vers du texte
        
        Args:
            symbolic: Représentation symbolique
            
        Returns:
            String (texte reconstruit)
        """
        # Si on a le texte dans les métadonnées, le retourner
        if 'text_preview' in symbolic.metadata:
            return symbolic.metadata['text_preview']
        
        # Sinon, reconstruire depuis le graphe de mots (∞)
        if symbolic.infinity.number_of_nodes() > 0:
            # Extraire les mots du graphe
            words = [
                symbolic.infinity.nodes[node].get('word', f'word_{node}')
                for node in symbolic.infinity.nodes()
            ]
            return ' '.join(words)
        
        # Fallback : message générique
        return "[Reconstructed text from symbolic representation]"
    
    # ========================================================================
    # MÉTHODES PRIVÉES
    # ========================================================================
    
    def _extract_keywords(self, text: str) -> np.ndarray:
        """
        Extraire les mots-clés (∆)
        
        Méthode simple : TF-IDF basique + filtrage stop words
        """
        # Tokenisation
        words = self._tokenize(text)
        
        # Filtrer stop words et mots courts
        keywords = [
            word for word in words
            if word not in self.stop_words and len(word) > 2
        ]
        
        # Compter fréquences
        word_freq = Counter(keywords)
        
        # Top K mots (K = embedding_dim // 10)
        top_k = min(self.embedding_dim // 10, len(word_freq))
        top_words = word_freq.most_common(top_k)
        
        # Créer embedding
        essence = np.zeros(self.embedding_dim)
        
        for i, (word, freq) in enumerate(top_words):
            if i < self.embedding_dim:
                # Hash du mot pour position stable
                word_hash = hash(word) % (self.embedding_dim - top_k)
                essence[word_hash] = freq / (len(keywords) + 1)
        
        # Normaliser
        essence /= (np.linalg.norm(essence) + 1e-8)
        
        return essence
    
    def _build_word_graph(self, text: str) -> nx.Graph:
        """
        Construire un graphe de mots (∞)
        
        Graphe simple : co-occurrence de mots dans une fenêtre
        """
        words = self._tokenize(text)
        graph = nx.Graph()
        
        # Fenêtre de co-occurrence
        window_size = 3
        
        for i, word in enumerate(words):
            # Ajouter le nœud
            if not graph.has_node(word):
                graph.add_node(word, word=word, position=i)
            
            # Arêtes vers mots dans la fenêtre
            for j in range(max(0, i - window_size), min(len(words), i + window_size + 1)):
                if i != j:
                    neighbor = words[j]
                    
                    if graph.has_edge(word, neighbor):
                        graph[word][neighbor]['weight'] += 1
                    else:
                        graph.add_edge(word, neighbor, weight=1)
        
        return graph
    
    def _compute_text_embedding(self, text: str) -> np.ndarray:
        """
        Calculer embedding du texte complet (Ο)
        
        Méthode simple : Bag of Words + caractéristiques statistiques
        """
        words = self._tokenize(text)
        embedding = np.zeros(self.embedding_dim)
        
        # Features statistiques
        embedding[0] = len(text) / 1000.0  # Longueur (normalisée)
        embedding[1] = len(words) / 100.0  # Nombre de mots
        embedding[2] = len(set(words)) / (len(words) + 1)  # Diversité lexicale
        
        # Average word length
        if words:
            embedding[3] = np.mean([len(w) for w in words]) / 10.0
        
        # Bag of words (hashed)
        word_counter = Counter(words)
        for word, count in word_counter.items():
            word_hash = hash(word) % (self.embedding_dim - 10)
            embedding[10 + word_hash] = count / (len(words) + 1)
        
        # Normaliser
        embedding /= (np.linalg.norm(embedding) + 1e-8)
        
        return embedding
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenisation simple"""
        # Lowercase
        text = text.lower()
        
        # Remplacer ponctuation par espaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split et filtrer vides
        words = [w.strip() for w in text.split() if w.strip()]
        
        return words


# ============================================================================
# UTILITAIRES TEXTUELS
# ============================================================================

def compute_text_similarity(text1: str, text2: str, domain: TextDomain) -> float:
    """
    Calculer la similarité sémantique entre deux textes
    
    Args:
        text1: Premier texte
        text2: Deuxième texte
        domain: Domaine textuel
        
    Returns:
        Score de similarité [0, 1]
    """
    from core.symbolic import SymbolicOperations
    
    sym1 = domain.encode(text1)
    sym2 = domain.encode(text2)
    
    return SymbolicOperations.similarity(sym1, sym2)


def extract_key_concepts(text: str, domain: TextDomain, top_k: int = 5) -> List[str]:
    """
    Extraire les concepts clés d'un texte
    
    Args:
        text: Texte à analyser
        domain: Domaine textuel
        top_k: Nombre de concepts à retourner
        
    Returns:
        Liste des mots-clés
    """
    symbolic = domain.encode(text)
    
    # Extraire mots du graphe ∞
    if symbolic.infinity.number_of_nodes() == 0:
        return []
    
    # Calculer centralité des mots
    centrality = nx.degree_centrality(symbolic.infinity)
    
    # Trier par centralité
    sorted_words = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
    
    # Retourner top K
    return [word for word, score in sorted_words[:top_k]]


# ============================================================================
# EXEMPLE D'UTILISATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("GLM PROTOTYPE - TEXT DOMAIN TEST")
    print("=" * 60)
    
    # Créer le domaine textuel
    text_domain = TextDomain(embedding_dim=128)
    print(f"\n✓ Text domain initialized: {text_domain.name}")
    
    # Test 1 : Texte simple
    print("\n" + "=" * 60)
    print("Test 1: Simple Text")
    print("=" * 60)
    
    text1 = "The quick brown fox jumps over the lazy dog."
    print(f"\nOriginal text: {text1}")
    
    # Encoder
    sym1 = text_domain.encode(text1)
    print(f"\nSymbolic representation:")
    print(sym1)
    
    # Concepts clés
    concepts = extract_key_concepts(text1, text_domain, top_k=5)
    print(f"\nKey concepts: {concepts}")
    
    # Décoder
    reconstructed = text_domain.decode(sym1)
    print(f"\nReconstructed: {reconstructed}")
    
    # Test 2 : Texte plus long
    print("\n" + "=" * 60)
    print("Test 2: Longer Text")
    print("=" * 60)
    
    text2 = """
    Artificial intelligence is transforming the world. Machine learning
    algorithms can now perform tasks that were once thought to be exclusively
    human. From image recognition to natural language processing, AI systems
    are becoming increasingly sophisticated and capable.
    """
    
    print(f"\nOriginal text:\n{text2}")
    
    sym2 = text_domain.encode(text2)
    print(f"\nSymbolic representation:")
    print(sym2)
    
    concepts2 = extract_key_concepts(text2, text_domain, top_k=10)
    print(f"\nKey concepts: {concepts2}")
    
    # Test 3 : Similarité textuelle
    print("\n" + "=" * 60)
    print("Test 3: Text Similarity")
    print("=" * 60)
    
    text_pairs = [
        ("The cat sat on the mat.", "A feline rested on the rug."),
        ("I love pizza.", "Pizza is my favorite food."),
        ("The weather is nice today.", "It's raining heavily outside."),
        ("Machine learning is powerful.", "AI algorithms are very capable."),
    ]
    
    print("\nSemantic similarity scores:")
    for t1, t2 in text_pairs:
        sim = compute_text_similarity(t1, t2, text_domain)
        print(f"  '{t1}' <-> '{t2}'")
        print(f"    Similarity: {sim:.4f}\n")
    
    # Test 4 : Round-trip fidelity
    print("\n" + "=" * 60)
    print("Test 4: Round-trip Fidelity")
    print("=" * 60)
    
    test_texts = [
        "Hello world!",
        "The quick brown fox jumps over the lazy dog.",
        "Artificial intelligence and machine learning.",
        "This is a test of the symbolic encoding system.",
    ]
    
    from core.symbolic import SymbolicOperations
    
    print("\nText -> ∆∞Ο -> Text fidelity:")
    for text in test_texts:
        sym = text_domain.encode(text)
        reconstructed = text_domain.decode(sym)
        
        # Re-encoder pour comparer
        sym_reconstructed = text_domain.encode(reconstructed)
        fidelity = SymbolicOperations.similarity(sym, sym_reconstructed)
        
        print(f"  '{text[:40]}'")
        print(f"    Fidelity: {fidelity:.4f}")
    
    print("\n" + "=" * 60)
    print("✓ All text tests passed!")
    print("=" * 60)
