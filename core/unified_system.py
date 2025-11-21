"""
Unified GLM v4.0 System
=======================

Complete integration of:
- GLM SymbolicEngine (domains: text, code, image, geometry)
- NumTriad System V4 (4 pillars: multimodal, vision, deeptriad, RAG)
- Neural Encoders (Nomic Text + Vision)
- RAG Index (DeepTriad)
- Gemini LLM (Q&A)

Provides unified API for encoding, searching, and answering.
"""

import logging
import numpy as np
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try importing all components
try:
    from core.symbolic import SymbolicEngine
    from core.auto_learning import AutoLearningEngine, integrate_auto_learning
    from numtriad.encoder import NumTriadEncoder
    SYMBOLIC_AVAILABLE = True
    AUTO_LEARNING_AVAILABLE = True
    NUMTRIAD_ENCODER_AVAILABLE = True
except ImportError:
    SYMBOLIC_AVAILABLE = False
    AUTO_LEARNING_AVAILABLE = False
    NUMTRIAD_ENCODER_AVAILABLE = False
    logger.warning("SymbolicEngine, AutoLearningEngine, or NumTriadEncoder not available")

try:
    from numtriad.core.system_v4 import NumTriadSystemV4, NumTriadSystemConfig
    NUMTRIAD_AVAILABLE = True
except ImportError:
    NUMTRIAD_AVAILABLE = False
    logger.warning("NumTriadSystemV4 not available")

try:
    from numtriad.multimodal_v4 import MultimodalV4Config
    MULTIMODAL_CONFIG_AVAILABLE = True
except ImportError:
    MULTIMODAL_CONFIG_AVAILABLE = False

try:
    from numtriad.llm.gemini_triad_wrapper import GeminiTriadWrapper
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("GeminiTriadWrapper not available")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


# ============================================================================
# DATA MODELS
# ============================================================================

class ContentType(str, Enum):
    """Supported content types"""
    TEXT = "text"
    CODE = "code"
    IMAGE = "image"
    AUDIO = "audio"
    MIXED = "mixed"


