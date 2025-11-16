# numtriad/utils/metrics.py

from typing import List, Tuple
import numpy as np

from ..triad_types import Triad


def triad_distance(a: Triad, b: Triad) -> float:
    return float(np.abs(a.as_array() - b.as_array()).sum())


def triad_cosine(a: Triad, b: Triad) -> float:
    va = a.as_array()
    vb = b.as_array()
    na = np.linalg.norm(va) or 1.0
    nb = np.linalg.norm(vb) or 1.0
    return float(va.dot(vb) / (na * nb))


def alignment_score(pred: List[Triad], target: List[Triad]) -> Tuple[float, float]:
    """
    Moyenne de distance L1 + 1 - cosine.
    """
    assert len(pred) == len(target)
    dists = []
    cos_list = []
    for p, t in zip(pred, target):
        dists.append(triad_distance(p, t))
        cos_list.append(triad_cosine(p, t))
    mean_dist = float(np.mean(dists))
    mean_cos = float(np.mean(cos_list))
    return mean_dist, mean_cos
