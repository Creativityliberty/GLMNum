# numtriad/config.py

from dataclasses import dataclass


@dataclass
class NumTriadConfig:
    """
    Configuration globale pour NumTriad.
    Ajustable selon ton infra.
    """
    base_text_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    triad_hidden_dim: int = 256
    triad_dropout: float = 0.1
    device: str = "cpu"  # Auto-détection ou forcé CPU pour compatibilité
    use_linguistic_features: bool = True
    linguistic_feature_dim: int = 8  # ex: longueur, entropie, etc.
    alpha_semantic: float = 0.7      # poids cosine
    beta_triad: float = 0.3          # poids triad distance
