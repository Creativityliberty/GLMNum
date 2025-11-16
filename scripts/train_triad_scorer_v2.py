#!/usr/bin/env python3
"""
Script d'entraînement pour TriadScorerMLP-V2.
Utilisation:
python scripts/train_triad_scorer_v2.py \
  --data data/numtriad_annotations.jsonl \
  --out checkpoints/triad_scorer_v2.pt \
  --epochs 8 \
  --batch_size 32 \
  --lr 1e-4 \
  --device cuda
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import torch
from torch.utils.data import DataLoader

from numtriad.config import NumTriadConfig
from numtriad.triad_types import Triad
from numtriad.data.dataset import TriadSample, NumTriadDataset
from numtriad.encoders.base_text_encoder import BaseTextEncoder
from numtriad.encoders.numtriad_text_v2 import basic_linguistic_features
from numtriad.models.triad_scorer_mlp_v2 import TriadScorerMLP_V2
from numtriad.losses import TriadLoss, ChainLoss


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Charge un fichier JSONL."""
    data = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data.append(json.loads(line))
    return data


def build_dataset_from_jsonl(
    jsonl_path: Path,
    text_encoder: BaseTextEncoder,
    use_ling_feats: bool = True,
) -> NumTriadDataset:
    """
    Construit un dataset à partir d'un JSONL.
    Format attendu:
      - text : str
      - delta, infinity, theta : floats
      - optionnel: chain_id : str
    """
    rows = load_jsonl(jsonl_path)
    texts = [r["text"] for r in rows]

    # 1) Base embeddings
    base_embeddings = text_encoder.encode(texts)  # (N, dim)

    # 2) Triads
    samples: List[TriadSample] = []
    for r in rows:
        triad = Triad.normalize(
            [r["delta"], r["infinity"], r["theta"]]
        )
        chain_id = r.get("chain_id", None)
        samples.append(
            TriadSample(
                text=r["text"],
                triad=triad,
                chain_id=chain_id,
                meta={k: v for k, v in r.items() if k not in ("text", "delta", "infinity", "theta")},
            )
        )

    # 3) Linguistic features
    if use_ling_feats:
        feats = np.stack([basic_linguistic_features(t) for t in texts], axis=0)
    else:
        feats = None

    return NumTriadDataset(
        samples=samples,
        base_embeddings=base_embeddings,
        linguistic_features=feats,
    )


def train(
    jsonl_path: Path,
    output_path: Path,
    config: NumTriadConfig,
    batch_size: int = 32,
    num_epochs: int = 5,
    lr: float = 1e-4,
    triad_mode: str = "l1",
    lambda_chain: float = 0.1,
):
    """Entraîne le modèle TriadScorerMLP-V2."""
    device = torch.device(config.device)

    # 1) Encoders de base
    base_encoder = BaseTextEncoder(config.base_text_model_name)
    dataset = build_dataset_from_jsonl(
        jsonl_path=jsonl_path,
        text_encoder=base_encoder,
        use_ling_feats=config.use_linguistic_features,
    )

    # 2) DataLoader
    def collate_fn(batch):
        emb = torch.stack([item["emb"] for item in batch], dim=0)
        triad = torch.stack([item["triad"] for item in batch], dim=0)
        feats = None
        if "feats" in batch[0]:
            feats = torch.stack([item["feats"] for item in batch], dim=0)
        chain_ids = [item.get("chain_id", None) for item in batch]
        return {
            "emb": emb,
            "triad": triad,
            "feats": feats,
            "chain_ids": chain_ids,
        }

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_fn,
    )

    base_dim = dataset.base_embeddings.shape[1]
    feat_dim = dataset.linguistic_features.shape[1] if dataset.linguistic_features is not None else 0

    # 3) Modèle
    model = TriadScorerMLP_V2(
        base_dim=base_dim,
        feat_dim=feat_dim,
        hidden_dim=config.triad_hidden_dim,
        dropout=config.triad_dropout,
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    triad_loss_fn = TriadLoss(mode=triad_mode)
    chain_loss_fn = ChainLoss()

    model.train()

    print(f"🚀 Début entraînement - {len(dataset)} samples")
    print(f"📊 Base dim: {base_dim}, Feat dim: {feat_dim}")

    for epoch in range(1, num_epochs + 1):
        total_loss = 0.0
        total_triad = 0.0
        total_chain = 0.0
        count = 0

        for batch in loader:
            emb = batch["emb"].to(device)
            triad = batch["triad"].to(device)
            feats = batch["feats"]
            if feats is not None:
                feats = feats.to(device)

            chain_ids = batch["chain_ids"]

            optimizer.zero_grad()

            pred_probs = model(emb, feats)  # (B, 3)

            # Triad loss
            loss_triad = triad_loss_fn(pred_probs, triad)

            # Chain loss : on groupe par chain_id
            loss_chain = torch.tensor(0.0, device=device)
            chains_map = {}
            for i, cid in enumerate(chain_ids):
                if cid is None:
                    continue
                chains_map.setdefault(cid, []).append(i)

            chain_terms = []
            for cid, idxs in chains_map.items():
                if len(idxs) < 2:
                    continue
                seq_triads = pred_probs[idxs, :]  # (seq_len, 3)
                chain_terms.append(chain_loss_fn(seq_triads))

            if len(chain_terms) > 0:
                loss_chain = torch.stack(chain_terms).mean()

            loss = loss_triad + lambda_chain * loss_chain

            loss.backward()
            optimizer.step()

            total_loss += float(loss.item())
            total_triad += float(loss_triad.item())
            total_chain += float(loss_chain.item())
            count += 1

        avg_loss = total_loss / max(1, count)
        avg_t = total_triad / max(1, count)
        avg_c = total_chain / max(1, count)

        print(
            f"[Epoch {epoch}/{num_epochs}] "
            f"Loss={avg_loss:.4f} | Triad={avg_t:.4f} | Chain={avg_c:.4f}"
        )

    # Sauvegarde du modèle
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": config.__dict__,
            "base_model_name": config.base_text_model_name,
        },
        output_path,
    )
    print("✅ Modèle TriadScorerMLP-V2 sauvegardé dans:", output_path)


def main():
    parser = argparse.ArgumentParser(description="Entraîner TriadScorerMLP-V2")
    parser.add_argument("--data", type=str, required=True, help="Chemin du JSONL annoté")
    parser.add_argument("--out", type=str, required=True, help="Chemin du .pt output")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--device", type=str, default="cuda")
    args = parser.parse_args()

    cfg = NumTriadConfig(device=args.device)

    train(
        jsonl_path=Path(args.data),
        output_path=Path(args.out),
        config=cfg,
        batch_size=args.batch_size,
        num_epochs=args.epochs,
        lr=args.lr,
    )


if __name__ == "__main__":
    main()
