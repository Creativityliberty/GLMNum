#!/usr/bin/env python3
"""
Script d'entraînement DeepTriadTransformer (niveau séquence).
Utilisation:
python scripts/train_deeptriad_transformer.py \
  --data data/deeptriad_sequences.jsonl \
  --out checkpoints/deeptriad_transformer_v1.pt \
  --max_len 32 \
  --epochs 5 \
  --batch_size 8 \
  --lr 1e-4 \
  --device cuda
"""

import argparse
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from numtriad.config import NumTriadConfig
from numtriad.encoders.base_text_encoder import BaseTextEncoder
from numtriad.data.deeptriad_dataset import build_deeptriad_dataset
from numtriad.models.deeptriad_transformer import (
    DeepTriadTransformer,
    DeepTriadTransformerConfig,
)
from numtriad.losses import TriadLoss


def train_deeptriad(
    data_path: Path,
    output_path: Path,
    config: NumTriadConfig,
    max_len: int = 32,
    batch_size: int = 8,
    num_epochs: int = 5,
    lr: float = 1e-4,
    triad_mode: str = "l1",
):
    """Entraîne le modèle DeepTriadTransformer."""
    device = torch.device(config.device)

    # 1) Encodeur texte (freeze)
    print("🔧 Initialisation de l'encodeur texte...")
    text_encoder = BaseTextEncoder(config.base_text_model_name)

    # 2) Dataset
    print("📊 Construction du dataset séquentiel...")
    dataset = build_deeptriad_dataset(
        jsonl_path=data_path,
        text_encoder=text_encoder,
        max_len=max_len,
    )

    def collate_fn(batch):
        x = torch.stack([b["x"] for b in batch], dim=0)        # (B,max_len,D)
        mask = torch.stack([b["mask"] for b in batch], dim=0)  # (B,max_len)
        triad = torch.stack([b["triad"] for b in batch], dim=0)  # (B,3)
        return {"x": x, "mask": mask, "triad": triad}

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_fn,
    )

    input_dim = dataset.input_dim
    print(f"📐 Dimensions: input_dim={input_dim}, max_seq_len={max_len}")

    # 3) Config DeepTriad
    print("🧠 Création du modèle DeepTriadTransformer...")
    dt_cfg = DeepTriadTransformerConfig(
        d_model=256,
        nhead=4,
        num_layers=2,
        dim_feedforward=512,
        dropout=config.triad_dropout,
        use_triad_control=False,   # ici on apprend la triade brute sans condition
        use_cls_token=True,
        output_mode="cls",
    )

    model = DeepTriadTransformer(input_dim=input_dim, config=dt_cfg).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    criterion = TriadLoss(mode=triad_mode)

    print(f"🚀 Début entraînement - {len(dataset)} séquences\n")

    for epoch in range(1, num_epochs + 1):
        model.train()
        total_loss = 0.0
        count = 0

        for batch in loader:
            x = batch["x"].to(device)         # (B,max_len,D)
            mask = batch["mask"].to(device)   # (B,max_len)
            triad = batch["triad"].to(device) # (B,3)

            # src_key_padding_mask : True = à masquer
            src_key_padding_mask = mask  # (B,max_len)

            optimizer.zero_grad()

            # mode 'cls' -> triad_probs : (B,3)
            triad_probs, _ = model(
                x,
                triad_control=None,
                src_key_padding_mask=src_key_padding_mask,
            )

            loss = criterion(triad_probs, triad)
            loss.backward()
            optimizer.step()

            total_loss += float(loss.item())
            count += 1

        avg_loss = total_loss / max(1, count)
        print(f"[Epoch {epoch}/{num_epochs}] DeepTriad loss={avg_loss:.4f}")

    # Sauvegarde
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": dt_cfg.__dict__,
            "input_dim": input_dim,
        },
        output_path,
    )
    print("✅ DeepTriadTransformer sauvegardé dans:", output_path)


def main():
    parser = argparse.ArgumentParser(description="Train DeepTriadTransformer (seq-level)")
    parser.add_argument("--data", type=str, required=True, help="JSONL avec séquences de chunks + triade globale")
    parser.add_argument("--out", type=str, required=True, help="chemin du checkpoint .pt")
    parser.add_argument("--max_len", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--device", type=str, default="cuda")

    args = parser.parse_args()

    cfg = NumTriadConfig(device=args.device)

    train_deeptriad(
        data_path=Path(args.data),
        output_path=Path(args.out),
        config=cfg,
        max_len=args.max_len,
        batch_size=args.batch_size,
        num_epochs=args.epochs,
        lr=args.lr,
    )


if __name__ == "__main__":
    main()
