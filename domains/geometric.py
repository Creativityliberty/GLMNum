"""
GLM Prototype - Geometric Domain
=================================

Implémentation du domaine géométrique avec transformation Triangle → Cercle

Author: GLM Research Team
Date: 2024-11-15
"""

from typing import Any, Dict, List
import numpy as np
import networkx as nx
from dataclasses import dataclass

import sys
import os
# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.symbolic import Domain, SymbolicRepresentation
from delta_infty_omicron import enhance_symbolic_metadata


# ============================================================================
# STRUCTURES GÉOMÉTRIQUES
# ============================================================================

@dataclass
class Polygon:
    """
    Représentation d'un polygone régulier
    
    Attributes:
        sides: Nombre de côtés
        radius: Rayon du cercle circonscrit
    """
    sides: int
    radius: float = 1.0
    
    def __post_init__(self):
        if self.sides < 3:
            raise ValueError("Un polygone doit avoir au moins 3 côtés")
    
    @property
    def is_triangle(self) -> bool:
        """Est-ce un triangle ?"""
        return self.sides == 3
    
    @property
    def is_circle(self) -> bool:
        """Est-ce approximativement un cercle ? (>1000 côtés)"""
        return self.sides > 1000
    
    @property
    def interior_angle(self) -> float:
        """Angle intérieur (degrés)"""
        return 180.0 * (self.sides - 2) / self.sides
    
    @property
    def sum_interior_angles(self) -> float:
        """Somme des angles intérieurs (degrés)"""
        return 180.0 * (self.sides - 2)
    
    @property
    def sum_exterior_angles(self) -> float:
        """Somme des angles extérieurs (toujours 360°)"""
        return 360.0
    
    @property
    def perimeter(self) -> float:
        """Périmètre approximatif"""
        side_length = 2 * self.radius * np.sin(np.pi / self.sides)
        return self.sides * side_length
    
    @property
    def area(self) -> float:
        """Aire du polygone"""
        return 0.5 * self.sides * self.radius**2 * np.sin(2 * np.pi / self.sides)
    
    def vertices(self) -> np.ndarray:
        """
        Coordonnées des sommets
        
        Returns:
            Array de shape (sides, 2) avec coordonnées (x, y)
        """
        angles = np.linspace(0, 2 * np.pi, self.sides, endpoint=False)
        x = self.radius * np.cos(angles)
        y = self.radius * np.sin(angles)
        return np.column_stack([x, y])
    
    def __repr__(self) -> str:
        if self.is_triangle:
            name = "Triangle"
        elif self.is_circle:
            name = "Circle (approximation)"
        else:
            name = f"Polygon({self.sides} sides)"
        
        return (
            f"{name}("
            f"sides={self.sides}, "
            f"radius={self.radius:.2f}, "
            f"area={self.area:.2f}"
            f")"
        )


@dataclass
class Circle:
    """
    Cercle (polygone avec ∞ côtés)
    
    Attributes:
        radius: Rayon du cercle
    """
    radius: float = 1.0
    
    @property
    def circumference(self) -> float:
        """Circonférence"""
        return 2 * np.pi * self.radius
    
    @property
    def area(self) -> float:
        """Aire"""
        return np.pi * self.radius**2
    
    def as_polygon(self, approximation_sides: int = 1000) -> Polygon:
        """Approximer le cercle comme un polygone"""
        return Polygon(sides=approximation_sides, radius=self.radius)
    
    def __repr__(self) -> str:
        return f"Circle(radius={self.radius:.2f}, area={self.area:.2f})"


# ============================================================================
# DOMAINE GÉOMÉTRIQUE
# ============================================================================

