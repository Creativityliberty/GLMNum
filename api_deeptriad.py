"""
GLM API Extension - DeepTriad Transformer Integration
======================================================

Extension de l'API GLM pour intégrer DeepTriad Transformer (Pilier 3)
Permet l'analyse au niveau séquence avec prédiction de triades globales.

Author: GLM Research Team
Date: 2024-11-16
"""

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import sys
import os
import numpy as np
import torch

# Import NumTriad components
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from numtriad.encoders.base_text_encoder import BaseTextEncoder
from numtriad.models.deeptriad_transformer import DeepTriadTransformer, DeepTriadTransformerConfig
from numtriad.triad_types import Triad
from numtriad.config import NumTriadConfig

# ============================================================================
# MODELS
# ============================================================================

class TriadScore(BaseModel):
    """Triad score representation"""
    delta: float = Field(..., ge=0.0, le=1.0, description="Complexity/Granularity")
    infinity: float = Field(..., ge=0.0, le=1.0, description="Generality/Abstraction")
    theta: float = Field(..., ge=0.0, le=1.0, description="Concreteness/Spatiality")


class DeepTriadAnalysisRequest(BaseModel):
    """Request for DeepTriad sequence analysis"""
    chunks: List[str] = Field(..., description="List of text chunks to analyze")
    max_len: int = Field(default=32, description="Maximum sequence length")
    
    class Config:
        schema_extra = {
            "example": {
                "chunks": [
                    "Concept théorique abstrait",
                    "Formalisation mathématique",
                    "Application pratique"
                ],
                "max_len": 32
            }
        }


class DeepTriadAnalysisResponse(BaseModel):
    """Response for DeepTriad analysis"""
    global_triad: TriadScore = Field(..., description="Global triad for the sequence")
    num_chunks: int = Field(..., description="Number of chunks analyzed")
    sequence_length: int = Field(..., description="Actual sequence length")
    abstraction_level: str = Field(..., description="Abstraction level (abstract/mixed/concrete)")
    insights: Dict[str, Any] = Field(..., description="Analysis insights")


class DeepTriadBatchRequest(BaseModel):
    """Request for batch DeepTriad analysis"""
    documents: List[Dict[str, Any]] = Field(..., description="List of documents with chunks")
    
    class Config:
        schema_extra = {
            "example": {
                "documents": [
                    {
                        "id": "doc1",
                        "chunks": ["Texte 1", "Texte 2", "Texte 3"]
                    },
                    {
                        "id": "doc2",
                        "chunks": ["Autre texte 1", "Autre texte 2"]
                    }
                ]
            }
        }


class DeepTriadBatchResponse(BaseModel):
    """Response for batch DeepTriad analysis"""
    results: List[Dict[str, Any]] = Field(..., description="Analysis results per document")
    total_documents: int = Field(..., description="Total documents processed")


# ============================================================================
# DEEPTRIAD MANAGER
# ============================================================================

class DeepTriadManager:
    """Gestionnaire pour DeepTriad Transformer"""
    
    def __init__(self):
        self.model = None
        self.text_encoder = None
        self.config = None
        self.device = torch.device("cpu")
        self.initialized = False
    
    def initialize(self, checkpoint_path: Optional[str] = None):
        """Initialise DeepTriad avec checkpoint optionnel"""
        try:
            self.config = NumTriadConfig(device="cpu")
            self.text_encoder = BaseTextEncoder(self.config.base_text_model_name)
            
            if checkpoint_path and os.path.exists(checkpoint_path):
                # Charger depuis checkpoint
                ckpt = torch.load(checkpoint_path, map_location="cpu")
                dt_cfg = DeepTriadTransformerConfig(**ckpt["config"])
                input_dim = ckpt["input_dim"]
                
                self.model = DeepTriadTransformer(input_dim=input_dim, config=dt_cfg)
                self.model.load_state_dict(ckpt["model_state_dict"])
                self.model.eval()
                print(f"✅ DeepTriad loaded from {checkpoint_path}")
            else:
                # Créer nouveau modèle
                dt_cfg = DeepTriadTransformerConfig(
                    d_model=256,
                    nhead=4,
                    num_layers=2,
                    output_mode="cls",
                    use_cls_token=True,
                )
                self.model = DeepTriadTransformer(input_dim=384, config=dt_cfg)
                self.model.eval()
                print("✅ DeepTriad initialized (untrained)")
            
            self.initialized = True
        except Exception as e:
            print(f"❌ Failed to initialize DeepTriad: {e}")
            self.initialized = False
    
    def analyze_sequence(self, chunks: List[str], max_len: int = 32) -> Dict[str, Any]:
        """Analyse une séquence de chunks"""
        if not self.initialized:
            raise ValueError("DeepTriad not initialized")
        
        if len(chunks) == 0:
            raise ValueError("Empty chunk list")
        
        # Encoder chunks
        embs = self.text_encoder.encode(chunks)  # (L, 384)
        
        # Préparer input
        L = min(len(chunks), max_len)
        x = np.zeros((max_len, 384), dtype="float32")
        mask = np.ones((max_len,), dtype=bool)
        
        x[:L, :] = embs[:L, :]
        mask[:L] = False
        
        # Prédire triade
        x_t = torch.tensor(x, dtype=torch.float32).unsqueeze(0)
        mask_t = torch.tensor(mask, dtype=torch.bool).unsqueeze(0)
        
        with torch.no_grad():
            triads = self.model.predict_triad_global(x_t, src_key_padding_mask=mask_t)
        
        triad = triads[0]
        
        # Déterminer niveau d'abstraction
        if triad.theta > 0.7:
            level = "concrete"
        elif triad.infinity > 0.7:
            level = "abstract"
        else:
            level = "mixed"
        
        return {
            "triad": {
                "delta": float(triad.delta),
                "infinity": float(triad.infinity),
                "theta": float(triad.theta),
            },
            "num_chunks": len(chunks),
            "sequence_length": L,
            "abstraction_level": level,
            "insights": {
                "complexity": float(triad.delta),
                "generality": float(triad.infinity),
                "concreteness": float(triad.theta),
            }
        }


