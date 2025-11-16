"""
GLM Prototype - REST API
=========================

API REST pour le General Language Model (GLM)

Author: GLM Research Team
Date: 2024-11-15

Usage:
    uvicorn api:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import sys
import traceback
import os

# Import GLM components
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.symbolic import SymbolicEngine, SymbolicOperations
from domains.geometric import GeometricDomain, Polygon, Circle
from domains.text import TextDomain
from domains.code import CodeDomain
try:
    from api_deeptriad import create_deeptriad_routes
except ImportError:
    print("⚠️ DeepTriad routes not available (torch not installed)")
    def create_deeptriad_routes(app, engine):
        pass

try:
    from numtriad.system_integration import get_unified_system
except ImportError:
    print("⚠️ Unified system not available")
    def get_unified_system():
        return None

# ============================================================================
# INITIALIZATION
# ============================================================================

# Create FastAPI app
app = FastAPI(
    title="GLM API",
    description="General Language Model API - Transform concepts across domains using ∆∞Ο",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize GLM Engine
engine = SymbolicEngine(embedding_dim=128)
engine.register_domain(GeometricDomain(embedding_dim=128))
engine.register_domain(TextDomain(embedding_dim=128))
engine.register_domain(CodeDomain(embedding_dim=128))

print("✓ GLM API initialized with domains:", engine.list_domains())

# Initialize DeepTriad routes
try:
    create_deeptriad_routes(app, engine)
    print("✓ DeepTriad routes initialized")
except Exception as e:
    print(f"⚠️ DeepTriad routes initialization failed: {e}")

# Initialize Unified System
try:
    unified_system = get_unified_system()
    if unified_system:
        print("✓ Unified system initialized")
except Exception as e:
    print(f"⚠️ Unified system initialization failed: {e}")
    unified_system = None

# ============================================================================
# MODELS
# ============================================================================

class TransformRequest(BaseModel):
    """Request model for transformation"""
    content: str = Field(..., description="Content to transform (text, code, or geometric description)")
    source_domain: str = Field(..., description="Source domain (text, code, geometry)")
    target_domain: str = Field(..., description="Target domain (text, code, geometry)")
    
    class Config:
        schema_extra = {
            "example": {
                "content": "def hello(): return 'world'",
                "source_domain": "code",
                "target_domain": "text"
            }
        }


class SymbolicRepresentationResponse(BaseModel):
    """Response model for symbolic representation"""
    delta_norm: float = Field(..., description="Norm of Delta (essence) vector")
    infinity_nodes: int = Field(..., description="Number of nodes in Infinity (process) graph")
    infinity_edges: int = Field(..., description="Number of edges in Infinity graph")
    omega_norm: float = Field(..., description="Norm of Omega (completeness) vector")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")


class TransformResponse(BaseModel):
    """Response model for transformation"""
    result: str = Field(..., description="Transformed content")
    source_symbolic: SymbolicRepresentationResponse
    target_symbolic: Optional[SymbolicRepresentationResponse] = None
    similarity_score: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "result": "A function named 'hello' that returns the string 'world'",
                "source_symbolic": {
                    "delta_norm": 1.0,
                    "infinity_nodes": 15,
                    "infinity_edges": 10,
                    "omega_norm": 1.0,
                    "metadata": {"domain": "code"}
                },
                "similarity_score": 0.85
            }
        }


class SimilarityRequest(BaseModel):
    """Request model for similarity computation"""
    content1: str
    content2: str
    domain: str = Field(..., description="Domain (text, code, geometry)")


class SimilarityResponse(BaseModel):
    """Response model for similarity"""
    similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity score [0, 1]")
    content1_symbolic: SymbolicRepresentationResponse
    content2_symbolic: SymbolicRepresentationResponse


class AnalyzeRequest(BaseModel):
    """Request model for content analysis"""
    content: str
    domain: str


class AnalyzeResponse(BaseModel):
    """Response model for analysis"""
    symbolic: SymbolicRepresentationResponse
    insights: Dict[str, Any] = Field(..., description="Domain-specific insights")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def symbolic_to_response(symbolic) -> SymbolicRepresentationResponse:
    """Convert SymbolicRepresentation to response model"""
    import numpy as np
    return SymbolicRepresentationResponse(
        delta_norm=float(np.linalg.norm(symbolic.delta)),
        infinity_nodes=symbolic.infinity.number_of_nodes(),
        infinity_edges=symbolic.infinity.number_of_edges(),
        omega_norm=float(np.linalg.norm(symbolic.omega)),
        metadata=symbolic.metadata
    )


def parse_geometric_content(content: str) -> Any:
    """Parse geometric description"""
    content = content.lower().strip()
    
    if 'triangle' in content:
        return Polygon(sides=3)
    elif 'square' in content or 'quadrilateral' in content:
        return Polygon(sides=4)
    elif 'pentagon' in content:
        return Polygon(sides=5)
    elif 'hexagon' in content:
        return Polygon(sides=6)
    elif 'circle' in content:
        return Circle()
    elif 'polygon' in content:
        # Extract number of sides
        import re
        match = re.search(r'(\d+)', content)
        if match:
            sides = int(match.group(1))
            return Polygon(sides=sides)
    
    # Default
    return Polygon(sides=3)


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GLM API - General Language Model with DeepTriad",
        "version": "0.2.0",
        "docs": "/docs",
        "available_domains": engine.list_domains(),
        "endpoints": {
            "GLM Core": {
                "POST /transform": "Transform content across domains",
                "POST /similarity": "Compute similarity between contents",
                "POST /analyze": "Analyze content in a domain",
                "GET /domains": "List available domains",
                "GET /stats": "Get engine statistics",
            },
            "DeepTriad (Pilier 3)": {
                "POST /deeptriad/analyze": "Analyze sequence with DeepTriad Transformer",
                "POST /deeptriad/batch": "Batch analyze documents",
                "GET /deeptriad/status": "DeepTriad status",
            },
            "System": {
                "GET /health": "Health check"
            }
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "engine": "operational",
        "domains": engine.list_domains(),
        "stats": engine.get_stats()
    }


@app.get("/domains")
async def list_domains():
    """List available domains"""
    return {
        "domains": engine.list_domains(),
        "count": len(engine.list_domains()),
        "descriptions": {
            "geometry": "Geometric shapes (Triangle, Polygon, Circle)",
            "text": "Natural language text",
            "code": "Python code (via AST)"
        }
    }


@app.get("/stats")
async def get_stats():
    """Get engine statistics"""
    stats = engine.get_stats()
    return {
        "statistics": stats,
        "domains": {
            domain: {
                "name": domain,
                "type": engine.get_domain(domain).__class__.__name__
            }
            for domain in engine.list_domains()
        }
    }


@app.post("/transform", response_model=TransformResponse)
async def transform(request: TransformRequest):
    """
    Transform content across domains
    
    This endpoint takes content in one domain and transforms it to another domain
    using the symbolic ∆∞Ο representation.
    
    Example:
        - Code → Text: Transform Python code to natural language description
        - Text → Code: Transform natural language to Python code (conceptual)
        - Geometry → Text: Describe a geometric shape in words
    """
    try:
        # Validate domains
        if request.source_domain not in engine.list_domains():
            raise HTTPException(
                status_code=400,
                detail=f"Unknown source domain: {request.source_domain}. Available: {engine.list_domains()}"
            )
        
        if request.target_domain not in engine.list_domains():
            raise HTTPException(
                status_code=400,
                detail=f"Unknown target domain: {request.target_domain}. Available: {engine.list_domains()}"
            )
        
        # Parse content based on source domain
        source_content = request.content
        
        if request.source_domain == "geometry":
            source_content = parse_geometric_content(request.content)
        
        # Encode to symbolic
        symbolic = engine.abstract(source_content, request.source_domain)
        
        # Decode to target domain
        if request.target_domain == "geometry":
            result = engine.concretize(symbolic, request.target_domain)
            result_str = str(result)
        elif request.target_domain == "text":
            # For code → text or geometry → text
            if request.source_domain == "code":
                result_str = f"This code {symbolic.metadata.get('code_preview', 'performs a computation')}"
                if symbolic.metadata.get('num_functions', 0) > 0:
                    result_str += f" and defines {symbolic.metadata['num_functions']} function(s)"
                if symbolic.metadata.get('num_classes', 0) > 0:
                    result_str += f" and {symbolic.metadata['num_classes']} class(es)"
            elif request.source_domain == "geometry":
                result_str = f"A geometric shape: {source_content}"
            else:
                result_str = engine.concretize(symbolic, request.target_domain)
        elif request.target_domain == "code":
            result_str = engine.concretize(symbolic, request.target_domain)
        else:
            result_str = engine.concretize(symbolic, request.target_domain)
        
        return TransformResponse(
            result=result_str,
            source_symbolic=symbolic_to_response(symbolic),
            similarity_score=None
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}\n{traceback.format_exc()}")


@app.post("/similarity", response_model=SimilarityResponse)
async def compute_similarity(request: SimilarityRequest):
    """
    Compute similarity between two contents in the same domain
    
    Returns a similarity score between 0 and 1:
    - 1.0 = identical
    - 0.0 = completely different
    """
    try:
        if request.domain not in engine.list_domains():
            raise HTTPException(
                status_code=400,
                detail=f"Unknown domain: {request.domain}. Available: {engine.list_domains()}"
            )
        
        # Parse contents
        content1 = request.content1
        content2 = request.content2
        
        if request.domain == "geometry":
            content1 = parse_geometric_content(request.content1)
            content2 = parse_geometric_content(request.content2)
        
        # Encode both
        sym1 = engine.abstract(content1, request.domain)
        sym2 = engine.abstract(content2, request.domain)
        
        # Compute similarity
        similarity = SymbolicOperations.similarity(sym1, sym2)
        
        return SimilarityResponse(
            similarity=float(similarity),
            content1_symbolic=symbolic_to_response(sym1),
            content2_symbolic=symbolic_to_response(sym2)
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Analyze content in a specific domain
    
    Returns the symbolic representation and domain-specific insights
    """
    try:
        if request.domain not in engine.list_domains():
            raise HTTPException(
                status_code=400,
                detail=f"Unknown domain: {request.domain}. Available: {engine.list_domains()}"
            )
        
        # Parse content
        content = request.content
        
        if request.domain == "geometry":
            content = parse_geometric_content(request.content)
        
        # Encode
        symbolic = engine.abstract(content, request.domain)
        
        # Domain-specific insights
        insights = {}
        
        if request.domain == "code":
            insights = {
                "num_functions": symbolic.metadata.get('num_functions', 0),
                "num_classes": symbolic.metadata.get('num_classes', 0),
                "lines": symbolic.metadata.get('lines', 0),
                "preview": symbolic.metadata.get('code_preview', '')
            }
        elif request.domain == "text":
            insights = {
                "length": symbolic.metadata.get('length', 0),
                "words": symbolic.metadata.get('words', 0),
                "preview": symbolic.metadata.get('text_preview', '')
            }
        elif request.domain == "geometry":
            insights = symbolic.metadata
        
        return AnalyzeResponse(
            symbolic=symbolic_to_response(symbolic),
            insights=insights
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# ============================================================================
# UNIFIED SYSTEM ENDPOINTS
# ============================================================================

@app.post("/unified/index")
async def unified_index(request: Dict[str, Any]):
    """Index documents in unified system"""
    if not unified_system:
        raise HTTPException(status_code=503, detail="Unified system not available")
    
    try:
        texts = request.get("texts", [])
        metadatas = request.get("metadatas")
        ids = request.get("ids")
        
        unified_system.index_documents(texts, metadatas=metadatas, ids=ids)
        
        return {
            "status": "success",
            "num_indexed": len(texts),
            "message": f"Indexed {len(texts)} documents"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/unified/search")
async def unified_search(request: Dict[str, Any]):
    """Search with triad-aware ranking"""
    try:
        query = request.get("query", "")
        k = request.get("k", 5)
        triad_target = request.get("triad_target", "auto")
        
        results = unified_system.search(query, k=k, triad_target=triad_target)
        
        return {
            "status": "success",
            "query": query,
            "triad_target": triad_target,
            "results": results,
            "num_results": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/unified/answer")
async def unified_answer(request: Dict[str, Any]):
    """Generate answer with Gemini + triad-aware context"""
    try:
        query = request.get("query", "")
        k = request.get("k", 5)
        triad_target_mode = request.get("triad_target_mode", "auto")
        
        result = unified_system.answer(
            query=query,
            k=k,
            triad_target_mode=triad_target_mode
        )
        
        return {
            "status": "success",
            "query": query,
            "answer": result.get("answer"),
            "triad_question": result.get("triad_question"),
            "style": result.get("style"),
            "num_documents": result.get("metadata", {}).get("num_documents", 0),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/unified/multimodal")
async def unified_multimodal(request: Dict[str, Any]):
    """Encode multimodal content"""
    try:
        texts = request.get("texts")
        codes = request.get("codes")
        return_triads = request.get("return_triads", False)
        
        result = unified_system.encode_multimodal(
            texts=texts,
            codes=codes,
            return_triads=return_triads
        )
        
        return {
            "status": "success",
            "embedding_shape": list(result["embedding"].shape) if hasattr(result["embedding"], "shape") else None,
            "triad_probs": result.get("triad_probs"),
            "triads": [str(t) for t in result.get("triads", [])] if return_triads else None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/unified/stats")
async def unified_stats():
    """Get system statistics"""
    try:
        stats = unified_system.get_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    print("\n" + "=" * 70)
    print("  GLM API Starting")
    print("=" * 70)
    print(f"  Domains: {engine.list_domains()}")
    print(f"  Version: 0.1.0")
    print("=" * 70 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    print("\n" + "=" * 70)
    print("  GLM API Shutting down")
    print("  Stats:", engine.get_stats())
    print("=" * 70 + "\n")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser(description="GLM API Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to run server on (default: 8080)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    
    args = parser.parse_args()
    
    print(f"🚀 Starting GLM API on {args.host}:{args.port}")
    print(f"📖 Documentation: http://localhost:{args.port}/docs")
    print(f"🔍 ReDoc: http://localhost:{args.port}/redoc\n")
    
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
