"""
GLM Prototype - Neural Encoder Integration
===========================================

Integration of Nomic encoders with GLM domains

Author: GLM Research Team
Date: 2024-11-15

Usage:
    from encoders.integration import enhance_text_domain, enhance_image_domain
    
    # Enhance existing domains with neural encoders
    enhanced_text = enhance_text_domain(text_domain)
    enhanced_image = enhance_image_domain(image_domain)
"""

import numpy as np
from typing import Optional, Any
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.symbolic import Domain, SymbolicRepresentation
from encoders.neural import NomicTextEncoder, NomicImageEncoder


# ============================================================================
# ENHANCED TEXT DOMAIN WITH NOMIC
# ============================================================================

class EnhancedTextDomainWithNomic(Domain):
    """
    Text domain enhanced with Nomic Embed for better embeddings
    
    Uses Nomic Embed for semantic understanding instead of TF-IDF
    """
    
    def __init__(self, embedding_dim: int = 768, use_gpu: bool = False):
        """Initialize enhanced text domain"""
        self.embedding_dim = embedding_dim
        self.encoder = NomicTextEncoder(embedding_dim=embedding_dim, use_gpu=use_gpu)
        print(f"✓ Enhanced Text Domain initialized with Nomic Embed")
    
    @property
    def name(self) -> str:
        return "text_neural"
    
    def has_notion_of(self, concept: str) -> bool:
        concepts = ['semantic', 'meaning', 'language', 'text', 'word', 'sentence']
        return concept.lower() in concepts
    
    def encode(self, obj: Any) -> SymbolicRepresentation:
        """Encode text using Nomic Embed"""
        if not isinstance(obj, str):
            obj = str(obj)
        
        # ∆ : Extract keywords (essence)
        words = obj.lower().split()
        keywords = [w for w in words if len(w) > 3][:5]
        
        # Create delta from keywords
        delta = np.zeros(self.embedding_dim)
        for i, kw in enumerate(keywords):
            kw_emb = self.encoder.encode(kw)
            delta += kw_emb * (1.0 / (i + 1))
        
        norm = np.linalg.norm(delta)
        if norm > 0:
            delta = delta / norm
        
        # ∞ : Build semantic graph
        import networkx as nx
        infinity = nx.Graph()
        
        # Add keyword nodes
        for i, kw in enumerate(keywords):
            infinity.add_node(i, label=kw)
        
        # Add edges based on semantic similarity
        for i in range(len(keywords)):
            for j in range(i + 1, len(keywords)):
                emb_i = self.encoder.encode(keywords[i])
                emb_j = self.encoder.encode(keywords[j])
                similarity = np.dot(emb_i, emb_j)
                
                if similarity > 0.5:
                    infinity.add_edge(i, j, weight=similarity)
        
        # Ο : Full semantic embedding
        omega = self.encoder.encode(obj)
        
        # Metadata
        metadata = {
            'domain': 'text_neural',
            'text_length': len(obj),
            'word_count': len(words),
            'keywords': keywords,
            'encoder': 'nomic-embed-text-v1.5'
        }
        
        return SymbolicRepresentation(
            delta=delta,
            infinity=infinity,
            omega=omega,
            metadata=metadata
        )
    
    def decode(self, symbolic: SymbolicRepresentation) -> str:
        """Decode symbolic representation to text"""
        metadata = symbolic.metadata
        keywords = metadata.get('keywords', [])
        
        if keywords:
            return f"Text about: {', '.join(keywords)}"
        else:
            return "Text content"


# ============================================================================
# ENHANCED IMAGE DOMAIN WITH NOMIC
# ============================================================================

