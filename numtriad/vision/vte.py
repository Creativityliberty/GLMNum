# numtriad/vision/vte.py
"""
Vision Transformation Engine (VTE)
==================================

Pillar B: Vision Transformation Engine pour NumTriad / GLM.

Objectifs :
-----------
- Définir G_vis : graphe des états visuels (images) et de leurs morphismes.
- Définir T_vis : espace des transformations visuelles (vecteurs de transformation).
- Fournir un moteur pratique pour :
    * encoder une image
    * l'injecter dans un graphe
    * créer des arêtes transformationnelles (edges) avec T_vis
    * interroger des chemins de transformation entre images (source -> target)

Concepts :
----------
- Chaque image est un noeud avec :
    id, embedding visuel, triade ∆∞Θ (optionnel), metadata (taille, bbox, etc.)

- Chaque transformation est une arête dirigée :
    (source_id -> target_id) + vecteur T_vis + poids

- T_vis est un vecteur simple :
    [ d_emb, d_triad, d_scale, d_position ]

    où :
      d_emb      = distance cosinus entre embeddings
      d_triad    = L1 distance sur ∆∞Θ (si dispo)
      d_scale    = |log(scale_t / scale_s)| approximative (si dispo)
      d_position = norme de la différence de position (si dispo)

Tu peux ensuite enrichir T_vis avec davantage de dimensions (couleurs, textures, etc.).

Dépendances :
-------------
- numpy
- torch
- networkx

Remarque :
----------
Ce module est auto-suffisant pour le pilier B et peut être connecté à
NumTriadMultimodalV4 ou à un encodeur visuel externe.

Author: GLM Research Team
Date: 2024-11-16
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple, Iterable

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import networkx as nx


# ============================================================================
# 1. TYPES DE BASE
# ============================================================================

@dataclass
class Triad:
    """
    Représentation simple ∆∞Θ pour la vision.
    Identique conceptuellement à celle de NumTriad, mais isolée ici pour éviter
    les imports circulaires.
    """
    delta: float
    infinity: float
    theta: float

    def as_array(self) -> np.ndarray:
        return np.asarray([self.delta, self.infinity, self.theta], dtype="float32")

    @staticmethod
    def from_tensor(t: torch.Tensor) -> "Triad":
        """Create Triad from logits tensor."""
        probs = F.softmax(t.float(), dim=-1).detach().cpu().numpy()
        return Triad(float(probs[0]), float(probs[1]), float(probs[2]))


@dataclass
class VisualNode:
    """
    Un noeud dans G_vis : représente un état visuel (une image).
    """
    node_id: str
    embedding: np.ndarray         # vecteur latent visuel
    triad: Optional[Triad] = None # ∆∞Θ visuelle, optionnelle
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VisualTransform:
    """
    Une arête dans G_vis : une transformation entre deux états visuels.
    """
    source_id: str
    target_id: str
    t_vec: np.ndarray             # T_vis (d_emb, d_triad, d_scale, d_position)
    weight: float                 # coût / intensité de la transformation
    kind: str = "generic"         # "scale", "pose", "semantic", etc.
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# 2. FONCTIONS D'UTILITÉ : DISTANCES & T_VIS
# ============================================================================

def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine distance between two vectors."""
    a = a.astype("float32")
    b = b.astype("float32")
    num = float(np.dot(a, b))
    den = float(np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)
    cos_sim = num / den
    return 1.0 - cos_sim


