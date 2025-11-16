# numtriad/losses.py

from typing import Tuple
import torch
import torch.nn as nn


class TriadLoss(nn.Module):
    """
    L1 ou L2 sur les triades prédites vs cibles.
    """

    def __init__(self, mode: str = "l1"):
        super().__init__()
        if mode not in ("l1", "l2"):
            raise ValueError("mode must be 'l1' or 'l2'")
        self.mode = mode
        self.l1 = nn.L1Loss()
        self.l2 = nn.MSELoss()

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """
        pred, target : (batch, 3)
        """
        if self.mode == "l1":
            return self.l1(pred, target)
        return self.l2(pred, target)


class ChainLoss(nn.Module):
    """
    Encourage une direction "abstrait → concret" (ou l'inverse)
    sur une chaîne de textes triadiquement annotés.
    Ex: Δ↓, Θ↑ sur la séquence.
    """

    def __init__(self, weight_delta: float = 1.0, weight_theta: float = 1.0):
        super().__init__()
        self.weight_delta = weight_delta
        self.weight_theta = weight_theta

    def forward(self, triads: torch.Tensor) -> torch.Tensor:
        """
        triads : (seq_len, 3)
        Suppose que la séquence est ordonnée abstrait → concret.
        On pénalise les inversions.
        """
        deltas = triads[:, 0]  # ∆
        thetas = triads[:, 2]  # Θ

        # On veut ∆ décroissante, Θ croissante
        delta_diff = deltas[1:] - deltas[:-1]  # doit être <= 0
        theta_diff = thetas[1:] - thetas[:-1]  # doit être >= 0

        loss_delta = torch.relu(delta_diff).mean()     # >0 = pénalité
        loss_theta = torch.relu(-theta_diff).mean()    # <0 = pénalité

        return self.weight_delta * loss_delta + self.weight_theta * loss_theta


def triad_total_loss(
    pred_triad: torch.Tensor,
    target_triad: torch.Tensor,
    sequence_triads: torch.Tensor,
    triad_mode: str = "l1",
    lambda_chain: float = 0.1,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Combine TriadLoss + ChainLoss.
    """
    triad_loss_fn = TriadLoss(mode=triad_mode)
    chain_loss_fn = ChainLoss()

    l_triad = triad_loss_fn(pred_triad, target_triad)
    l_chain = chain_loss_fn(sequence_triads)

    total = l_triad + lambda_chain * l_chain
    return total, l_triad, l_chain
