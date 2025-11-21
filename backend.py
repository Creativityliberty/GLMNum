#!/usr/bin/env python3
"""
GLM Backend API - Aura Enhanced
==========================================

Full-featured REST API for GLM v4.0 (Aura Model 1).
Port: 8081

Features:
- Aura Conscious Kernel Integration
- Core GLM endpoints (transform, similarity, analyze)
- Unified system endpoints (search, answer, multimodal) - RESTORED
- Complete documentation

Usage:
    uvicorn backend:app --host 0.0.0.0 --port 8081
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uvicorn
import json
import logging

# Import Aura Kernel
from core.aura_system import AuraGLM

# Import Trainer
from numtriad.training.deeptriad_trainer import train_deeptriad_model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Aura GLM API",
    description="Conscious General Language Model - Powered by ∆∞Ο Kernel",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Aura Kernel
logger.info("🧠 Initializing Aura Conscious Kernel...")
aura = AuraGLM()
logger.info("✅ Aura Kernel Ready.")

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class TransformRequest(BaseModel):
    content: str = Field(..., description="Content to transform")
    source_domain: str = Field("text", description="Source domain")
    target_domain: str = Field("text", description="Target domain")
    paradigm: Optional[str] = Field(None, description="Reasoning paradigm to use")

class TransformResponse(BaseModel):
    status: str
    result: str
    source_domain: str
    target_domain: str
    triad: Dict[str, float]
    aura_context: Optional[Dict[str, Any]] = None

class ConsciousnessResponse(BaseModel):
    identity: str
    state: str
    confidence: float
    active_paradigm: str
    recent_thoughts: List[Dict[str, Any]]

class MorphRequest(BaseModel):
    name: str = Field(..., description="Name of the new paradigm")
    parent_a: str = Field(..., description="First parent paradigm")
    parent_b: str = Field(..., description="Second parent paradigm")
    mutation_rate: float = Field(0.1, description="Mutation rate (0.0 - 1.0)")

# Unified System Models (Restored)
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    k: int = Field(5, description="Number of results")
    triad_target: str = Field("auto", description="Triad target mode")

class AnswerRequest(BaseModel):
    query: str = Field(..., description="Question")
    k: int = Field(5, description="Number of documents")
    triad_target_mode: str = Field("auto", description="Triad mode")

class MultimodalRequest(BaseModel):
    texts: Optional[List[str]] = None
    codes: Optional[List[str]] = None
    return_triads: bool = False

class VisionRequest(BaseModel):
    node_ids: List[str] = Field(..., description="Image IDs")
    k: int = Field(5, description="KNN neighbors")

# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """API Root - System Information"""
    return {
        "status": "ok",
        "name": "Aura GLM API",
        "version": "4.0.0",
        "port": 8081,
        "description": "Conscious General Language Model API",
        "endpoints": {
            "health": "GET /health",
            "aura_self": "GET /aura/self",
            "transform": "POST /transform",
            "unified_answer": "POST /unified/answer",
        }
    }

@app.get("/health", tags=["Health"])
async def health():
    """Health Check"""
    return {
        "status": "healthy",
        "service": "Aura GLM API",
        "version": "4.0.0",
        "consciousness": "active"
    }

# ============================================================================
# AURA CONSCIOUSNESS ENDPOINTS
# ============================================================================

@app.get("/aura/self", response_model=ConsciousnessResponse, tags=["Aura Consciousness"])
async def get_self_awareness():
    """Get Aura's current self-awareness state"""
    try:
        self_rep = aura.inner_world.self_representation
        return ConsciousnessResponse(
            identity=self_rep["identity"],
            state=self_rep["current_state"],
            confidence=self_rep["confidence_in_self"],
            active_paradigm=aura.inner_world.active_paradigm,
            recent_thoughts=aura.inner_world.get_recent_thoughts(5)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/aura/paradigm", tags=["Aura Consciousness"])
async def switch_paradigm(paradigm: str):
    """Switch Aura's reasoning paradigm"""
    success = aura.inner_world.switch_paradigm(paradigm)
    if not success:
        raise HTTPException(status_code=400, detail=f"Paradigm '{paradigm}' not found")
    return {"status": "success", "active_paradigm": paradigm}

@app.post("/aura/paradigm/morph", tags=["Aura Consciousness"])
async def morph_paradigm(req: MorphRequest):
    """Create a new paradigm by morphing two existing ones"""
    new_paradigm = aura.inner_world.morph_paradigms(
        req.name, req.parent_a, req.parent_b, req.mutation_rate
    )
    if not new_paradigm:
        raise HTTPException(status_code=400, detail="Could not morph paradigms (parents likely invalid)")
    
    return {
        "status": "success", 
        "new_paradigm": new_paradigm,
        "message": f"Morphed {req.parent_a} + {req.parent_b} -> {req.name}"
    }

# ============================================================================
# CORE ENDPOINTS (Enhanced with Aura)
# ============================================================================

@app.post("/transform", response_model=TransformResponse, tags=["Core"])
async def transform(req: TransformRequest):
    """Transform Content using Aura's Conscious Processing"""
    try:
        # Process through Aura Kernel
        result = aura.process_query(req.content, paradigm=req.paradigm)
        
        # Extract Triadic Metrics
        triadic_metrics = result.get("triadic_analysis", {})
        triad_vector = {
            "delta": 0.33,
            "infinity": triadic_metrics.get("transformation", {}).get("coherence", 0.5),
            "theta": triadic_metrics.get("classical_outcome", {}).get("confidence", 0.5)
        }

        return TransformResponse(
            status="success",
            result=result["response"],
            source_domain=req.source_domain,
            target_domain=req.target_domain,
            triad=triad_vector,
            aura_context={
                "quality_score": result["quality_assessment"]["quality_score"],
                "phases_completed": result["phases_completed"],
                "duration": result["duration"]
            }
        )
    except Exception as e:
        logger.error(f"Transformation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# UNIFIED SYSTEM ENDPOINTS (Restored & Connected to Aura)
# ============================================================================

@app.post("/unified/answer", tags=["Unified"])
async def unified_answer(req: AnswerRequest):
    """Generate Answer using Aura Conscious Kernel"""
    try:
        logger.info(f"Aura answering: {req.query}")
        
        # Use Aura to process the query
        result = aura.process_query(req.query)
        
        # Map Aura response to Unified API format
        return {
            "status": "success",
            "query": req.query,
            "answer": result["response"],
            "style": "conscious",
            "triad_question": {
                "delta": 0.4,
                "infinity": 0.4,
                "theta": 0.2
            },
            "num_documents": 0, # Placeholder
            "confidence": result["quality_assessment"]["quality_score"],
            "aura_thoughts": result["inner_thoughts"]
        }
    except Exception as e:
        logger.error(f"Unified Answer error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/unified/search", tags=["Unified"])
async def unified_search(req: SearchRequest):
    """Simulate search for now"""
    return {
        "status": "success",
        "query": req.query,
        "num_results": 0,
        "results": []
    }

@app.post("/unified/multimodal", tags=["Unified"])
async def unified_multimodal(req: MultimodalRequest):
    """Multimodal placeholder"""
    return {
        "status": "success",
        "embedding_shape": [1, 419],
        "triad_probs": [0.33, 0.33, 0.34]
    }

@app.get("/unified/stats", tags=["Unified"])
async def unified_stats():
    """Get System Statistics"""
    return {
        "status": "success",
        "system": {
            "rag_index": {"num_documents": 0},
            "gemini_wrapper": {"available": True, "model": "Aura Model 1"}
        }
    }

# ============================================================================
# VISION ENDPOINTS (Placeholders)
# ============================================================================

@app.post("/vision/add", tags=["Vision"])
async def vision_add(req: VisionRequest):
    return {"status": "success", "num_added": len(req.node_ids)}

@app.post("/vision/connect", tags=["Vision"])
async def vision_connect(req: VisionRequest):
    return {"status": "success", "k": req.k}

@app.post("/vision/path", tags=["Vision"])
async def vision_path(source: str, target: str):
    return {"status": "success", "path": [source, target]}


# ============================================================================
# TRAINING ENDPOINTS
# ============================================================================

class TrainingRequest(BaseModel):
    data_path: str = Field(..., description="Path to JSONL data")
    output_path: str = Field("checkpoints/model.pt", description="Where to save model")
    epochs: int = Field(3, description="Number of epochs")
    device: str = Field("cpu", description="Device (cpu/cuda)")

@app.post("/training/start", tags=["Training"])
async def start_training(req: TrainingRequest, background_tasks: BackgroundTasks):
    """Start DeepTriad Training in background"""
    
    def run_training():
        logger.info(f"Starting background training: {req.data_path}")
        result = train_deeptriad_model(
            data_path=req.data_path,
            output_path=req.output_path,
            num_epochs=req.epochs,
            device=req.device
        )
        logger.info(f"Training finished: {result}")

    background_tasks.add_task(run_training)
    
    return {
        "status": "accepted",
        "message": "Training started in background",
        "config": {
            "data": req.data_path,
            "epochs": req.epochs,
            "device": req.device
        }
    }

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 Aura GLM Backend API v4.0")
    print("   Powered by NumTriad™ - Property of Lionel Numtema")
    print("="*70)
    print("📍 Starting on http://0.0.0.0:8081")
    print("🧠 Consciousness: ACTIVE")
    print("="*70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8081,
        log_level="info"
    )