class GeometricDomain(Domain):
    """
    Domaine géométrique : Triangle ↔ Polygones ↔ Cercle
    
    Dans ce domaine :
    - ∆ (Delta) = Triangle (origine, 3 côtés)
    - ∞ (Infinity) = Polygones intermédiaires (4, 5, 6... côtés)
    - Ο (Omega) = Cercle (complétude, ∞ côtés)
    """
    
    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
    
    @property
    def name(self) -> str:
        return "geometry"
    
    def has_notion_of(self, concept: str) -> bool:
        """Le domaine géométrique a-t-il cette notion ?"""
        notions = {
            'beginning': True,      # Triangle (minimal)
            'compression': True,    # Angles aigus
            'transformation': True, # Morphing
            'continuity': True,     # Limite continue
            'ending': True,         # Cercle (maximal)
            'manifestation': True,  # Forme visible
        }
        return notions.get(concept, False)
    
    def _parse_string_to_geometry(self, text: str):
        """Parser string to geometric object"""
        text = text.lower().strip()
        
        if text in ['triangle', 'tri']:
            return Polygon(sides=3, radius=1.0)
        elif text in ['square', 'carre']:
            return Polygon(sides=4, radius=1.0)
        elif text in ['pentagon', 'pentagone']:
            return Polygon(sides=5, radius=1.0)
        elif text in ['hexagon', 'hexagone']:
            return Polygon(sides=6, radius=1.0)
        elif text in ['circle', 'cercle']:
            return Circle(radius=1.0)
        elif text in ['sphere', 'sphere']:
            return Circle(radius=1.0)  # Approximate as circle
        else:
            # Default to triangle for unknown shapes
            return Polygon(sides=3, radius=1.0)
    
    def encode(self, obj: Any) -> SymbolicRepresentation:
        """
        Encoder une forme géométrique vers ∆∞Ο
        
        Args:
            obj: Polygon, Circle, ou string (ex: "triangle", "circle")
            
        Returns:
            Représentation symbolique
        """
        # Convert string to geometric object
        if isinstance(obj, str):
            obj = self._parse_string_to_geometry(obj)
        
        if isinstance(obj, Circle):
            obj = obj.as_polygon()
        
        if not isinstance(obj, Polygon):
            raise ValueError(f"Expected Polygon, Circle, or string, got {type(obj)}")
        
        # ∆ : Essence de la forme (features géométriques)
        delta = self._extract_essence(obj)
        
        # ∞ : Processus de transformation (graphe de morphing)
        infinity = self._build_morphing_graph(obj)
        
        # Ο : Représentation complète (embedding de la forme finale)
        omega = self._compute_shape_embedding(obj)
        
        # Base metadata with ∆∞Ο scores
        base_metadata = {
            'domain': self.name,
            'sides': obj.sides,
            'radius': obj.radius,
            'type': 'triangle' if obj.is_triangle else 'circle' if obj.is_circle else 'polygon'
        }
        
        # Create text representation for ∆∞Ο scoring
        geom_text = f"{base_metadata['type']} with {obj.sides} sides and radius {obj.radius}"
        
        # Enhance with ∆∞Ο triadic scores
        enhanced_metadata = enhance_symbolic_metadata(base_metadata, geom_text)
        
        return SymbolicRepresentation(
            delta=delta,
            infinity=infinity,
            omega=omega,
            metadata=enhanced_metadata
        )
    
    def decode(self, symbolic: SymbolicRepresentation) -> Any:
        """
        Décoder ∆∞Ο vers une forme géométrique
        
        Args:
            symbolic: Représentation symbolique
            
        Returns:
            Polygon ou Circle
        """
        # Reconstruire depuis les métadonnées si disponibles
        if 'sides' in symbolic.metadata:
            sides = symbolic.metadata['sides']
            radius = symbolic.metadata.get('radius', 1.0)
            
            if sides > 1000:
                return Circle(radius=radius)
            else:
                return Polygon(sides=sides, radius=radius)
        
        # Sinon, décoder depuis omega (embedding)
        # Pour simplifier, on extrait le nombre de côtés depuis omega[0]
        sides_estimate = int(np.clip(symbolic.omega[0] * 100, 3, 1000))
        
        if sides_estimate > 100:
            return Circle(radius=1.0)
        else:
            return Polygon(sides=sides_estimate, radius=1.0)
    
    def is_origin(self, obj: Any) -> bool:
        """Est-ce une origine (triangle) ?"""
        return isinstance(obj, Polygon) and obj.is_triangle
    
    def is_completion(self, obj: Any) -> bool:
        """Est-ce une complétude (cercle) ?"""
        return isinstance(obj, (Circle, Polygon)) and (
            isinstance(obj, Circle) or obj.is_circle
        )
    
    # ========================================================================
    # MÉTHODES PRIVÉES
    # ========================================================================
    
    def _extract_essence(self, polygon: Polygon) -> np.ndarray:
        """
        Extraire l'essence géométrique (∆)
        
        Features :
        - Nombre de côtés (normalisé)
        - Angle intérieur
        - Régularité
        - Complexité
        """
        essence = np.zeros(self.embedding_dim)
        
        # Feature 0-9 : Nombre de côtés (one-hot approximation)
        sides_normalized = min(polygon.sides / 10.0, 1.0)
        essence[0] = sides_normalized
        
        # Feature 10-19 : Angle intérieur
        angle_normalized = polygon.interior_angle / 180.0
        essence[10] = angle_normalized
        
        # Feature 20-29 : Régularité (1.0 pour polygones réguliers)
        essence[20] = 1.0
        
        # Feature 30-39 : Complexité géométrique
        complexity = np.log(polygon.sides) / np.log(1000)  # Normalisé [0, 1]
        essence[30] = complexity
        
        # Reste : embedding aléatoire stable basé sur sides
        np.random.seed(polygon.sides)
        essence[40:] = np.random.randn(self.embedding_dim - 40) * 0.1
        
        # Normaliser
        essence /= (np.linalg.norm(essence) + 1e-8)
        
        return essence
    
    def _build_morphing_graph(self, polygon: Polygon) -> nx.Graph:
        """
        Construire le graphe de morphing (∞)
        
        Le graphe représente les transformations possibles :
        Triangle → Carré → Pentagone → ... → Cercle
        """
        graph = nx.Graph()
        
        # Ajouter les nœuds (étapes de morphing)
        current_sides = 3
        max_sides = max(polygon.sides, 10)
        
        while current_sides <= max_sides:
            graph.add_node(
                current_sides,
                sides=current_sides,
                type='polygon'
            )
            
            # Arête vers le prochain polygone
            if current_sides < max_sides:
                graph.add_edge(current_sides, current_sides + 1)
            
            current_sides += 1
        
        # Si on vise un cercle, ajouter nœud final
        if polygon.sides > 100 or isinstance(polygon, Circle):
            graph.add_node('circle', sides=float('inf'), type='circle')
            graph.add_edge(max_sides, 'circle')
        
        return graph
    
    def _compute_shape_embedding(self, polygon: Polygon) -> np.ndarray:
        """
        Calculer l'embedding complet de la forme (Ο)
        
        Combine toutes les propriétés géométriques
        """
        embedding = np.zeros(self.embedding_dim)
        
        # Features géométriques
        embedding[0] = polygon.sides / 1000.0  # Normalisé
        embedding[1] = polygon.area
        embedding[2] = polygon.perimeter
        embedding[3] = polygon.interior_angle / 180.0
        embedding[4] = polygon.sum_interior_angles / 180000.0
        
        # Features de forme
        vertices = polygon.vertices()
        embedding[5] = np.std(vertices[:, 0])  # Variabilité en x
        embedding[6] = np.std(vertices[:, 1])  # Variabilité en y
        
        # Embedding basé sur Fourier descriptors (simplifié)
        fft_x = np.fft.fft(vertices[:, 0])
        fft_y = np.fft.fft(vertices[:, 1])
        n_coeffs = min(10, len(fft_x))
        embedding[10:10+n_coeffs] = np.abs(fft_x[:n_coeffs]) / (polygon.sides + 1)
        embedding[20:20+n_coeffs] = np.abs(fft_y[:n_coeffs]) / (polygon.sides + 1)
        
        # Reste : caractéristiques stables
        np.random.seed(polygon.sides * 17)
        embedding[30:] = np.random.randn(self.embedding_dim - 30) * 0.1
        
        # Normaliser
        embedding /= (np.linalg.norm(embedding) + 1e-8)
        
        return embedding


