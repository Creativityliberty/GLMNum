"""
NumTriad Encoder Wrapper
========================

Unified interface for NumTriad embeddings (V2, V3, V4).
Provides text encoding with triad extraction.

This wrapper abstracts the underlying model and provides:
- Text encoding to embeddings
- Triad extraction (∆, ∞, Θ)
- Fallback mechanisms
"""

import logging
from typing import List, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class NumTriadEncoder:
    """
    Wrapper around NumTriadEmbeddingV3 / DeepTriadCoreEncoder.
    
    Provides unified interface for encoding text with triad extraction.
    """
    
    def __init__(
        self,
        model_name: str = "numtriad-v3",
        embedding_dim: int = 384,
        device: str = "cpu"
    ):
        """
        Initialize NumTriad encoder.
        
        Args:
            model_name: Model identifier ("numtriad-v2", "numtriad-v3", "numtriad-v4")
            embedding_dim: Embedding dimension
            device: Device to use ("cpu" or "cuda")
        """
        self.model_name = model_name
        self.embedding_dim = embedding_dim
        self.device = device
        self.triad_dim = 3
        
        # Try to load actual model
        self.model = None
        self._load_model()
        
        logger.info(f"NumTriadEncoder initialized: {model_name} (dim={embedding_dim})")
    
    def _load_model(self) -> None:
        """Load the actual NumTriad model if available"""
        try:
            if self.model_name == "numtriad-v3":
                # Try to import and load NumTriadEmbeddingV3
                try:
                    from numtriad.encoders.numtriad_v3_multimodal import NumTriadEmbeddingV3
                    self.model = NumTriadEmbeddingV3(device=self.device)
                    logger.info("✅ Loaded NumTriadEmbeddingV3")
                except ImportError:
                    logger.warning("NumTriadEmbeddingV3 not available, using mock")
                    self.model = None
            
            elif self.model_name == "numtriad-v2":
                # Try to import and load NumTriadEmbeddingV2
                try:
                    from numtriad.encoders.numtriad_v2_text import NumTriadEmbeddingV2
                    self.model = NumTriadEmbeddingV2(device=self.device)
                    logger.info("✅ Loaded NumTriadEmbeddingV2")
                except ImportError:
                    logger.warning("NumTriadEmbeddingV2 not available, using mock")
                    self.model = None
            
            else:
                logger.warning(f"Unknown model: {self.model_name}, using mock")
                self.model = None
        
        except Exception as e:
            logger.warning(f"Failed to load model: {e}, using mock")
            self.model = None
    
    def encode_text(
        self,
        texts: List[str]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Encode texts to embeddings and extract triads.
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            embeddings: (N, embedding_dim) array of embeddings
            triads: (N, 3) array of [∆̂, ∞̂, Θ̂] scores
        """
        n = len(texts)
        
        if self.model is not None:
            try:
                # Use actual model
                embeddings, triads = self._encode_with_model(texts)
                return embeddings, triads
            except Exception as e:
                logger.warning(f"Model encoding failed: {e}, falling back to mock")
        
        # Fallback: mock encoding
        return self._encode_mock(texts)
    
    def _encode_with_model(
        self,
        texts: List[str]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Encode using actual model"""
        try:
            # Try to use the model's encode method
            if hasattr(self.model, 'encode_text'):
                result = self.model.encode_text(texts)
                
                # Extract embeddings and triads from result
                if isinstance(result, tuple) and len(result) == 2:
                    embeddings, triads = result
                    return embeddings, triads
                else:
                    # Assume result is embeddings, extract triads separately
                    embeddings = result
                    triads = self._extract_triads_from_embeddings(embeddings)
                    return embeddings, triads
            
            # Fallback to generic encode
            elif hasattr(self.model, 'encode'):
                embeddings = self.model.encode(texts)
                triads = self._extract_triads_from_embeddings(embeddings)
                return embeddings, triads
            
            else:
                raise AttributeError("Model has no encode method")
        
        except Exception as e:
            logger.warning(f"Model encoding error: {e}")
            raise
    
    def _extract_triads_from_embeddings(
        self,
        embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Extract triad scores from embeddings.
        
        Simple heuristic: use embedding statistics to estimate triads.
        """
        n = len(embeddings)
        triads = np.zeros((n, 3), dtype=np.float32)
        
        for i, emb in enumerate(embeddings):
            # Heuristic: use embedding statistics
            # ∆ (Delta): variance (specificity)
            delta = float(np.var(emb))
            
            # ∞ (Infinity): mean absolute value (generality)
            infty = float(np.mean(np.abs(emb)))
            
            # Θ (Theta): norm (context/magnitude)
            theta = float(np.linalg.norm(emb))
            
            # Normalize to [0, 1]
            total = delta + infty + theta + 1e-8
            triads[i] = np.array([delta, infty, theta], dtype=np.float32) / total
        
        return triads
    
    def _encode_mock(
        self,
        texts: List[str]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Mock encoding for when model is not available.
        
        Returns reasonable default embeddings and neutral triads.
        """
        n = len(texts)
        
        # Generate mock embeddings (deterministic based on text)
        embeddings = np.zeros((n, self.embedding_dim), dtype=np.float32)
        triads = np.zeros((n, 3), dtype=np.float32)
        
        for i, text in enumerate(texts):
            # Deterministic mock embedding based on text hash
            seed = hash(text) % (2**31)
            np.random.seed(seed)
            embeddings[i] = np.random.randn(self.embedding_dim).astype(np.float32)
            
            # Normalize embedding
            norm = np.linalg.norm(embeddings[i])
            if norm > 0:
                embeddings[i] /= norm
            
            # Mock triads: analyze text to estimate triads
            triads[i] = self._analyze_text_for_triads(text)
        
        return embeddings, triads
    
    def _analyze_text_for_triads(self, text: str) -> np.ndarray:
        """
        Analyze text to estimate triad scores.
        
        Heuristic:
        - ∆ (Delta): Specificity based on unique words
        - ∞ (Infinity): Generality based on common words
        - Θ (Theta): Context based on text length
        """
        words = text.lower().split()
        
        if not words:
            return np.array([1/3, 1/3, 1/3], dtype=np.float32)
        
        # Common words (low specificity)
        common_words = {
            "the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
            "be", "been", "being", "have", "has", "had", "do", "does", "did",
            "will", "would", "could", "should", "may", "might", "must", "can"
        }
        
        # Count unique words (specificity)
        unique_words = len(set(words))
        specificity = min(unique_words / len(words), 1.0)
        
        # Count common words (generality)
        common_count = sum(1 for w in words if w in common_words)
        generality = min(common_count / len(words), 1.0)
        
        # Text length (context)
        context = min(len(text) / 100.0, 1.0)
        
        # Normalize
        total = specificity + generality + context + 1e-8
        triads = np.array([specificity, generality, context], dtype=np.float32) / total
        
        return triads
    
    def encode_batch(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Encode texts in batches.
        
        Args:
            texts: List of texts to encode
            batch_size: Batch size for processing
            
        Returns:
            embeddings: (N, embedding_dim)
            triads: (N, 3)
        """
        all_embeddings = []
        all_triads = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            emb, tri = self.encode_text(batch)
            all_embeddings.append(emb)
            all_triads.append(tri)
        
        embeddings = np.vstack(all_embeddings)
        triads = np.vstack(all_triads)
        
        return embeddings, triads
    
    def get_config(self) -> dict:
        """Get encoder configuration"""
        return {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "triad_dim": self.triad_dim,
            "device": self.device,
            "model_available": self.model is not None,
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    encoder = NumTriadEncoder(model_name="numtriad-v3")
    
    texts = [
        "This is a DNA sequence: ATCG",
        "Kubernetes is a container orchestration platform",
        "Machine learning is a subset of artificial intelligence"
    ]
    
    embeddings, triads = encoder.encode_text(texts)
    
    print(f"\n✅ Encoded {len(texts)} texts")
    print(f"Embeddings shape: {embeddings.shape}")
    print(f"Triads shape: {triads.shape}")
    print(f"\nTriads (∆, ∞, Θ):")
    for i, (text, triad) in enumerate(zip(texts, triads)):
        print(f"  {i+1}. {text[:40]}...")
        print(f"     ∆={triad[0]:.3f}, ∞={triad[1]:.3f}, Θ={triad[2]:.3f}")