def l1_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Compute L1 distance between two vectors."""
    return float(np.sum(np.abs(a - b)))


def compute_scale_from_metadata(meta: Dict[str, Any]) -> Optional[float]:
    """
    Retourne une "échelle" approximative à partir de la metadata.
    Exemple :
      - si meta contient "bbox": (x,y,w,h) -> scale := w*h
      - sinon si "size": (w,h) -> scale := w*h
      - sinon None
    """
    if "bbox" in meta:
        _, _, w, h = meta["bbox"]
        return float(abs(w * h))
    if "size" in meta:
        w, h = meta["size"]
        return float(abs(w * h))
    return None


def compute_position_from_metadata(meta: Dict[str, Any]) -> Optional[np.ndarray]:
    """
    Retourne une position approximative (x,y) à partir de la metadata.
    Exemple :
      - si meta contient "bbox": (x,y,w,h) -> pos := (x + w/2, y + h/2)
      - sinon None
    """
    if "bbox" in meta:
        x, y, w, h = meta["bbox"]
        return np.asarray([x + w / 2.0, y + h / 2.0], dtype="float32")
    return None


def build_T_vis(source: VisualNode, target: VisualNode) -> np.ndarray:
    """
    Construit le vecteur T_vis entre deux nodes.

    T_vis = [ d_emb, d_triad, d_scale, d_position ]

    Valeurs manquantes -> 0.
    """
    # d_emb
    d_emb = cosine_distance(source.embedding, target.embedding)

    # d_triad
    if source.triad is not None and target.triad is not None:
        d_triad = l1_distance(source.triad.as_array(), target.triad.as_array())
    else:
        d_triad = 0.0

    # d_scale
    s_scale = compute_scale_from_metadata(source.metadata)
    t_scale = compute_scale_from_metadata(target.metadata)
    if s_scale is not None and t_scale is not None and s_scale > 0 and t_scale > 0:
        d_scale = abs(np.log(t_scale / s_scale))
    else:
        d_scale = 0.0

    # d_position
    s_pos = compute_position_from_metadata(source.metadata)
    t_pos = compute_position_from_metadata(target.metadata)
    if s_pos is not None and t_pos is not None:
        d_position = float(np.linalg.norm(t_pos - s_pos))
    else:
        d_position = 0.0

    return np.asarray([d_emb, d_triad, d_scale, d_position], dtype="float32")


# ============================================================================
# 3. G_VIS = GRAPHE TRANSFORMATIONNEL VISUEL
# ============================================================================

class VisualGraph:
    """
    Graphe de transformations visuelles G_vis.

    Chaque noeud = VisualNode
    Chaque arête = VisualTransform (avec T_vis et weight)
    """

    def __init__(self):
        self.G = nx.DiGraph()
        self.nodes: Dict[str, VisualNode] = {}

    # -----------------------------------------------------------------------
    # Noeuds
    # -----------------------------------------------------------------------

    def add_node(self, node: VisualNode) -> None:
        """Add a visual node to the graph."""
        self.nodes[node.node_id] = node
        self.G.add_node(node.node_id)

    def has_node(self, node_id: str) -> bool:
        """Check if node exists."""
        return node_id in self.nodes

    def get_node(self, node_id: str) -> VisualNode:
        """Get a node by ID."""
        return self.nodes[node_id]

    def all_nodes(self) -> Iterable[VisualNode]:
        """Get all nodes."""
        return self.nodes.values()

    # -----------------------------------------------------------------------
    # Transformations (arêtes)
    # -----------------------------------------------------------------------

    def add_transform(self, transform: VisualTransform) -> None:
        """Add a transformation edge."""
        self.G.add_edge(
            transform.source_id,
            transform.target_id,
            t_vec=transform.t_vec,
            weight=float(transform.weight),
            kind=transform.kind,
            metadata=transform.metadata,
        )

    def get_neighbors(self, node_id: str) -> List[str]:
        """Get successor nodes."""
        return list(self.G.successors(node_id))

    def shortest_path_by_weight(
        self,
        source_id: str,
        target_id: str,
    ) -> List[str]:
        """
        Renvoie la liste des ids de noeuds sur le plus court chemin
        en termes de poids cumulé.
        """
        return nx.shortest_path(self.G, source=source_id, target=target_id, weight="weight")

    def transform_sequence_T_vis(
        self,
        path: List[str],
    ) -> np.ndarray:
        """
        Agrège T_vis le long d'un chemin (somme élément-wise).
        """
        if len(path) < 2:
            return np.zeros(4, dtype="float32")
        agg = np.zeros(4, dtype="float32")
        for u, v in zip(path[:-1], path[1:]):
            edge_data = self.G.get_edge_data(u, v)
            if edge_data is None:
                continue
            t_vec = edge_data.get("t_vec", None)
            if t_vec is not None:
                agg += t_vec
        return agg

    # -----------------------------------------------------------------------
    # Construction de graphes denses
    # -----------------------------------------------------------------------

    def fully_connect_knn(
        self,
        k: int = 5,
        use_triad_weighting: bool = True,
        kind: str = "knn",
    ) -> None:
        """
        Connecte chaque noeud aux k voisins les plus proches
        en distance transformationnelle (embedding + éventuellement triade).

        Poids = ||T_vis||_2 (norme du vecteur T_vis).
        """
        node_list = list(self.nodes.values())
        n = len(node_list)
        if n == 0:
            return

        # Matrice des embeddings
        embeddings = np.stack([n.embedding for n in node_list], axis=0)
        # Optionnel : triades
        triads = []
        for n_ in node_list:
            if n_.triad is not None:
                triads.append(n_.triad.as_array())
            else:
                triads.append(np.zeros(3, dtype="float32"))
        triads = np.stack(triads, axis=0)

        # distances de base (emb)
        dists_emb = np.zeros((n, n), dtype="float32")
        for i in range(n):
            for j in range(n):
                if i == j:
                    dists_emb[i, j] = 1e9
                else:
                    dists_emb[i, j] = cosine_distance(embeddings[i], embeddings[j])

        # pondération triadique
        if use_triad_weighting:
            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    d_tr = l1_distance(triads[i], triads[j])
                    dists_emb[i, j] += 0.2 * d_tr  # lambda triad = 0.2

        # pour chaque i -> k plus petits j
        for i, node_i in enumerate(node_list):
            idx_sorted = np.argsort(dists_emb[i])[:k]
            for j in idx_sorted:
                node_j = node_list[j]
                # construire T_vis + weight
                T = build_T_vis(node_i, node_j)
                weight = float(np.linalg.norm(T, ord=2))
                tf = VisualTransform(
                    source_id=node_i.node_id,
                    target_id=node_j.node_id,
                    t_vec=T,
                    weight=weight,
                    kind=kind,
                    metadata={"base_distance": float(dists_emb[i, j])},
                )
                self.add_transform(tf)


# ============================================================================
# 4. VTE : MOTEUR HAUT NIVEAU
# ============================================================================

class SimpleVisionEncoder(nn.Module):
    """
    Encodeur visuel très simple, destiné à être remplacé par CLIP/ViT/Nomic.
    On part d'un Tensor (B,3,H,W).
    """

    def __init__(self, dim_out: int = 256):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.pool = nn.AdaptiveAvgPool2d((4, 4))
        self.fc = nn.Linear(32 * 4 * 4, dim_out)

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.conv1(images))
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)


class SimpleTriadHead(nn.Module):
    """
    Tête triadique simple pour la vision.
    Peut être remplacée par la tête triadique globale de NumTriad.
    """

    def __init__(self, dim_in: int, dropout: float = 0.1):
        super().__init__()
        self.fc1 = nn.Linear(dim_in, dim_in)
        self.fc2 = nn.Linear(dim_in, 3)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        return self.fc2(x)  # logits (B,3)


class VisionTransformationEngine(nn.Module):
    """
    VTE complet :

    - encode_image: image -> embedding visuel + triade
    - add_image: création de noeud dans G_vis
    - connect_knn: construction automatique des morphismes
    - shortest_path & T_vis_path: navigation transformationnelle
    """

    def __init__(
        self,
        dim_embedding: int = 256,
        use_triad_head: bool = True,
        device: str = "cpu",
    ):
        super().__init__()
        self.device = torch.device(device)

        self.encoder = SimpleVisionEncoder(dim_out=dim_embedding)
        self.use_triad_head = use_triad_head
        self.triad_head = SimpleTriadHead(dim_in=dim_embedding) if use_triad_head else None

        self.graph = VisualGraph()
        self.to(self.device)

    # -----------------------------------------------------------------------
    # Encodage visuel
    # -----------------------------------------------------------------------

    def encode_image(
        self,
        images: torch.Tensor,
        metadata_batch: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[np.ndarray, Optional[List[Triad]]]:
        """
        images: Tensor (B,3,H,W)
        metadata_batch: liste de dicts (len=B) ou None

        Retourne:
          embeddings_np: (B, dim_embedding)
          triads_list: List[Triad] ou None
        """
        self.eval()
        with torch.no_grad():
            images = images.to(self.device)
            feats = self.encoder(images)  # (B,dim)
            if self.use_triad_head and self.triad_head is not None:
                triad_logits = self.triad_head(feats)   # (B,3)
                triads = [
                    Triad.from_tensor(triad_logits[i])
                    for i in range(triad_logits.size(0))
                ]
            else:
                triads = None

            emb_np = feats.cpu().numpy().astype("float32")

        return emb_np, triads

    # -----------------------------------------------------------------------
    # Gestion du graphe
    # -----------------------------------------------------------------------

    def add_image(
        self,
        node_id: str,
        image: torch.Tensor,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VisualNode:
        """
        Ajoute une image comme noeud dans le graphe G_vis.

        image: Tensor (3,H,W)
        """
        if metadata is None:
            metadata = {}

        img_batch = image.unsqueeze(0)  # (1,3,H,W)
        emb_np, triads = self.encode_image(img_batch, metadata_batch=[metadata])
        triad = triads[0] if triads is not None else None

        node = VisualNode(
            node_id=node_id,
            embedding=emb_np[0],
            triad=triad,
            metadata=metadata,
        )
        self.graph.add_node(node)
        return node

    def add_images_batch(
        self,
        node_ids: List[str],
        images: torch.Tensor,
        metadata_list: Optional[List[Dict[str, Any]]] = None,
    ) -> List[VisualNode]:
        """
        Ajoute un batch d'images (B,3,H,W) en une fois.
        """
        if metadata_list is None:
            metadata_list = [{} for _ in node_ids]
        if len(node_ids) != images.size(0):
            raise ValueError("node_ids et images doivent avoir la même longueur")

        emb_np, triads = self.encode_image(images, metadata_batch=metadata_list)

        nodes = []
        for i, nid in enumerate(node_ids):
            triad = triads[i] if triads is not None else None
            node = VisualNode(
                node_id=nid,
                embedding=emb_np[i],
                triad=triad,
                metadata=metadata_list[i],
            )
            self.graph.add_node(node)
            nodes.append(node)

        return nodes

    def connect_knn(
        self,
        k: int = 5,
        use_triad_weighting: bool = True,
        kind: str = "knn",
    ) -> None:
        """
        Construit automatiquement les arêtes dans G_vis
        en reliant chaque node à ses k plus proches voisins.
        """
        self.graph.fully_connect_knn(k=k, use_triad_weighting=use_triad_weighting, kind=kind)

    # -----------------------------------------------------------------------
    # Navigation transformationnelle
    # -----------------------------------------------------------------------

    def shortest_transform_path(
        self,
        source_id: str,
        target_id: str,
    ) -> Tuple[List[str], np.ndarray]:
        """
        Calcule :
          - le chemin minimal (en poids) dans G_vis entre source et target
          - le T_vis agrégé le long de ce chemin
        """
        path = self.graph.shortest_path_by_weight(source_id, target_id)
        T_path = self.graph.transform_sequence_T_vis(path)
        return path, T_path

    def neighbors(
        self,
        node_id: str,
    ) -> List[str]:
        """Get neighbors of a node."""
        return self.graph.get_neighbors(node_id)


# ============================================================================
# 5. EXEMPLE D'UTILISATION RAPIDE
# ============================================================================

if __name__ == "__main__":
    print("🚀 Vision Transformation Engine (Pillar B) Example\n")
    
    # Exemple simple : 4 images aléatoires, construction du graphe puis chemin
    vte = VisionTransformationEngine(dim_embedding=64, device="cpu")
    print("✅ VTE initialized\n")

    # On simule 4 images 64x64
    imgs = torch.randn(4, 3, 64, 64)
    ids = ["img_A", "img_B", "img_C", "img_D"]
    metas = [
        {"bbox": (0, 0, 32, 32), "size": (64, 64)},
        {"bbox": (16, 16, 40, 40), "size": (64, 64)},
        {"bbox": (8, 8, 48, 48), "size": (64, 64)},
        {"bbox": (0, 0, 64, 64), "size": (64, 64)},
    ]

    vte.add_images_batch(ids, imgs, metas)
    print(f"✅ Added {len(ids)} images\n")

    # Connecter le graphe en KNN
    vte.connect_knn(k=2, use_triad_weighting=True)
    print("✅ Graph connected with KNN\n")

    # Chercher un chemin transformationnel entre A et D
    path, T_path = vte.shortest_transform_path("img_A", "img_D")

    print(f"📍 Chemin A → D : {path}")
    print(f"📊 T_vis agrégé : {T_path}")
    print(f"\n✅ Example completed!")