# ============================================================================
# GLOBAL MANAGER
# ============================================================================

deeptriad_manager = DeepTriadManager()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_deeptriad_routes(app: FastAPI):
    """Crée les routes DeepTriad dans l'app FastAPI"""
    
    @app.on_event("startup")
    async def init_deeptriad():
        """Initialise DeepTriad au démarrage"""
        checkpoint = "checkpoints/deeptriad_transformer_v1.pt"
        deeptriad_manager.initialize(checkpoint if os.path.exists(checkpoint) else None)
    
    @app.post("/deeptriad/analyze", response_model=DeepTriadAnalysisResponse)
    async def analyze_sequence(request: DeepTriadAnalysisRequest):
        """
        Analyse une séquence de chunks avec DeepTriad Transformer
        
        Retourne la triade globale (∆∞Ο) pour la séquence.
        """
        try:
            if not deeptriad_manager.initialized:
                raise HTTPException(
                    status_code=503,
                    detail="DeepTriad not initialized"
                )
            
            result = deeptriad_manager.analyze_sequence(
                chunks=request.chunks,
                max_len=request.max_len
            )
            
            return DeepTriadAnalysisResponse(
                global_triad=TriadScore(**result["triad"]),
                num_chunks=result["num_chunks"],
                sequence_length=result["sequence_length"],
                abstraction_level=result["abstraction_level"],
                insights=result["insights"]
            )
        
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    
    @app.post("/deeptriad/batch", response_model=DeepTriadBatchResponse)
    async def batch_analyze(request: DeepTriadBatchRequest):
        """
        Analyse un batch de documents avec DeepTriad
        """
        try:
            if not deeptriad_manager.initialized:
                raise HTTPException(
                    status_code=503,
                    detail="DeepTriad not initialized"
                )
            
            results = []
            for doc in request.documents:
                doc_id = doc.get("id", "unknown")
                chunks = doc.get("chunks", [])
                
                if not chunks:
                    results.append({
                        "id": doc_id,
                        "error": "No chunks provided"
                    })
                    continue
                
                try:
                    result = deeptriad_manager.analyze_sequence(chunks)
                    results.append({
                        "id": doc_id,
                        "triad": result["triad"],
                        "abstraction_level": result["abstraction_level"],
                        "num_chunks": result["num_chunks"],
                    })
                except Exception as e:
                    results.append({
                        "id": doc_id,
                        "error": str(e)
                    })
            
            return DeepTriadBatchResponse(
                results=results,
                total_documents=len(request.documents)
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    
    @app.get("/deeptriad/status")
    async def deeptriad_status():
        """Retourne le statut de DeepTriad"""
        return {
            "initialized": deeptriad_manager.initialized,
            "model": "DeepTriadTransformer" if deeptriad_manager.model else None,
            "text_encoder": "BaseTextEncoder" if deeptriad_manager.text_encoder else None,
            "device": str(deeptriad_manager.device),
        }


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "create_deeptriad_routes",
    "deeptriad_manager",
    "DeepTriadAnalysisRequest",
    "DeepTriadAnalysisResponse",
    "DeepTriadBatchRequest",
    "DeepTriadBatchResponse",
]
