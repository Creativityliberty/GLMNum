"""
GLM Prototype - Image Domain
=============================

Domaine Image pour le système symbolique ∆∞Ο

∆ (Delta) : Features visuelles (couleurs dominantes, formes)
∞ (Infinity) : Graphe spatial (objets + relations)
Ο (Omega) : Description complète / Embedding visuel

Author: GLM Research Team
Date: 2024-11-15

Usage:
    from domains.image import ImageDomain
    domain = ImageDomain()
    symbolic = domain.encode(image)
    description = domain.decode(symbolic)
"""

from typing import Any, Dict, List, Tuple, Optional
import numpy as np
import networkx as nx
from dataclasses import dataclass
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.symbolic import Domain, SymbolicRepresentation
from delta_infty_omicron import enhance_symbolic_metadata

# Optionnel : PIL pour traitement d'images
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Optionnel : OpenCV pour détection
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


# ============================================================================
# UTILITAIRES D'EXTRACTION DE FEATURES
# ============================================================================

def extract_dominant_colors(image_data: np.ndarray, num_colors: int = 5) -> List[Tuple[int, int, int]]:
    """
    Extraire les couleurs dominantes d'une image
    
    Args:
        image_data: Array numpy de l'image (H, W, 3)
        num_colors: Nombre de couleurs à extraire
    
    Returns:
        Liste de tuples RGB
    """
    if len(image_data.shape) != 3 or image_data.shape[2] != 3:
        return [(128, 128, 128)]  # Couleur par défaut
    
    # Redimensionner pour performance
    small = cv2.resize(image_data, (50, 50)) if HAS_CV2 else image_data
    
    # Reshape en liste de pixels
    pixels = small.reshape(-1, 3)
    
    # K-means clustering (simplifié)
    unique_colors = np.unique(pixels, axis=0)
    
    # Retourner les couleurs uniques (max num_colors)
    colors = []
    for color in unique_colors[:num_colors]:
        colors.append(tuple(int(c) for c in color))
    
    return colors if colors else [(128, 128, 128)]


