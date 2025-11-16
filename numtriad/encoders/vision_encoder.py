# numtriad/encoders/vision_encoder.py

from typing import List, Optional

import torch
import torch.nn as nn
import numpy as np

try:
    import torchvision.models as models
    from torchvision import transforms
except ImportError:
    models = None
    transforms = None


class VisionEncoder(nn.Module):
    """
    Encodeur vision simple basé sur ResNet50 pré-entraîné.
    Produit un vecteur v_vis de dimension fixe.
    """

    def __init__(self, device: str = "cuda"):
        super().__init__()
        if models is None:
            raise ImportError(
                "torchvision n'est pas installé. "
                "pip install torchvision"
            )
        self.device = torch.device(device)

        backbone = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        # on enlève la dernière couche FC, on garde le penultimate
        self.backbone = nn.Sequential(*list(backbone.children())[:-1])  # (B, 2048, 1,1)
        self.backbone.to(self.device)
        self.backbone.eval()

        self._dim = 2048

        # Transforms standard ImageNet
        self.preprocess = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ]
        )

    @property
    def dim(self) -> int:
        return self._dim

    @torch.no_grad()
    def encode(self, images: List["PIL.Image.Image"]) -> np.ndarray:
        """
        images: liste de PIL Images
        retourne: (batch, dim)
        """
        self.eval()
        tensors = [self.preprocess(img) for img in images]
        batch = torch.stack(tensors, dim=0).to(self.device)  # (B,3,224,224)
        feats = self.backbone(batch)  # (B,2048,1,1)
        feats = feats.view(feats.size(0), -1)  # (B,2048)
        return feats.cpu().numpy()
