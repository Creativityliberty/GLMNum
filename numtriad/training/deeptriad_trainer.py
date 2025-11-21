"""
NumTriad Training Module
========================
Logic for training DeepTriad models directly from the system.
"""

import logging
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

logger = logging.getLogger(__name__)

def train_deeptriad_model(
    data_path: str,
    output_path: str,
    max_len: int = 32,
    batch_size: int = 8,
    num_epochs: int = 5,
    lr: float = 1e-4,
    device: str = "cpu"  # Default to CPU for compatibility
):
    """
    Train DeepTriadTransformer model.
    Designed to be called from Aura System or API.
    """
    logger.info(f"🚀 Starting DeepTriad Training on {device}...")
    
    config = NumTriadConfig(device=device)
    device_obj = torch.device(device)
    
    # 1) Text Encoder
    logger.info("🔧 Initializing Text Encoder...")
    try:
        text_encoder = BaseTextEncoder(config.base_text_model_name)
    except Exception as e:
        logger.error(f"Failed to load text encoder: {e}")
        return {"status": "error", "message": str(e)}

    # 2) Dataset
    logger.info("📊 Building Dataset...")
    try:
        dataset = build_deeptriad_dataset(
            jsonl_path=Path(data_path),
            text_encoder=text_encoder,
            max_len=max_len,
        )
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        return {"status": "error", "message": f"Dataset error: {e}"}

    def collate_fn(batch):
        x = torch.stack([b["x"] for b in batch], dim=0)
        mask = torch.stack([b["mask"] for b in batch], dim=0)
        triad = torch.stack([b["triad"] for b in batch], dim=0)
        return {"x": x, "mask": mask, "triad": triad}

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_fn,
    )

    input_dim = dataset.input_dim
    
    # 3) Model
    logger.info("🧠 Creating DeepTriad Transformer...")
    dt_cfg = DeepTriadTransformerConfig(
        d_model=256,
        nhead=4,
        num_layers=2,
        dim_feedforward=512,
        dropout=config.triad_dropout,
        use_triad_control=False,
        use_cls_token=True,
        output_mode="cls",
    )

    model = DeepTriadTransformer(input_dim=input_dim, config=dt_cfg).to(device_obj)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    criterion = TriadLoss(mode="l1")

    # Training Loop
    metrics = []
    for epoch in range(1, num_epochs + 1):
        model.train()
        total_loss = 0.0
        count = 0

        for batch in loader:
            x = batch["x"].to(device_obj)
            mask = batch["mask"].to(device_obj)
            triad = batch["triad"].to(device_obj)
            src_key_padding_mask = mask

            optimizer.zero_grad()
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
        logger.info(f"[Epoch {epoch}/{num_epochs}] Loss={avg_loss:.4f}")
        metrics.append({"epoch": epoch, "loss": avg_loss})

    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": dt_cfg.__dict__,
            "input_dim": input_dim,
        },
        output_path,
    )
    logger.info(f"✅ Model saved to {output_path}")
    
    return {
        "status": "success",
        "output_path": output_path,
        "metrics": metrics,
        "epochs_completed": num_epochs
    }