def detect_shapes(image_data: np.ndarray) -> Dict[str, int]:
    """
    Détecter les formes basiques dans l'image
    
    Args:
        image_data: Array numpy de l'image
    
    Returns:
        Dict avec comptage des formes
    """
    shapes = {
        'rectangles': 0,
        'circles': 0,
        'triangles': 0,
        'lines': 0,
        'other': 0
    }
    
    if not HAS_CV2:
        # Estimation basique sans OpenCV
        h, w = image_data.shape[:2]
        aspect_ratio = w / h if h > 0 else 1
        
        if 0.8 < aspect_ratio < 1.2:
            shapes['rectangles'] = 1
        else:
            shapes['rectangles'] = 0
        
        shapes['circles'] = 1 if aspect_ratio > 0.9 else 0
        return shapes
    
    # Avec OpenCV
    gray = cv2.cvtColor(image_data, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    
    # Détecter contours
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 100:
            continue
        
        # Approximer la forme
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        sides = len(approx)
        
        if sides == 3:
            shapes['triangles'] += 1
        elif sides == 4:
            shapes['rectangles'] += 1
        elif sides > 6:
            shapes['circles'] += 1
        else:
            shapes['other'] += 1
    
    return shapes


def detect_objects(image_data: np.ndarray) -> List[str]:
    """
    Détecter les objets dans l'image (simplifié)
    
    Args:
        image_data: Array numpy de l'image
    
    Returns:
        Liste de labels d'objets
    """
    objects = []
    
    # Analyse basique sans modèle pré-entraîné
    h, w = image_data.shape[:2]
    
    # Analyser les couleurs pour inférer objets
    colors = extract_dominant_colors(image_data, 3)
    
    # Heuristiques simples
    for r, g, b in colors:
        if r > 150 and g < 100 and b < 100:
            objects.append('red_object')
        elif r < 100 and g > 150 and b < 100:
            objects.append('green_object')
        elif r < 100 and g < 100 and b > 150:
            objects.append('blue_object')
        elif r > 150 and g > 150 and b < 100:
            objects.append('yellow_object')
    
    # Détecter formes
    shapes = detect_shapes(image_data)
    if shapes['circles'] > 0:
        objects.append('circular_shape')
    if shapes['rectangles'] > 0:
        objects.append('rectangular_shape')
    if shapes['triangles'] > 0:
        objects.append('triangular_shape')
    
    return objects if objects else ['image']


def build_spatial_graph(objects: List[str]) -> nx.Graph:
    """
    Construire un graphe spatial des objets
    
    Args:
        objects: Liste d'objets détectés
    
    Returns:
        Graphe NetworkX représentant les relations spatiales
    """
    graph = nx.Graph()
    
    # Ajouter nœuds pour chaque objet
    for i, obj in enumerate(objects):
        graph.add_node(i, label=obj)
    
    # Ajouter arêtes (relations spatiales)
    for i in range(len(objects)):
        for j in range(i + 1, min(i + 3, len(objects))):
            # Relation de proximité
            graph.add_edge(i, j, relation='adjacent')
    
    return graph


def compute_image_embedding(image_data: np.ndarray, embedding_dim: int = 128) -> np.ndarray:
    """
    Calculer un embedding complet de l'image
    
    Args:
        image_data: Array numpy de l'image
        embedding_dim: Dimensionalité de l'embedding
    
    Returns:
        Vecteur embedding
    """
    # Redimensionner l'image
    if len(image_data.shape) == 3:
        resized = cv2.resize(image_data, (32, 32)) if HAS_CV2 else image_data[:32, :32]
    else:
        resized = image_data[:32, :32]
    
    # Normaliser
    normalized = resized.astype(np.float32) / 255.0
    
    # Aplatir
    flattened = normalized.flatten()
    
    # Redimensionner à embedding_dim
    if len(flattened) > embedding_dim:
        # Réduire par moyenne
        chunk_size = len(flattened) // embedding_dim
        embedding = np.array([
            flattened[i*chunk_size:(i+1)*chunk_size].mean()
            for i in range(embedding_dim)
        ])
    else:
        # Augmenter par padding
        embedding = np.zeros(embedding_dim)
        embedding[:len(flattened)] = flattened
    
    # Normaliser
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    
    return embedding


# ============================================================================
# IMAGE DOMAIN
# ============================================================================

class ImageDomain(Domain):
    """
    Domaine Image pour le système symbolique ∆∞Ο
    
    Encode des images en représentations symboliques :
    - ∆ : Features visuelles (couleurs, formes)
    - ∞ : Graphe spatial (objets + relations)
    - Ο : Embedding complet
    """
    
    def __init__(self, embedding_dim: int = 128):
        """
        Initialiser le domaine Image
        
        Args:
            embedding_dim: Dimensionalité des embeddings
        """
        self.embedding_dim = embedding_dim
        print(f"✓ Image domain initialized: {self.name}")
    
    @property
    def name(self) -> str:
        """Nom du domaine"""
        return "image"
    
    def has_notion_of(self, concept: str) -> bool:
        """Vérifier si le domaine a une notion du concept"""
        concepts = ['color', 'shape', 'object', 'spatial', 'visual', 'scene']
        return concept.lower() in concepts
    
    def encode(self, obj: Any) -> SymbolicRepresentation:
        """
        Encoder une image en représentation symbolique ∆∞Ο
        
        Args:
            obj: Image (PIL.Image ou np.ndarray ou chemin fichier)
        
        Returns:
            SymbolicRepresentation
        """
        # Charger l'image
        if isinstance(obj, str):
            # Chemin fichier
            if HAS_PIL:
                image = Image.open(obj).convert('RGB')
                image_data = np.array(image)
            else:
                raise ValueError("PIL required to load image from file")
        elif HAS_PIL and isinstance(obj, Image.Image):
            # PIL Image
            image_data = np.array(obj.convert('RGB'))
        elif isinstance(obj, np.ndarray):
            # Numpy array
            image_data = obj
        else:
            raise ValueError(f"Unsupported image type: {type(obj)}")
        
        # Extraire features
        colors = extract_dominant_colors(image_data)
        shapes = detect_shapes(image_data)
        objects = detect_objects(image_data)
        
        # ∆ : Essence visuelle (features principales)
        delta = self._encode_delta(colors, shapes, objects)
        
        # ∞ : Graphe spatial
        infinity = build_spatial_graph(objects)
        
        # Ο : Embedding complet
        omega = compute_image_embedding(image_data, self.embedding_dim)
        
        # Base metadata with ∆∞Ο scores
        base_metadata = {
            'domain': 'image',
            'height': image_data.shape[0],
            'width': image_data.shape[1],
            'colors': colors,
            'shapes': shapes,
            'objects': objects,
            'num_objects': len(objects),
            'image_preview': f"Image({image_data.shape[0]}x{image_data.shape[1]})"
        }
        
        # Create text representation for ∆∞Ο scoring
        image_text = f"Image with {len(objects)} objects, colors: {colors[:3]}, shapes: {shapes[:3]}"
        
        # Enhance with ∆∞Ο triadic scores
        metadata = enhance_symbolic_metadata(base_metadata, image_text)
        
        return SymbolicRepresentation(
            delta=delta,
            infinity=infinity,
            omega=omega,
            metadata=metadata
        )
    
    def decode(self, symbolic: SymbolicRepresentation) -> str:
        """
        Décoder une représentation symbolique en description textuelle
        
        Args:
            symbolic: SymbolicRepresentation
        
        Returns:
            Description textuelle de l'image
        """
        metadata = symbolic.metadata
        
        # Construire description
        description = "Image scene: "
        
        # Ajouter informations sur les objets
        if 'objects' in metadata and metadata['objects']:
            objects_str = ', '.join(metadata['objects'][:3])
            description += f"Contains {objects_str}. "
        
        # Ajouter informations sur les couleurs
        if 'colors' in metadata and metadata['colors']:
            colors_desc = self._describe_colors(metadata['colors'])
            description += f"Colors: {colors_desc}. "
        
        # Ajouter informations sur les formes
        if 'shapes' in metadata:
            shapes = metadata['shapes']
            shape_desc = self._describe_shapes(shapes)
            if shape_desc:
                description += f"Shapes: {shape_desc}. "
        
        # Ajouter dimensions
        if 'height' in metadata and 'width' in metadata:
            description += f"Dimensions: {metadata['width']}x{metadata['height']}."
        
        return description
    
    def _encode_delta(self, colors: List[Tuple[int, int, int]], 
                      shapes: Dict[str, int], 
                      objects: List[str]) -> np.ndarray:
        """Encoder l'essence visuelle (∆)"""
        features = []
        
        # Features de couleur
        for r, g, b in colors[:3]:
            features.extend([r/255.0, g/255.0, b/255.0])
        
        # Features de forme
        for count in shapes.values():
            features.append(count / 10.0)  # Normaliser
        
        # Features d'objets
        features.append(len(objects) / 10.0)
        
        # Padding
        while len(features) < self.embedding_dim:
            features.append(0.0)
        
        # Convertir en array et normaliser
        delta = np.array(features[:self.embedding_dim], dtype=np.float32)
        norm = np.linalg.norm(delta)
        if norm > 0:
            delta = delta / norm
        
        return delta
    
    def _describe_colors(self, colors: List[Tuple[int, int, int]]) -> str:
        """Décrire les couleurs"""
        color_names = []
        for r, g, b in colors:
            if r > 150 and g < 100 and b < 100:
                color_names.append('red')
            elif r < 100 and g > 150 and b < 100:
                color_names.append('green')
            elif r < 100 and g < 100 and b > 150:
                color_names.append('blue')
            elif r > 150 and g > 150 and b < 100:
                color_names.append('yellow')
            elif r > 150 and g > 150 and b > 150:
                color_names.append('white')
            elif r < 100 and g < 100 and b < 100:
                color_names.append('black')
            else:
                color_names.append('mixed')
        
        return ', '.join(color_names[:3])
    
    def _describe_shapes(self, shapes: Dict[str, int]) -> str:
        """Décrire les formes"""
        shape_desc = []
        if shapes.get('rectangles', 0) > 0:
            shape_desc.append(f"{shapes['rectangles']} rectangle(s)")
        if shapes.get('circles', 0) > 0:
            shape_desc.append(f"{shapes['circles']} circle(s)")
        if shapes.get('triangles', 0) > 0:
            shape_desc.append(f"{shapes['triangles']} triangle(s)")
        
        return ', '.join(shape_desc) if shape_desc else "various"


# ============================================================================
# TESTS
# ============================================================================

def test_image_domain():
    """Tester le domaine Image"""
    print("\n" + "="*70)
    print("GLM PROTOTYPE - IMAGE DOMAIN TEST")
    print("="*70)
    
    domain = ImageDomain(embedding_dim=128)
    
    # Test 1 : Image synthétique simple
    print("\n" + "="*70)
    print("Test 1: Simple Synthetic Image")
    print("="*70)
    
    # Créer une image simple
    simple_image = np.zeros((100, 100, 3), dtype=np.uint8)
    simple_image[20:80, 20:80] = [255, 0, 0]  # Carré rouge
    
    sym = domain.encode(simple_image)
    print(f"\nSymbolic representation:")
    print(f"SymbolicRepresentation(")
    print(f"  ∆: shape={sym.delta.shape}, norm={np.linalg.norm(sym.delta):.4f}")
    print(f"  ∞: nodes={sym.infinity.number_of_nodes()}, edges={sym.infinity.number_of_edges()}")
    print(f"  Ο: shape={sym.omega.shape}, norm={np.linalg.norm(sym.omega):.4f}")
    print(f"  metadata: {sym.metadata}")
    print(f")")
    
    description = domain.decode(sym)
    print(f"\nDecoded description: {description}")
    
    # Test 2 : Image avec plusieurs couleurs
    print("\n" + "="*70)
    print("Test 2: Multi-color Image")
    print("="*70)
    
    multi_image = np.zeros((100, 100, 3), dtype=np.uint8)
    multi_image[0:50, 0:50] = [255, 0, 0]      # Rouge
    multi_image[0:50, 50:100] = [0, 255, 0]    # Vert
    multi_image[50:100, 0:50] = [0, 0, 255]    # Bleu
    multi_image[50:100, 50:100] = [255, 255, 0]  # Jaune
    
    sym = domain.encode(multi_image)
    description = domain.decode(sym)
    print(f"\nDecoded description: {description}")
    print(f"Metadata: {sym.metadata}")
    
    # Test 3 : Image similarity
    print("\n" + "="*70)
    print("Test 3: Image Similarity")
    print("="*70)
    
    # Créer deux images similaires
    image1 = np.zeros((100, 100, 3), dtype=np.uint8)
    image1[20:80, 20:80] = [255, 0, 0]
    
    image2 = np.zeros((100, 100, 3), dtype=np.uint8)
    image2[25:75, 25:75] = [255, 0, 0]
    
    sym1 = domain.encode(image1)
    sym2 = domain.encode(image2)
    
    # Calculer similarité
    similarity = np.dot(sym1.omega, sym2.omega)
    print(f"\nImage 1 vs Image 2 similarity: {similarity:.4f}")
    
    # Test 4 : Round-trip fidelity
    print("\n" + "="*70)
    print("Test 4: Round-trip Fidelity")
    print("="*70)
    
    test_images = [
        ("Simple Red", np.full((50, 50, 3), [255, 0, 0], dtype=np.uint8)),
        ("Simple Blue", np.full((50, 50, 3), [0, 0, 255], dtype=np.uint8)),
        ("Gradient", np.tile(np.linspace(0, 255, 50), (50, 3)).reshape(50, 50, 3).astype(np.uint8)),
    ]
    
    print(f"\n{'Original':<30} {'Reconstructed':<30} {'Fidelity':<10}")
    print("-" * 70)
    
    for name, image in test_images:
        sym = domain.encode(image)
        reconstructed = domain.decode(sym)
        sym_recon = domain.encode(image)  # Re-encode
        
        fidelity = np.dot(sym.omega, sym_recon.omega)
        print(f"{name:<30} {reconstructed[:28]:<30} {fidelity:.4f}")
    
    print("\n" + "="*70)
    print("✓ All image tests completed!")
    print("="*70)


if __name__ == "__main__":
    test_image_domain()
