#!/usr/bin/env python3
"""
Script d'entraînement TriadFusionHeadV3 (multimodal).
Utilisation:
python scripts/train_triad_fusion_v3.py \
  --data data/numtriad_multimodal.jsonl \
  --images_root data/ \
  --out checkpoints/triad_fusion_v3.pt \
  --epochs 5 \
  --batch_size 16 \
  --lr 1e-4 \
  --device cuda
"""

import argparse
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from numtriad.config import NumTriadConfig
from numtriad.encoders.base_text_encoder import BaseTextEncoder
from numtriad.encoders.vision_encoder import VisionEncoder
from numtriad.data.multimodal_dataset import build_multimodal_dataset
from numtriad.models.triad_fusion_head_v3 import TriadFusionHeadV3
from numtriad.losses import TriadLoss


def train_triad_fusion_v3(
    data_path: Path,
    output_path: Path,
    config: NumTriadConfig,
    images_root: Path,
    batch_size: int = 16,
    num_epochs: int = 5,
    lr: float = 1e-4,
    triad_mode: str = "l1",
):
    """Entraîne le modèle TriadFusionHeadV3."""
    device = torch.device(config.device)

    # 1) Encoders freeze
    print("🔧 Initialisation des encodeurs...")
    text_encoder = BaseTextEncoder(config.base_text_model_name)
    vision_encoder = VisionEncoder(device=config.device)

    print("📊 Construction du dataset multimodal...")
    dataset = build_multimodal_dataset(
        jsonl_path=data_path,
        text_encoder=text_encoder,
        vision_encoder=vision_encoder,
        use_ling_feats=config.use_linguistic_features,
        images_root=images_root,
    )

    def collate_fn(batch):
        # batch : list of items from MultiModalTriadDataset.__getitem__
        triad = torch.stack([b["triad"] for b in batch], dim=0)
        text_embs = [b.get("text_emb") for b in batch]
        vis_embs = [b.get("vis_emb") for b in batch]
        feats = [b.get("feats") for b in batch if "feats" in b]

        # Some samples may not have text or vision, but in notre dataset on a tout encodé
        if text_embs[0] is not None:
            text_emb = torch.stack(text_embs, dim=0)
        else:
            text_emb = None

        if vis_embs[0] is not None:
            vis_emb = torch.stack(vis_embs, dim=0)
        else:
            vis_emb = None

        if len(feats) > 0:
            feats_t = torch.stack([b["feats"] for b in batch], dim=0)
        else:
            feats_t = None

        return {
            "triad": triad,
            "text_emb": text_emb,
            "vis_emb": vis_emb,
            "feats": feats_t,
        }

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_fn,
    )

    # 2) Dimensions
    text_dim = dataset.text_embeddings.shape[1] if dataset.text_embeddings is not None else 0
    vis_dim = dataset.vision_embeddings.shape[1] if dataset.vision_embeddings is not None else 0
    feat_dim = dataset.linguistic_features.shape[1] if dataset.linguistic_features is not None else 0

    print(f"📐 Dimensions: text={text_dim}, vision={vis_dim}, features={feat_dim}")

    # 3) Modèle
    print("🧠 Création du modèle TriadFusionHeadV3...")
    model = TriadFusionHeadV3(
        text_dim=text_dim,
        vision_dim=vis_dim,
        feat_dim=feat_dim,
        hidden_dim=max(512, config.triad_hidden_dim),
        dropout=config.triad_dropout,
    ).to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    criterion = TriadLoss(mode=triad_mode)

    print(f"🚀 Début entraînement - {len(dataset)} samples\n")

    for epoch in range(1, num_epochs + 1):
        model.train()
        total_loss = 0.0
        count = 0

        for batch in loader:
            triad = batch["triad"].to(device)  # (B,3)

            text_emb = batch["text_emb"]
            if text_emb is not None:
                text_emb = text_emb.to(device)
            else:
                # vecteur nul si pas de texte
                text_emb = torch.zeros(
                    triad.size(0), text_dim, device=device, dtype=torch.float32
                )

            vis_emb = batch["vis_emb"]
            if vis_emb is not None:
                vis_emb = vis_emb.to(device)
            else:
                vis_emb = torch.zeros(
                    triad.size(0), vis_dim, device=device, dtype=torch.float32
                )

            feats = batch["feats"]
            if feats is not None:
                feats = feats.to(device)

            optimizer.zero_grad()
            pred = model(text_emb, vis_emb, feats)  # (B,3)
            loss = criterion(pred, triad)

            loss.backward()
            optimizer.step()

            total_loss += float(loss.item())
            count += 1

        avg_loss = total_loss / max(1, count)
        print(f"[Epoch {epoch}/{num_epochs}] Loss={avg_loss:.4f}")

    # 4) Sauvegarde
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": config.__dict__,
            "text_dim": text_dim,
            "vision_dim": vis_dim,
            "feat_dim": feat_dim,
        },
        output_path,
    )
    print("✅ TriadFusionHeadV3 sauvegardé dans:", output_path)


def main():
    parser = argparse.ArgumentParser(description="Train TriadFusionHeadV3 (multimodal)")
    parser.add_argument("--data", type=str, required=True, help="JSONL multimodal annoté")
    parser.add_argument("--images_root", type=str, required=True, help="Racine des images")
    parser.add_argument("--out", type=str, required=True, help="Chemin checkpoint .pt")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--device", type=str, default="cuda")

    args = parser.parse_args()

    cfg = NumTriadConfig(device=args.device)

    train_triad_fusion_v3(
        data_path=Path(args.data),
        output_path=Path(args.out),
        config=cfg,
        images_root=Path(args.images_root),
        batch_size=args.batch_size,
        num_epochs=args.epochs,
        lr=args.lr,
    )


if __name__ == "__main__":
    main()
