"""
GLM Prototype - Neural Encoders with Nomic Embed
=================================================

High-quality neural embeddings using Nomic Embed models

Author: GLM Research Team
Date: 2024-11-15

Usage:
    from encoders.neural import NomicTextEncoder, NomicImageEncoder
    
    text_encoder = NomicTextEncoder()
    embedding = text_encoder.encode("Hello world")
    
    image_encoder = NomicImageEncoder()
    embedding = image_encoder.encode(image_array)
"""

import numpy as np
from typing import Union, List, Optional
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Optional imports
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# ============================================================================
# NOMIC TEXT ENCODER
# ============================================================================

class NomicTextEncoder:
    """
    High-quality text encoder using Nomic Embed
    
    Nomic Embed is a lightweight, efficient text embedding model
    that provides excellent semantic understanding.
    
    Model: nomic-ai/nomic-embed-text-v1
    Embedding dimension: 768
    """
    
    def __init__(self, embedding_dim: int = 768, use_gpu: bool = False):
        """
        Initialize Nomic Text Encoder
        
        Args:
            embedding_dim: Output embedding dimension (768 or 384)
            use_gpu: Whether to use GPU if available
        """
        self.embedding_dim = embedding_dim
        self.use_gpu = use_gpu and HAS_TORCH and torch.cuda.is_available()
        self.model = None
        self.device = 'cuda' if self.use_gpu else 'cpu'
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Nomic Embed model"""
        if not HAS_SENTENCE_TRANSFORMERS:
            print("⚠️  sentence-transformers not installed. Using fallback encoder.")
            self.model = None
            return
        
        try:
            print(f"📦 Loading Nomic Embed Text model (device: {self.device})...")
            
            # Use Nomic Embed model (or fallback to all-MiniLM if not available)
            try:
                self.model = SentenceTransformer(
                    'nomic-ai/nomic-embed-text-v1.5',
                    device=self.device,
                    trust_remote_code=True
                )
                print("✓ Nomic Embed Text model loaded successfully")
            except Exception as nomic_error:
                print(f"⚠️  Nomic model not available: {nomic_error}")
                print("📦 Loading all-MiniLM-L6-v2 as fallback...")
                self.model = SentenceTransformer(
                    'sentence-transformers/all-MiniLM-L6-v2',
                    device=self.device
                )
                print("✓ all-MiniLM-L6-v2 model loaded successfully")
        except Exception as e:
            print(f"⚠️  Error loading model: {e}")
            print("Using hash-based fallback encoder...")
            self.model = None
    
    def encode(self, text: Union[str, List[str]], 
               normalize: bool = True) -> np.ndarray:
        """
        Encode text to embedding
        
        Args:
            text: Text string or list of strings
            normalize: Whether to normalize the embedding
        
        Returns:
            Embedding vector(s)
        """
        if isinstance(text, str):
            text = [text]
            squeeze = True
        else:
            squeeze = False
        
        if self.model is not None:
            try:
                # Use Nomic Embed
                embeddings = self.model.encode(
                    text,
                    convert_to_numpy=True,
                    show_progress_bar=False
                )
            except Exception as e:
                print(f"Error encoding with Nomic: {e}")
                embeddings = self._fallback_encode(text)
        else:
            embeddings = self._fallback_encode(text)
        
        # Normalize if requested
        if normalize:
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / (norms + 1e-8)
        
        # Resize to target dimension if needed
        if embeddings.shape[1] != self.embedding_dim:
            embeddings = self._resize_embedding(embeddings)
        
        return embeddings[0] if squeeze else embeddings
    
    def _fallback_encode(self, texts: List[str]) -> np.ndarray:
        """Fallback encoding using simple TF-IDF"""
        embeddings = []
        
        for text in texts:
            # Simple hash-based embedding
            words = text.lower().split()
            embedding = np.zeros(self.embedding_dim)
            
            for i, word in enumerate(words[:self.embedding_dim]):
                # Use hash to generate deterministic values
                hash_val = hash(word) % 1000
                embedding[i] = hash_val / 1000.0
            
            # Normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            embeddings.append(embedding)
        
        return np.array(embeddings)
    
    def _resize_embedding(self, embeddings: np.ndarray) -> np.ndarray:
        """Resize embeddings to target dimension"""
        current_dim = embeddings.shape[1]
        
        if current_dim > self.embedding_dim:
            # Reduce by averaging
            chunk_size = current_dim // self.embedding_dim
            resized = []
            for emb in embeddings:
                chunks = [
                    emb[i*chunk_size:(i+1)*chunk_size].mean()
                    for i in range(self.embedding_dim)
                ]
                resized.append(np.array(chunks))
            return np.array(resized)
        else:
            # Expand by padding
            resized = np.zeros((embeddings.shape[0], self.embedding_dim))
            resized[:, :current_dim] = embeddings
            return resized


# ============================================================================
# NOMIC IMAGE ENCODER
# ============================================================================

class NomicImageEncoder:
    """
    High-quality image encoder using Nomic Embed Vision
    
    Encodes images to semantic embeddings using vision transformers
    
    Model: nomic-ai/nomic-embed-vision-v1
    Embedding dimension: 768
    """
    
    def __init__(self, embedding_dim: int = 768, use_gpu: bool = False):
        """
        Initialize Nomic Image Encoder
        
        Args:
            embedding_dim: Output embedding dimension
            use_gpu: Whether to use GPU if available
        """
        self.embedding_dim = embedding_dim
        self.use_gpu = use_gpu and HAS_TORCH and torch.cuda.is_available()
        self.model = None
        self.device = 'cuda' if self.use_gpu else 'cpu'
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Nomic Image model"""
        if not HAS_SENTENCE_TRANSFORMERS:
            print("⚠️  sentence-transformers not installed. Using fallback encoder.")
            self.model = None
            return
        
        try:
            print(f"📦 Loading Nomic Embed Vision model (device: {self.device})...")
            
            # Use Nomic Embed Vision model (or fallback to clip-vit if not available)
            try:
                self.model = SentenceTransformer(
                    'nomic-ai/nomic-embed-vision-v1.5',
                    device=self.device,
                    trust_remote_code=True
                )
                print("✓ Nomic Embed Vision model loaded successfully")
            except Exception as nomic_error:
                print(f"⚠️  Nomic Vision model not available: {nomic_error}")
                print("📦 Loading clip-ViT-B-32 as fallback...")
                self.model = SentenceTransformer(
                    'sentence-transformers/clip-ViT-B-32',
                    device=self.device
                )
                print("✓ clip-ViT-B-32 model loaded successfully")
        except Exception as e:
            print(f"⚠️  Error loading model: {e}")
            print("Using array-based fallback encoder...")
            self.model = None
    
    def encode(self, image, normalize: bool = True) -> np.ndarray:
        """
        Encode image to embedding
        
        Args:
            image: PIL Image or numpy array
            normalize: Whether to normalize the embedding
        
        Returns:
            Embedding vector
        """
        # Convert to PIL Image if needed
        if isinstance(image, np.ndarray):
            if HAS_PIL:
                image = Image.fromarray(image.astype('uint8'))
            else:
                # Fallback: use array directly
                return self._fallback_encode_image(image, normalize)
        
        if self.model is not None:
            try:
                # Use Nomic Embed Vision
                embedding = self.model.encode(
                    image,
                    convert_to_numpy=True
                )
            except Exception as e:
                print(f"Error encoding with Nomic Vision: {e}")
                if isinstance(image, np.ndarray):
                    embedding = self._fallback_encode_image(image, normalize)
                else:
                    embedding = self._fallback_encode_image(np.array(image), normalize)
        else:
            if isinstance(image, np.ndarray):
                embedding = self._fallback_encode_image(image, normalize)
            else:
                embedding = self._fallback_encode_image(np.array(image), normalize)
        
        # Normalize if requested
        if normalize:
            norm = np.linalg.norm(embedding)
            embedding = embedding / (norm + 1e-8)
        
        # Resize to target dimension if needed
        if len(embedding.shape) > 1:
            embedding = embedding[0]
        
        if embedding.shape[0] != self.embedding_dim:
            embedding = self._resize_embedding(embedding)
        
        return embedding
    
    def _fallback_encode_image(self, image: np.ndarray, 
                               normalize: bool = True) -> np.ndarray:
        """Fallback image encoding using color histograms"""
        # Redimensionner
        if len(image.shape) == 3:
            h, w, c = image.shape
            resized = image[::max(1, h//32), ::max(1, w//32), :]
        else:
            resized = image[::max(1, image.shape[0]//32), ::max(1, image.shape[1]//32)]
        
        # Aplatir
        flat = resized.flatten().astype(np.float32) / 255.0
        
        # Redimensionner à embedding_dim
        if len(flat) > self.embedding_dim:
            chunk_size = len(flat) // self.embedding_dim
            embedding = np.array([
                flat[i*chunk_size:(i+1)*chunk_size].mean()
                for i in range(self.embedding_dim)
            ])
        else:
            embedding = np.zeros(self.embedding_dim)
            embedding[:len(flat)] = flat
        
        # Normaliser
        if normalize:
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
        
        return embedding
    
    def _resize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """Resize embedding to target dimension"""
        current_dim = embedding.shape[0]
        
        if current_dim > self.embedding_dim:
            # Reduce by averaging
            chunk_size = current_dim // self.embedding_dim
            resized = np.array([
                embedding[i*chunk_size:(i+1)*chunk_size].mean()
                for i in range(self.embedding_dim)
            ])
            return resized
        else:
            # Expand by padding
            resized = np.zeros(self.embedding_dim)
            resized[:current_dim] = embedding
            return resized


# ============================================================================
# TESTS
# ============================================================================

def test_nomic_encoders():
    """Test Nomic encoders"""
    print("\n" + "="*70)
    print("NOMIC EMBED ENCODERS TEST")
    print("="*70)
    
    # Test 1: Text Encoder
    print("\n" + "="*70)
    print("Test 1: Nomic Text Encoder")
    print("="*70)
    
    text_encoder = NomicTextEncoder(embedding_dim=768)
    
    texts = [
        "The quick brown fox jumps over the lazy dog",
        "A fast brown fox leaps over a sleeping dog",
        "Machine learning is transforming AI"
    ]
    
    print("\nEncoding texts...")
    embeddings = text_encoder.encode(texts)
    
    print(f"\nEmbeddings shape: {embeddings.shape}")
    print(f"Embedding 1 norm: {np.linalg.norm(embeddings[0]):.4f}")
    print(f"Embedding 2 norm: {np.linalg.norm(embeddings[1]):.4f}")
    print(f"Embedding 3 norm: {np.linalg.norm(embeddings[2]):.4f}")
    
    # Calculate similarities
    sim_1_2 = np.dot(embeddings[0], embeddings[1])
    sim_1_3 = np.dot(embeddings[0], embeddings[2])
    sim_2_3 = np.dot(embeddings[1], embeddings[2])
    
    print(f"\nSimilarities:")
    print(f"Text 1 vs Text 2: {sim_1_2:.4f} (similar sentences)")
    print(f"Text 1 vs Text 3: {sim_1_3:.4f} (different topics)")
    print(f"Text 2 vs Text 3: {sim_2_3:.4f} (different topics)")
    
    # Test 2: Image Encoder
    print("\n" + "="*70)
    print("Test 2: Nomic Image Encoder")
    print("="*70)
    
    image_encoder = NomicImageEncoder(embedding_dim=768)
    
    # Create test images
    print("\nCreating test images...")
    
    image1 = np.zeros((100, 100, 3), dtype=np.uint8)
    image1[20:80, 20:80] = [255, 0, 0]  # Red square
    
    image2 = np.zeros((100, 100, 3), dtype=np.uint8)
    image2[25:75, 25:75] = [255, 0, 0]  # Similar red square
    
    image3 = np.zeros((100, 100, 3), dtype=np.uint8)
    image3[:, :] = [0, 255, 0]  # Green background
    
    print("Encoding images...")
    emb1 = image_encoder.encode(image1)
    emb2 = image_encoder.encode(image2)
    emb3 = image_encoder.encode(image3)
    
    print(f"\nImage embeddings shape: {emb1.shape}")
    print(f"Image 1 norm: {np.linalg.norm(emb1):.4f}")
    print(f"Image 2 norm: {np.linalg.norm(emb2):.4f}")
    print(f"Image 3 norm: {np.linalg.norm(emb3):.4f}")
    
    # Calculate similarities
    sim_img_1_2 = np.dot(emb1, emb2)
    sim_img_1_3 = np.dot(emb1, emb3)
    sim_img_2_3 = np.dot(emb2, emb3)
    
    print(f"\nImage Similarities:")
    print(f"Image 1 vs Image 2: {sim_img_1_2:.4f} (similar red squares)")
    print(f"Image 1 vs Image 3: {sim_img_1_3:.4f} (different colors)")
    print(f"Image 2 vs Image 3: {sim_img_2_3:.4f} (different colors)")
    
    # Test 3: Cross-modal similarity
    print("\n" + "="*70)
    print("Test 3: Performance Comparison")
    print("="*70)
    
    import time
    
    # Text encoding speed
    start = time.time()
    for _ in range(10):
        text_encoder.encode("This is a test sentence for performance measurement")
    text_time = (time.time() - start) / 10
    
    # Image encoding speed
    test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    start = time.time()
    for _ in range(10):
        image_encoder.encode(test_img)
    image_time = (time.time() - start) / 10
    
    print(f"\nAverage encoding times:")
    print(f"Text: {text_time*1000:.2f}ms per sentence")
    print(f"Image: {image_time*1000:.2f}ms per image")
    
    print("\n" + "="*70)
    print("✓ All Nomic encoder tests completed!")
    print("="*70)


if __name__ == "__main__":
    test_nomic_encoders()
