# numtriad/triad_types.py

from dataclasses import dataclass
from typing import Iterable
import numpy as np


@dataclass
class Triad:
    """
    ∆∞Θ triad : (structure, abstraction, concrétude)
    """
    delta: float
    infinity: float
    theta: float

    @staticmethod
    def normalize(values: Iterable[float]) -> "Triad":
        arr = np.array(list(values), dtype=float)
        s = float(arr.sum()) or 1.0
        arr = arr / s
        arr = np.clip(arr, 0.0, 1.0)
        return Triad(delta=float(arr[0]), infinity=float(arr[1]), theta=float(arr[2]))

    def as_array(self) -> np.ndarray:
        return np.array([self.delta, self.infinity, self.theta], dtype=float)

    def __repr__(self) -> str:
        return f"Triad(Δ={self.delta:.3f}, ∞={self.infinity:.3f}, Θ={self.theta:.3f})"