class EnhancedImageDomainWithNomic(Domain):
    """
    Image domain enhanced with Nomic Embed Vision for better embeddings
    
    Uses Nomic Embed Vision for semantic image understanding
    """
    
    def __init__(self, embedding_dim: int = 768, use_gpu: bool = False):
        """Initialize enhanced image domain"""
        self.embedding_dim = embedding_dim
        self.encoder = NomicImageEncoder(embedding_dim=embedding_dim, use_gpu=use_gpu)
        print(f"✓ Enhanced Image Domain initialized with Nomic Embed Vision")
    
    @property
    def name(self) -> str:
        return "image_neural"
    
    def has_notion_of(self, concept: str) -> bool:
        concepts = ['visual', 'color', 'shape', 'scene', 'object', 'image']
        return concept.lower() in concepts
    
    def encode(self, obj: Any) -> SymbolicRepresentation:
        """Encode image using Nomic Embed Vision"""
        import numpy as np
        
        # Convert to numpy array if needed
        if hasattr(obj, 'convert'):  # PIL Image
            obj = np.array(obj.convert('RGB'))
        elif isinstance(obj, str):
            # Try to load from file
            try:
                from PIL import Image
                img = Image.open(obj).convert('RGB')
                obj = np.array(img)
            except:
                raise ValueError(f"Cannot load image from {obj}")
        
        # ∆ : Extract visual features (essence)
        delta = self._extract_visual_features(obj)
        
        # ∞ : Build spatial graph
        infinity = self._build_spatial_graph(obj)
        
        # Ο : Full visual embedding using Nomic
        omega = self.encoder.encode(obj)
        
        # Metadata
        metadata = {
            'domain': 'image_neural',
            'height': obj.shape[0],
            'width': obj.shape[1],
            'encoder': 'nomic-embed-vision-v1.5'
        }
        
        return SymbolicRepresentation(
            delta=delta,
            infinity=infinity,
            omega=omega,
            metadata=metadata
        )
    
    def decode(self, symbolic: SymbolicRepresentation) -> str:
        """Decode symbolic representation to text"""
        metadata = symbolic.metadata
        h = metadata.get('height', 0)
        w = metadata.get('width', 0)
        
        return f"Image ({w}x{h})"
    
    def _extract_visual_features(self, image: np.ndarray) -> np.ndarray:
        """Extract visual features for delta"""
        # Resize for feature extraction
        resized = image[::max(1, image.shape[0]//32), ::max(1, image.shape[1]//32)]
        
        # Flatten and normalize
        flat = resized.flatten().astype(np.float32) / 255.0
        
        # Create delta
        delta = np.zeros(self.embedding_dim)
        if len(flat) > 0:
            chunk_size = max(1, len(flat) // self.embedding_dim)
            for i in range(min(self.embedding_dim, len(flat) // chunk_size)):
                delta[i] = flat[i*chunk_size:(i+1)*chunk_size].mean()
        
        # Normalize
        norm = np.linalg.norm(delta)
        if norm > 0:
            delta = delta / norm
        
        return delta
    
    def _build_spatial_graph(self, image: np.ndarray):
        """Build spatial graph for infinity"""
        import networkx as nx
        
        graph = nx.Graph()
        
        # Detect regions
        h, w = image.shape[:2]
        regions = 4  # 2x2 grid
        
        for i in range(regions):
            graph.add_node(i, label=f"region_{i}")
        
        # Add edges between adjacent regions
        for i in range(regions):
            for j in range(i + 1, regions):
                if abs(i - j) <= 1:
                    graph.add_edge(i, j, relation='adjacent')
        
        return graph


# ============================================================================
# COMPARISON FUNCTION
# ============================================================================

def compare_encoders():
    """Compare baseline vs Nomic encoders"""
    print("\n" + "="*70)
    print("ENCODER COMPARISON: Baseline vs Nomic")
    print("="*70)
    
    # Test texts
    texts = [
        "The cat sat on the mat",
        "A feline rested on the rug",
        "Machine learning is powerful"
    ]
    
    print("\n" + "="*70)
    print("Text Similarity Comparison")
    print("="*70)
    
    # Baseline (simple hash)
    print("\nBaseline Encoder (Hash-based):")
    baseline_embs = []
    for text in texts:
        emb = np.zeros(768)
        for i, word in enumerate(text.lower().split()[:768]):
            emb[i] = (hash(word) % 1000) / 1000.0
        norm = np.linalg.norm(emb)
        if norm > 0:
            emb = emb / norm
        baseline_embs.append(emb)
    
    sim_baseline_1_2 = np.dot(baseline_embs[0], baseline_embs[1])
    sim_baseline_1_3 = np.dot(baseline_embs[0], baseline_embs[2])
    
    print(f"  Text 1 vs Text 2 (similar): {sim_baseline_1_2:.4f}")
    print(f"  Text 1 vs Text 3 (different): {sim_baseline_1_3:.4f}")
    
    # Nomic Encoder
    print("\nNomic Encoder (Semantic):")
    encoder = NomicTextEncoder(embedding_dim=768)
    nomic_embs = encoder.encode(texts)
    
    sim_nomic_1_2 = np.dot(nomic_embs[0], nomic_embs[1])
    sim_nomic_1_3 = np.dot(nomic_embs[0], nomic_embs[2])
    
    print(f"  Text 1 vs Text 2 (similar): {sim_nomic_1_2:.4f}")
    print(f"  Text 1 vs Text 3 (different): {sim_nomic_1_3:.4f}")
    
    print("\n" + "="*70)
    print("✓ Comparison complete!")
    print("="*70)


# ============================================================================
# TESTS
# ============================================================================

def test_enhanced_domains():
    """Test enhanced domains with Nomic"""
    print("\n" + "="*70)
    print("ENHANCED DOMAINS WITH NOMIC TEST")
    print("="*70)
    
    # Test 1: Enhanced Text Domain
    print("\n" + "="*70)
    print("Test 1: Enhanced Text Domain")
    print("="*70)
    
    text_domain = EnhancedTextDomainWithNomic()
    
    text = "Artificial intelligence is revolutionizing technology and society"
    sym = text_domain.encode(text)
    
    print(f"\nText: {text}")
    print(f"∆ norm: {np.linalg.norm(sym.delta):.4f}")
    print(f"∞ nodes: {sym.infinity.number_of_nodes()}, edges: {sym.infinity.number_of_edges()}")
    print(f"Ο norm: {np.linalg.norm(sym.omega):.4f}")
    print(f"Keywords: {sym.metadata['keywords']}")
    print(f"Decoded: {text_domain.decode(sym)}")
    
    # Test 2: Enhanced Image Domain
    print("\n" + "="*70)
    print("Test 2: Enhanced Image Domain")
    print("="*70)
    
    image_domain = EnhancedImageDomainWithNomic()
    
    # Create test image
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    test_image[20:80, 20:80] = [255, 0, 0]
    
    sym = image_domain.encode(test_image)
    
    print(f"\nImage: 100x100 with red square")
    print(f"∆ norm: {np.linalg.norm(sym.delta):.4f}")
    print(f"∞ nodes: {sym.infinity.number_of_nodes()}, edges: {sym.infinity.number_of_edges()}")
    print(f"Ο norm: {np.linalg.norm(sym.omega):.4f}")
    print(f"Decoded: {image_domain.decode(sym)}")
    
    print("\n" + "="*70)
    print("✓ All enhanced domain tests completed!")
    print("="*70)


if __name__ == "__main__":
    test_enhanced_domains()
    compare_encoders()