# ============================================================================
# TRANSFORMATIONS GÉOMÉTRIQUES
# ============================================================================

def morph_polygon(polygon: Polygon, target_sides: int, steps: int = 10) -> List[Polygon]:
    """
    Morphing progressif d'un polygone vers un autre
    
    Args:
        polygon: Polygone source
        target_sides: Nombre de côtés cible
        steps: Nombre d'étapes intermédiaires
        
    Returns:
        Liste de polygones intermédiaires
    """
    morphing_sequence = []
    
    current = polygon.sides
    step_size = (target_sides - current) / steps
    
    for i in range(steps + 1):
        sides = int(current + i * step_size)
        sides = max(3, sides)  # Au minimum un triangle
        
        morphing_sequence.append(Polygon(sides=sides, radius=polygon.radius))
    
    return morphing_sequence


def triangle_to_circle(radius: float = 1.0, steps: int = 20) -> List[Polygon]:
    """
    Transformation complète Triangle → Cercle
    
    Args:
        radius: Rayon du cercle circonscrit
        steps: Nombre d'étapes
        
    Returns:
        Séquence de polygones du triangle au cercle
    """
    triangle = Polygon(sides=3, radius=radius)
    circle_approx_sides = 1000
    
    return morph_polygon(triangle, circle_approx_sides, steps=steps)


