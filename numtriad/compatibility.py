# numtriad/compatibility.py

"""
Gestionnaire de compatibilité pour NumTriad.
Détecte la disponibilité des dépendances et offre des fallbacks.
"""

import sys
from typing import Optional

# Détection de disponibilité
TORCH_AVAILABLE = False
SENTENCE_TRANSFORMERS_AVAILABLE = False
SCIPY_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None

try:
    import sentence_transformers
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    sentence_transformers = None

try:
    import scipy
    SCIPY_AVAILABLE = True
except ImportError:
    scipy = None

def get_compatibility_status() -> dict:
    """Retourne le statut de compatibilité des dépendances."""
    return {
        "python_version": sys.version,
        "torch_available": TORCH_AVAILABLE,
        "sentence_transformers_available": SENTENCE_TRANSFORMERS_AVAILABLE,
        "scipy_available": SCIPY_AVAILABLE,
        "numtriad_mode": "neural" if TORCH_AVAILABLE and SENTENCE_TRANSFORMERS_AVAILABLE else "heuristic"
    }

def create_fallback_encoder():
    """
    Crée un encodeur fallback basé sur le système heuristique existant
    quand les dépendances neuronales ne sont pas disponibles.
    """
    if not TORCH_AVAILABLE or not SENTENCE_TRANSFORMERS_AVAILABLE:
        # Importer le système heuristique existant
        try:
            from delta_infty_omicron import compute_dio_scores
            return HeuristicFallbackEncoder(compute_dio_scores)
        except ImportError:
            return NoneEncoder()
    else:
        # Importer le système neuronal
        from .encoders.numtriad_text_v2 import NumTriadTextEncoderV2
        from .config import NumTriadConfig
        return NumTriadTextEncoderV2(NumTriadConfig())

class HeuristicFallbackEncoder:
    """Encodeur fallback utilisant le système heuristique ∆∞Ó existant."""
    
    def __init__(self, scoring_function):
        self.scoring_function = scoring_function
    
    def encode(self, texts, return_full=True):
        """Encode avec le système heuristique."""
        from .triad_types import Triad
        import numpy as np
        
        triads = []
        embeddings = []
        
        for text in texts:
            scores = self.scoring_function(text)
            # Le système heuristique retourne un dataclass DeltaOmegaThetaScores
            # Triad utilise 'infinity' pas 'omega'
            triad = Triad(
                delta=scores.delta,
                infinity=scores.omega, 
                theta=scores.theta
            )
            triads.append(triad)
            
            # Embedding simulé (basé sur features simples)
            emb = self._simple_embedding(text)
            embeddings.append(emb)
        
        if return_full:
            triad_arrays = np.stack([t.as_array() for t in triads])
            full_embeddings = np.concatenate([embeddings, triad_arrays], axis=-1)
        else:
            full_embeddings = embeddings
            
        return FallbackResult(full_embeddings, triads)
    
    def _simple_embedding(self, text):
        """Embedding simple basé sur des features de base."""
        import numpy as np
        # Features basiques: longueur, mots uniques, etc.
        words = text.lower().split()
        unique_words = set(words)
        
        features = [
            len(text) / 1000.0,  # longueur normalisée
            len(words) / 100.0,   # nombre de mots
            len(unique_words) / 100.0,  # diversité lexicale
            text.count('.') / 10.0,     # ponctuation
            sum(c.isdigit() for c in text) / 10.0,  # chiffres
        ]
        return np.array(features, dtype=float)

class NoneEncoder:
    """Encodeur neutre quand aucune dépendance n'est disponible."""
    
    def encode(self, texts, return_full=True):
        """Retourne des embeddings nuls."""
        from .triad_types import Triad
        import numpy as np
        
        triads = [Triad(delta=0.33, omega=0.33, theta=0.34) for _ in texts]
        embeddings = np.zeros((len(texts), 5))  # 5 features basiques
        
        if return_full:
            triad_arrays = np.stack([t.as_array() for t in triads])
            full_embeddings = np.concatenate([embeddings, triad_arrays], axis=-1)
        else:
            full_embeddings = embeddings
            
        return FallbackResult(full_embeddings, triads)

class FallbackResult:
    """Résultat compatible avec NumTriadTextEmbeddingV2."""
    
    def __init__(self, embeddings, triads):
        self.embeddings = embeddings
        self.triads = triads
        self.meta = {"mode": "fallback"}

def get_encoder():
    """Retourne le meilleur encodeur disponible."""
    encoder = create_fallback_encoder()
    print(f"🔧 NumTriad mode: {get_compatibility_status()['numtriad_mode']}")
    return encoder