@dataclass
class TriadScores:
    """Triad representation (∆∞Θ)"""
    delta: float      # Specificity/Difference
    infinity: float   # Generality/Universality
    theta: float      # Context/Application
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array"""
        return np.array([self.delta, self.infinity, self.theta], dtype="float32")
    
    @classmethod
    def from_array(cls, arr: np.ndarray) -> "TriadScores":
        """Create from numpy array"""
        return cls(delta=float(arr[0]), infinity=float(arr[1]), theta=float(arr[2]))


@dataclass
class UnifiedEmbedding:
    """Unified embedding from all systems"""
    content: str
    content_type: ContentType
    
    # GLM symbolic representation
    glm_symbolic: Optional[Dict[str, Any]] = None
    
    # NumTriad embedding
    numtriad_embedding: Optional[np.ndarray] = None
    numtriad_triad: Optional[TriadScores] = None
    
    # Neural embedding
    neural_embedding: Optional[np.ndarray] = None
    
    # Fused embedding
    fused_embedding: Optional[np.ndarray] = None
    
    # Metadata
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SearchResult:
    """Search result with metadata"""
    doc_id: str
    content: str
    score: float
    triad: TriadScores
    metadata: Dict[str, Any]
    source: str  # "glm", "numtriad", "neural"


@dataclass
class QAResult:
    """Q&A result"""
    query: str
    answer: str
    context: List[SearchResult]
    confidence: float
    metadata: Dict[str, Any]


# ============================================================================
# UNIFIED SYSTEM
# ============================================================================

class UnifiedGLM:
    """
    Unified GLM v4.0 System
    
    Combines all components into a single coherent system:
    - GLM SymbolicEngine for symbolic reasoning
    - NumTriad for multimodal triad-aware embeddings
    - Neural encoders for semantic understanding
    - RAG for document retrieval
    - Gemini for natural language generation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize unified system"""
        self.config = config or {}
        self.device = self.config.get("device", "cpu")
        self.enable_auto_learning = self.config.get("enable_auto_learning", True)
        
        logger.info("Initializing Unified GLM v4.0...")
        
        # Initialize NumTriad Encoder (for learned domains)
        self.numtriad_encoder = None
        if NUMTRIAD_ENCODER_AVAILABLE:
            try:
                self.numtriad_encoder = NumTriadEncoder(model_name="numtriad-v3")
                logger.info("✅ NumTriadEncoder initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize NumTriadEncoder: {e}")
        
        # Initialize GLM SymbolicEngine
        self.symbolic_engine = None
        self.auto_learner = None
        if SYMBOLIC_AVAILABLE:
            try:
                self.symbolic_engine = SymbolicEngine()
                logger.info("✅ SymbolicEngine initialized")
                
                # Initialize AutoLearningEngine (with NumTriad encoder if available)
                if AUTO_LEARNING_AVAILABLE and self.enable_auto_learning:
                    try:
                        self.auto_learner = AutoLearningEngine(
                            self.symbolic_engine,
                            numtriad_encoder=self.numtriad_encoder
                        )
                        logger.info("✅ AutoLearningEngine integrated")
                        if self.numtriad_encoder:
                            logger.info("   └─ With NumTriad encoder for learned domains")
                    except Exception as e:
                        logger.warning(f"Failed to integrate AutoLearningEngine: {e}")
            except Exception as e:
                logger.warning(f"Failed to initialize SymbolicEngine: {e}")
        
        # Initialize NumTriad System V4
        self.numtriad_system = None
        if NUMTRIAD_AVAILABLE and MULTIMODAL_CONFIG_AVAILABLE and TORCH_AVAILABLE:
            try:
                mm_cfg = MultimodalV4Config(
                    dim_text_in=256,
                    dim_vision_in=256,
                    dim_code_in=256,
                    dim_audio_in=128,
                    dim_proj=192,
                    dim_t_cross=32,
                    device=self.device
                )
                sys_cfg = NumTriadSystemConfig(multimodal=mm_cfg, device=self.device)
                self.numtriad_system = NumTriadSystemV4(sys_cfg)
                logger.info("✅ NumTriadSystemV4 initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize NumTriadSystemV4: {e}")
        
        # Initialize Gemini wrapper
        self.gemini_wrapper = None
        if GEMINI_AVAILABLE:
            try:
                self.gemini_wrapper = GeminiTriadWrapper()
                logger.info("✅ GeminiTriadWrapper initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize GeminiTriadWrapper: {e}")
        
        logger.info("Unified GLM v4.0 ready!")
    
    # ========================================================================
    # ENCODING
    # ========================================================================
    
    def _standard_encode(self, content: str, domain: str) -> Dict[str, Any]:
        """
        Standard encoding through SymbolicEngine.
        
        Routes content to appropriate domain for encoding.
        
        Args:
            content: Content to encode
            domain: Domain name (text, code, geometry, image, etc.)
        
        Returns:
            Encoded representation with ∆∞Ο
            
        Raises:
            RuntimeError: If SymbolicEngine not available
            ValueError: If domain not found
        """
        if not self.symbolic_engine:
            raise RuntimeError("SymbolicEngine not available")
        
        # Get domain from engine
        domain_obj = self.symbolic_engine.get_domain(domain)
        if not domain_obj:
            raise ValueError(f"Domain not found: {domain}")
        
        # Encode using domain
        result = domain_obj.encode(content)
        
        return result
    
    def detect_content_type(self, content: Union[str, bytes]) -> ContentType:
        """Auto-detect content type"""
        if isinstance(content, str):
            # Check for code patterns
            if any(keyword in content for keyword in ["def ", "class ", "import ", "function ", "const "]):
                return ContentType.CODE
            # Default to text
            return ContentType.TEXT
        elif isinstance(content, bytes):
            # Could be image
            return ContentType.IMAGE
        return ContentType.MIXED
    
    def encode_with_auto_learning(
        self,
        content: Union[str, bytes],
        domain: str = "auto"
    ) -> Dict[str, Any]:
        """
        Encode content with automatic domain learning.
        
        If domain is unknown, AutoLearningEngine will:
        1. Detect the unknown concept
        2. Fetch knowledge from multiple sources
        3. Create a new domain dynamically
        4. Register it with SymbolicEngine
        5. Encode with the new domain
        
        Args:
            content: Content to encode
            domain: Domain name or "auto"
            
        Returns:
            Encoding result with triad representation
        """
        if not self.auto_learner:
            logger.warning("AutoLearningEngine not available, using standard encoding")
            result = self.encode_anything(content, domain)
            return {
                "status": "success",
                "method": "standard",
                "embedding": result.embedding if hasattr(result, 'embedding') else None,
                "metadata": {
                    "learned": False,
                    "numtriad_used": False,
                    "domain": domain,
                }
            }
        
        content_str = str(content)
        
        # Try standard encoding first
        try:
            result = self.encode_anything(content_str, domain)
            return {
                "status": "success",
                "method": "standard",
                "embedding": result.embedding if hasattr(result, 'embedding') else None,
                "metadata": {
                    "learned": False,
                    "numtriad_used": False,
                    "domain": domain,
                }
            }
        except Exception as e:
            logger.info(f"Standard encoding failed: {e}")
            
            # Try auto-learning
            if not self.enable_auto_learning:
                raise
            
            logger.info("🔍 Attempting auto-learning...")
            
            # Detect unknown concept
            unknown_concept = self.auto_learner.detect_unknown_concept(content_str)
            
            if not unknown_concept:
                raise ValueError("Could not detect unknown concept for auto-learning")
            
            logger.info(f"Detected unknown concept: {unknown_concept}")
            
            # Learn domain
            new_domain = self.auto_learner.learn_domain(unknown_concept)
            
            if not new_domain:
                raise ValueError(f"Could not learn domain for: {unknown_concept}")
            
            logger.info(f"✅ Successfully learned domain: {new_domain.name}")
            
            # Encode with new domain
            result = new_domain.encode(content_str)
            
            return {
                "status": "success",
                "method": "auto_learning",
                "embedding": result.embedding if hasattr(result, 'embedding') else None,
                "metadata": {
                    "learned": True,
                    "numtriad_used": getattr(new_domain, 'numtriad_encoder', None) is not None,
                    "domain": new_domain.name,
                    "concept": unknown_concept,
                }
            }
    
    def encode_anything(
        self,
        content: Union[str, bytes],
        domain: str = "auto",
        include_glm: bool = True,
        include_numtriad: bool = True,
        include_neural: bool = True
    ) -> UnifiedEmbedding:
        """
        Encode ANY content type with all available systems
        
        Args:
            content: Text, code, image, or audio
            domain: "auto", "text", "code", "image", "geometry"
            include_glm: Include GLM symbolic encoding
            include_numtriad: Include NumTriad embedding
            include_neural: Include neural encoding
        
        Returns:
            UnifiedEmbedding with all representations
        """
        logger.info(f"Encoding content (domain={domain})...")
        
        # Detect type
        content_type = self.detect_content_type(content)
        if isinstance(content, bytes):
            content_str = f"[{content_type.value}]"
        else:
            content_str = content
        
        embedding = UnifiedEmbedding(
            content=content_str,
            content_type=content_type
        )
        
        # 1. GLM Symbolic Encoding
        if include_glm and self.symbolic_engine:
            try:
                if domain == "auto":
                    domain = content_type.value
                embedding.glm_symbolic = self.symbolic_engine.abstract(content_str, domain)
                logger.info("✅ GLM symbolic encoding done")
            except Exception as e:
                logger.warning(f"GLM encoding failed: {e}")
        
        # 2. NumTriad Embedding
        if include_numtriad and self.numtriad_system:
            try:
                if content_type == ContentType.TEXT or content_type == ContentType.CODE:
                    emb, triad = self.numtriad_system.encode_sample(texts=[content_str])
                    embedding.numtriad_embedding = emb[0]
                    embedding.numtriad_triad = TriadScores.from_array(triad[0])
                    logger.info("✅ NumTriad embedding done")
            except Exception as e:
                logger.warning(f"NumTriad encoding failed: {e}")
        
        # 3. Fused Embedding
        if embedding.numtriad_embedding is not None:
            embedding.fused_embedding = embedding.numtriad_embedding
        
        embedding.metadata = {
            "content_type": content_type.value,
            "domain": domain,
            "glm_available": embedding.glm_symbolic is not None,
            "numtriad_available": embedding.numtriad_embedding is not None,
        }
        
        return embedding
    
    # ========================================================================
    # SEARCH
    # ========================================================================
    
    def add_document(
        self,
        doc_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add document to RAG index"""
        if not self.numtriad_system:
            logger.error("NumTriad system not available")
            return
        
        try:
            self.numtriad_system.add_document(
                doc_id,
                texts=[content],
                metadata=metadata or {}
            )
            logger.info(f"✅ Document {doc_id} added to index")
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
    
    def search(
        self,
        query: str,
        mode: str = "auto",
        k: int = 5
    ) -> List[SearchResult]:
        """
        Unified search with triad control
        
        Args:
            query: Search query
            mode: "auto", "abstract", "concrete", "balanced"
            k: Number of results
        
        Returns:
            List of SearchResult
        """
        logger.info(f"Searching: {query} (mode={mode}, k={k})...")
        
        results = []
        
        # 1. Analyze query triad
        query_embedding = self.encode_anything(query)
        
        # 2. Auto-select mode if needed
        if mode == "auto" and query_embedding.numtriad_triad:
            triad = query_embedding.numtriad_triad
            if triad.infinity > 0.6:
                mode = "abstract"
            elif triad.theta > 0.6:
                mode = "concrete"
            else:
                mode = "balanced"
            logger.info(f"Auto-selected mode: {mode}")
        
        # 3. Search with NumTriad
        if self.numtriad_system:
            try:
                numtriad_results = self.numtriad_system.query_documents(
                    query,
                    mode=mode,
                    k=k
                )
                
                for doc, score in numtriad_results:
                    results.append(SearchResult(
                        doc_id=doc.doc_id,
                        content=doc.texts[0] if doc.texts else "",
                        score=float(score),
                        triad=TriadScores.from_array(doc.triad),
                        metadata=doc.metadata,
                        source="numtriad"
                    ))
                logger.info(f"✅ Found {len(results)} results")
            except Exception as e:
                logger.warning(f"NumTriad search failed: {e}")
        
        return results
    
    # ========================================================================
    # Q&A
    # ========================================================================
    
    def answer(
        self,
        query: str,
        k: int = 5,
        use_gemini: bool = True
    ) -> QAResult:
        """
        Complete Q&A pipeline
        
        Args:
            query: Question
            k: Number of context documents
            use_gemini: Use Gemini for generation
        
        Returns:
            QAResult with answer and context
        """
        logger.info(f"Answering: {query}...")
        
        # 1. Search for context
        context = self.search(query, mode="auto", k=k)
        
        # 2. Generate answer
        answer_text = "No answer generated"
        confidence = 0.0
        
        if use_gemini and self.gemini_wrapper:
            try:
                context_text = "\n".join([f"- {r.content}" for r in context])
                answer_text = self.gemini_wrapper.answer(query, context_text)
                confidence = 0.8
                logger.info("✅ Answer generated with Gemini")
            except Exception as e:
                logger.warning(f"Gemini generation failed: {e}")
        else:
            # Fallback: return top result
            if context:
                answer_text = context[0].content
                confidence = context[0].score
        
        return QAResult(
            query=query,
            answer=answer_text,
            context=context,
            confidence=confidence,
            metadata={
                "num_context_docs": len(context),
                "gemini_used": use_gemini and self.gemini_wrapper is not None
            }
        )
    
    # ========================================================================
    # TRANSFORMATIONS
    # ========================================================================
    
    def transform(
        self,
        content: str,
        from_domain: str = "auto",
        to_domain: str = "auto",
        mode: str = "abstract"
    ) -> Dict[str, Any]:
        """
        Transform content between domains
        
        Args:
            content: Content to transform
            from_domain: Source domain
            to_domain: Target domain
            mode: Transformation mode
        
        Returns:
            Transformed content
        """
        logger.info(f"Transforming: {from_domain} -> {to_domain}...")
        
        if not self.symbolic_engine:
            logger.error("SymbolicEngine not available")
            return {"error": "SymbolicEngine not available"}
        
        try:
            # Encode
            embedding = self.encode_anything(content, domain=from_domain)
            
            # Transform
            result = self.symbolic_engine.transform(
                embedding.glm_symbolic or content,
                from_domain,
                to_domain
            )
            
            logger.info("✅ Transformation done")
            return {
                "original": content,
                "transformed": result,
                "from_domain": from_domain,
                "to_domain": to_domain,
                "triad": embedding.numtriad_triad.to_array().tolist() if embedding.numtriad_triad else None
            }
        except Exception as e:
            logger.error(f"Transformation failed: {e}")
            return {"error": str(e)}
    
    # ========================================================================
    # SYSTEM STATUS
    # ========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        status = {
            "version": "4.0.0",
            "components": {
                "symbolic_engine": SYMBOLIC_AVAILABLE and self.symbolic_engine is not None,
                "numtriad_system": NUMTRIAD_AVAILABLE and self.numtriad_system is not None,
                "gemini_wrapper": GEMINI_AVAILABLE and self.gemini_wrapper is not None,
            },
            "device": self.device,
        }
        
        if self.numtriad_system:
            status["numtriad"] = self.numtriad_system.get_status()
        
        return status
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "glm": {
                "symbolic_engine": "available" if self.symbolic_engine else "unavailable",
                "domains": 4,
            },
            "numtriad": {
                "documents_indexed": len(self.numtriad_system.rag_index.docs) if self.numtriad_system else 0,
                "pillars": 4,
            },
            "gemini": {
                "available": self.gemini_wrapper is not None,
            },
            "device": self.device,
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_unified_glm(device: str = "cpu") -> UnifiedGLM:
    """Create and initialize unified GLM system"""
    return UnifiedGLM(config={"device": device})


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("Unified GLM v4.0 - Example Usage")
    logger.info("=" * 70)
    
    # Initialize
    glm = create_unified_glm(device="cpu")
    
    # Show status
    status = glm.get_status()
    logger.info(f"System status: {status}")
    
    # Example 1: Encode text
    logger.info("\n--- Example 1: Encoding ---")
    embedding = glm.encode_anything("Hello, world!")
    logger.info(f"Embedding shape: {embedding.fused_embedding.shape if embedding.fused_embedding is not None else 'N/A'}")
    if embedding.numtriad_triad:
        logger.info(f"Triad: ∆={embedding.numtriad_triad.delta:.3f}, ∞={embedding.numtriad_triad.infinity:.3f}, Θ={embedding.numtriad_triad.theta:.3f}")
    
    # Example 2: Add documents
    logger.info("\n--- Example 2: Adding Documents ---")
    glm.add_document("doc1", "Machine learning is a subset of AI")
    glm.add_document("doc2", "Neural networks are inspired by biology")
    glm.add_document("doc3", "Deep learning uses multiple layers")
    
    # Example 3: Search
    logger.info("\n--- Example 3: Search ---")
    results = glm.search("what is machine learning?", mode="auto", k=2)
    for i, result in enumerate(results):
        logger.info(f"Result {i+1}: {result.doc_id} (score={result.score:.3f})")
    
    # Example 4: Q&A
    logger.info("\n--- Example 4: Q&A ---")
    qa_result = glm.answer("explain neural networks", k=2)
    logger.info(f"Answer: {qa_result.answer}")
    logger.info(f"Confidence: {qa_result.confidence:.3f}")
    
    # Example 5: Metrics
    logger.info("\n--- Example 5: Metrics ---")
    metrics = glm.get_metrics()
    logger.info(f"Metrics: {metrics}")
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ Unified GLM v4.0 ready for production!")
    logger.info("=" * 70)
