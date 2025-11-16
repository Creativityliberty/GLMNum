"""
∆∞Ο Embedding System for GLM v3.0
==================================

Minimal implementation of triadic embedding scores:
- ∆ (Delta): Complexity/Granularity (0-1)
- ∞ (Omega): Generality/Transformability (0-1) 
- Ο (Theta): Concreteness/Spatiality (0-1)

Integrates with existing GLM domains to enhance symbolic representations.
"""

import re
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class DeltaOmegaThetaScores:
    """Triadic embedding scores for conceptual analysis."""
    delta: float    # ∆ - complexity/granularity
    omega: float    # ∞ - generality/transformability  
    theta: float    # Ο - concreteness/spatiality
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for metadata storage."""
        return {
            "delta_score": self.delta,
            "omega_score": self.omega, 
            "theta_score": self.theta
        }
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for computations."""
        return np.array([self.delta, self.omega, self.theta])
    
    def distance(self, other: 'DeltaOmegaThetaScores') -> float:
        """L1 distance between triadic scores."""
        return float(np.sum(np.abs(self.to_array() - other.to_array())))

class DeltaOmegaThetaComputer:
    """Computes ∆∞Ο scores using minimal heuristics."""
    
    # Minimal term sets for scoring
    GENERAL_TERMS = {
        "intelligence", "énergie", "temps", "espace", "valeur", "système",
        "information", "relation", "transformation", "concept", "abstraction",
        "théorie", "modèle", "structure", "principe", "loi", "méthode"
    }
    
    CONCRETE_TERMS = {
        "machine", "capteur", "bâtiment", "voiture", "ordinateur", "serveur",
        "ville", "robot", "kg", "mètre", "euro", "usd", "donnée", "code"
    }
    
    LOGIC_CONNECTORS = {
        "donc", "tandis", "cependant", "néanmoins", "pourtant",
        "ainsi", "mais", "alors", "parce", "car", "si", "alors"
    }
    
    @staticmethod
    def tokenize(text: str) -> list:
        """Simple tokenization for scoring."""
        return re.findall(r"\w+", text.lower())
    
    @staticmethod
    def compute_delta(text: str) -> float:
        """∆: Complexity score based on length, sentences, and logic."""
        tokens = DeltaOmegaThetaComputer.tokenize(text)
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        
        # Complexity indicators
        n_tokens = len(tokens)
        n_sentences = len(sentences)
        n_connectors = sum(1 for t in tokens if t in DeltaOmegaThetaComputer.LOGIC_CONNECTORS)
        
        # Normalize to [0,1]
        raw = (n_tokens / 50.0) + (n_sentences / 5.0) + (n_connectors / 5.0)
        return float(min(1.0, raw))
    
    @staticmethod  
    def compute_omega(text: str) -> float:
        """∞: Generality score based on abstract terms."""
        tokens = DeltaOmegaThetaComputer.tokenize(text)
        if not tokens:
            return 0.0
        
        general_hits = sum(1 for t in tokens if t in DeltaOmegaThetaComputer.GENERAL_TERMS)
        ratio = general_hits / len(tokens)
        
        # Stretch: 10% general terms = high generality
        stretched = ratio * 10.0
        return float(min(1.0, stretched))
    
    @staticmethod
    def compute_theta(text: str) -> float:
        """Ο: Concreteness score based on numbers and concrete terms."""
        tokens = DeltaOmegaThetaComputer.tokenize(text)
        
        # Numbers and concrete indicators
        n_numbers = sum(1 for t in tokens if re.match(r"^\d+([.,]\d+)?$", t))
        concrete_hits = sum(1 for t in tokens if t in DeltaOmegaThetaComputer.CONCRETE_TERMS)
        
        raw = (n_numbers / 5.0) + (concrete_hits / 5.0)
        return float(min(1.0, raw))
    
    @classmethod
    def compute_scores(cls, text: str) -> DeltaOmegaThetaScores:
        """Compute all ∆∞Ο scores for given text."""
        return DeltaOmegaThetaScores(
            delta=cls.compute_delta(text),
            omega=cls.compute_omega(text),
            theta=cls.compute_theta(text)
        )

def compute_dio_scores(text: str) -> DeltaOmegaThetaScores:
    """Convenience function for score computation."""
    return DeltaOmegaThetaComputer.compute_scores(text)

# Integration utilities for GLM domains
def enhance_symbolic_metadata(metadata: Dict[str, Any], text: str) -> Dict[str, Any]:
    """Add ∆∞Ο scores to existing symbolic metadata."""
    scores = compute_dio_scores(text)
    metadata.update(scores.to_dict())
    return metadata

def dio_distance(emb1: Dict[str, Any], emb2: Dict[str, Any]) -> Optional[float]:
    """Compute ∆∞Ο distance between two metadata-enhanced embeddings."""
    try:
        scores1 = DeltaOmegaThetaScores(
            delta=emb1.get("delta_score", 0),
            omega=emb1.get("omega_score", 0), 
            theta=emb1.get("theta_score", 0)
        )
        scores2 = DeltaOmegaThetaScores(
            delta=emb2.get("delta_score", 0),
            omega=emb2.get("omega_score", 0),
            theta=emb2.get("theta_score", 0)
        )
        return scores1.distance(scores2)
    except Exception:
        return None

if __name__ == "__main__":
    # Quick demo
    text_a = "L'intelligence est la capacité générale de transformation de concepts dans un système."
    text_b = "Ce robot utilise des capteurs, des moteurs et un ordinateur pour se déplacer dans un bâtiment."
    
    scores_a = compute_dio_scores(text_a)
    scores_b = compute_dio_scores(text_b)
    
    print("∆∞Ο Demo:")
    print(f"Abstract: ∆={scores_a.delta:.2f}, ∞={scores_a.omega:.2f}, Ο={scores_a.theta:.2f}")
    print(f"Concrete: ∆={scores_b.delta:.2f}, ∞={scores_b.omega:.2f}, Ο={scores_b.theta:.2f}")
    print(f"Distance: {scores_a.distance(scores_b):.3f}")