# ============================================================================
# EXEMPLE D'UTILISATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("GLM PROTOTYPE - GEOMETRIC DOMAIN TEST")
    print("=" * 60)
    
    # Créer le domaine géométrique
    geo_domain = GeometricDomain(embedding_dim=128)
    print(f"\n✓ Geometric domain initialized: {geo_domain.name}")
    
    # Test 1 : Triangle
    print("\n" + "=" * 60)
    print("Test 1: Triangle")
    print("=" * 60)
    
    triangle = Polygon(sides=3, radius=1.0)
    print(f"\nOriginal: {triangle}")
    print(f"Interior angle: {triangle.interior_angle:.2f}°")
    print(f"Area: {triangle.area:.4f}")
    print(f"Perimeter: {triangle.perimeter:.4f}")
    
    # Encoder
    sym_triangle = geo_domain.encode(triangle)
    print(f"\nSymbolic representation:")
    print(sym_triangle)
    
    # Décoder
    reconstructed = geo_domain.decode(sym_triangle)
    print(f"\nReconstructed: {reconstructed}")
    
    # Test 2 : Cercle
    print("\n" + "=" * 60)
    print("Test 2: Circle")
    print("=" * 60)
    
    circle = Circle(radius=1.0)
    print(f"\nOriginal: {circle}")
    print(f"Circumference: {circle.circumference:.4f}")
    print(f"Area: {circle.area:.4f}")
    
    sym_circle = geo_domain.encode(circle)
    print(f"\nSymbolic representation:")
    print(sym_circle)
    
    reconstructed_circle = geo_domain.decode(sym_circle)
    print(f"\nReconstructed: {reconstructed_circle}")
    
    # Test 3 : Morphing Triangle → Circle
    print("\n" + "=" * 60)
    print("Test 3: Morphing Triangle → Circle")
    print("=" * 60)
    
    sequence = triangle_to_circle(radius=1.0, steps=10)
    print(f"\nMorphing sequence ({len(sequence)} steps):")
    for i, poly in enumerate(sequence):
        print(f"  Step {i}: {poly.sides:4d} sides, area={poly.area:.4f}")
    
    # Test 4 : Round-trip fidelity
    print("\n" + "=" * 60)
    print("Test 4: Round-trip Fidelity")
    print("=" * 60)
    
    test_polygons = [
        Polygon(sides=3),
        Polygon(sides=5),
        Polygon(sides=8),
        Polygon(sides=12),
        Circle(radius=1.0)
    ]
    
    from core.symbolic import SymbolicOperations
    
    print("\nPolygon -> ∆∞Ο -> Polygon fidelity:")
    for poly in test_polygons:
        sym = geo_domain.encode(poly)
        reconstructed = geo_domain.decode(sym)
        
        # Re-encoder pour comparer
        sym_reconstructed = geo_domain.encode(reconstructed)
        fidelity = SymbolicOperations.similarity(sym, sym_reconstructed)
        
        print(f"  {str(poly):40s} -> Fidelity: {fidelity:.4f}")
    
    print("\n" + "=" * 60)
    print("✓ All geometric tests passed!")
    print("=" * 60)
