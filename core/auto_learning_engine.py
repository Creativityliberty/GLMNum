"""
Auto-Learning Engine for GLM v4.0
==================================

Automatically detects unknown concepts and creates new domains dynamically.
This is the killer feature that makes GLM truly extensible.

Features:
- Concept detection
- Knowledge fetching (Wikipedia, PyPI, etc.)
- Dynamic domain creation
- Automatic registration
- Learning from user interactions
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

logger = logging.getLogger(__name__)


@dataclass
class ConceptInfo:
    """Information about a learned concept"""
    name: str
    domain: str
    description: str
    source: str
    confidence: float
    created_at: str
    metadata: Dict[str, Any]
    examples: List[str]


@dataclass
class DomainTemplate:
    """Template for creating new domains"""
    name: str
    description: str
    features: List[str]
    encoders: List[str]
    transformations: Dict[str, str]
    metadata: Dict[str, Any]


class AutoLearningEngine:
    """
    Automatically learns and creates new domains from user interactions.
    
    Workflow:
    1. User provides unknown concept
    2. Engine detects it's unknown
    3. Fetches knowledge from sources
    4. Creates domain template
    5. Registers domain
    6. Learns from interactions
    """
    
    def __init__(self, cache_dir: str = "./cache/learned_domains"):
        """
        Initialize Auto-Learning Engine
        
        Args:
            cache_dir: Directory to cache learned domains
        """
        self.cache_dir = cache_dir
        self.learned_concepts: Dict[str, ConceptInfo] = {}
        self.learned_domains: Dict[str, DomainTemplate] = {}
        self.learning_history: List[Dict] = []
        self.knowledge_sources = {
            "wikipedia": self._fetch_wikipedia,
            "pypi": self._fetch_pypi,
            "github": self._fetch_github,
            "arxiv": self._fetch_arxiv,
        }
        
        logger.info("AutoLearningEngine initialized")
    
    # ========================================================================
    # CONCEPT DETECTION
    # ========================================================================
    
    def detect_unknown_concept(self, text: str, known_domains: List[str]) -> Optional[str]:
        """
        Detect if text contains unknown concepts not in known domains.
        
        Args:
            text: Input text to analyze
            known_domains: List of known domain names
            
        Returns:
            Unknown concept name or None
        """
        # Extract potential concepts (capitalized words, technical terms)
        concepts = self._extract_concepts(text)
        
        for concept in concepts:
            if not self._is_known_concept(concept, known_domains):
                logger.info(f"Detected unknown concept: {concept}")
                return concept
        
        return None
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract potential concepts from text"""
        import re
        
        # Find capitalized words and technical terms
        concepts = []
        
        # Pattern 1: Capitalized words (proper nouns)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        concepts.extend(capitalized)
        
        # Pattern 2: Words in quotes
        quoted = re.findall(r'"([^"]+)"', text)
        concepts.extend(quoted)
        
        # Pattern 3: Technical terms (CamelCase)
        camelcase = re.findall(r'\b[a-z]+[A-Z][a-zA-Z]*\b', text)
        concepts.extend(camelcase)
        
        return list(set(concepts))
    
    def _is_known_concept(self, concept: str, known_domains: List[str]) -> bool:
        """Check if concept is already known"""
        # Check against known domains
        if concept.lower() in [d.lower() for d in known_domains]:
            return True
        
        # Check against learned concepts
        if concept.lower() in [c.lower() for c in self.learned_concepts.keys()]:
            return True
        
        return False
    
    # ========================================================================
    # KNOWLEDGE FETCHING
    # ========================================================================
    
    def fetch_knowledge(self, concept: str, sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fetch knowledge about a concept from multiple sources.
        
        Args:
            concept: Concept name
            sources: List of sources to query (default: all)
            
        Returns:
            Dictionary with knowledge from all sources
        """
        if sources is None:
            sources = list(self.knowledge_sources.keys())
        
        knowledge = {
            "concept": concept,
            "sources": {},
            "fetched_at": datetime.now().isoformat(),
        }
        
        for source in sources:
            if source in self.knowledge_sources:
                try:
                    logger.info(f"Fetching from {source}: {concept}")
                    result = self.knowledge_sources[source](concept)
                    knowledge["sources"][source] = result
                except Exception as e:
                    logger.warning(f"Failed to fetch from {source}: {e}")
                    knowledge["sources"][source] = {"error": str(e)}
        
        return knowledge
    
    def _fetch_wikipedia(self, concept: str) -> Dict[str, Any]:
        """Fetch from Wikipedia"""
        if not requests or not BeautifulSoup:
            return {"error": "requests or BeautifulSoup not installed"}
        
        try:
            url = f"https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "titles": concept,
                "prop": "extracts",
                "explaintext": True,
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            pages = data.get("query", {}).get("pages", {})
            if pages:
                page = list(pages.values())[0]
                extract = page.get("extract", "")
                
                return {
                    "source": "wikipedia",
                    "title": page.get("title", concept),
                    "description": extract[:500],  # First 500 chars
                    "url": f"https://en.wikipedia.org/wiki/{concept.replace(' ', '_')}",
                    "confidence": 0.9,
                }
        except Exception as e:
            logger.warning(f"Wikipedia fetch failed: {e}")
        
        return {"error": "Not found on Wikipedia"}
    
    def _fetch_pypi(self, concept: str) -> Dict[str, Any]:
        """Fetch from PyPI (Python packages)"""
        if not requests:
            return {"error": "requests not installed"}
        
        try:
            url = f"https://pypi.org/pypi/{concept}/json"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                info = data.get("info", {})
                
                return {
                    "source": "pypi",
                    "name": info.get("name", concept),
                    "description": info.get("summary", ""),
                    "version": info.get("version", ""),
                    "url": info.get("home_page", ""),
                    "confidence": 0.85,
                }
        except Exception as e:
            logger.warning(f"PyPI fetch failed: {e}")
        
        return {"error": "Not found on PyPI"}
    
    def _fetch_github(self, concept: str) -> Dict[str, Any]:
        """Fetch from GitHub (repositories)"""
        if not requests:
            return {"error": "requests not installed"}
        
        try:
            url = f"https://api.github.com/search/repositories"
            params = {
                "q": concept,
                "sort": "stars",
                "order": "desc",
                "per_page": 1,
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data.get("items"):
                repo = data["items"][0]
                
                return {
                    "source": "github",
                    "name": repo.get("name", concept),
                    "description": repo.get("description", ""),
                    "stars": repo.get("stargazers_count", 0),
                    "url": repo.get("html_url", ""),
                    "confidence": 0.8,
                }
        except Exception as e:
            logger.warning(f"GitHub fetch failed: {e}")
        
        return {"error": "Not found on GitHub"}
    
    def _fetch_arxiv(self, concept: str) -> Dict[str, Any]:
        """Fetch from arXiv (research papers)"""
        if not requests:
            return {"error": "requests not installed"}
        
        try:
            url = "http://export.arxiv.org/api/query"
            params = {
                "search_query": f"all:{concept}",
                "start": 0,
                "max_results": 1,
                "sortBy": "relevance",
                "sortOrder": "descending",
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                # Parse arXiv response
                ns = {"arxiv": "http://arxiv.org/schemas/atom"}
                entries = root.findall("atom:entry", ns)
                
                if entries:
                    entry = entries[0]
                    title = entry.find("atom:title", ns).text
                    summary = entry.find("atom:summary", ns).text
                    
                    return {
                        "source": "arxiv",
                        "title": title,
                        "summary": summary[:300],
                        "confidence": 0.85,
                    }
        except Exception as e:
            logger.warning(f"arXiv fetch failed: {e}")
        
        return {"error": "Not found on arXiv"}
    
    # ========================================================================
    # DOMAIN CREATION
    # ========================================================================
    
    def create_domain_from_knowledge(self, concept: str, knowledge: Dict[str, Any]) -> DomainTemplate:
        """
        Create a domain template from fetched knowledge.
        
        Args:
            concept: Concept name
            knowledge: Knowledge dictionary from fetch_knowledge()
            
        Returns:
            DomainTemplate ready for registration
        """
        # Extract information from sources
        description = self._synthesize_description(knowledge)
        features = self._extract_features(concept, knowledge)
        encoders = self._suggest_encoders(concept, knowledge)
        transformations = self._suggest_transformations(concept)
        
        domain = DomainTemplate(
            name=concept.lower().replace(" ", "_"),
            description=description,
            features=features,
            encoders=encoders,
            transformations=transformations,
            metadata={
                "created_at": datetime.now().isoformat(),
                "source": "auto_learning",
                "confidence": self._calculate_confidence(knowledge),
                "knowledge_sources": list(knowledge.get("sources", {}).keys()),
            }
        )
        
        logger.info(f"Created domain template for: {concept}")
        return domain
    
    def _synthesize_description(self, knowledge: Dict[str, Any]) -> str:
        """Synthesize description from multiple sources"""
        descriptions = []
        
        for source, data in knowledge.get("sources", {}).items():
            if isinstance(data, dict):
                # Try different description fields
                desc = (
                    data.get("description") or
                    data.get("summary") or
                    data.get("title") or
                    ""
                )
                if desc:
                    descriptions.append(desc)
        
        # Combine descriptions (take first 500 chars)
        combined = " ".join(descriptions)
        return combined[:500] if combined else "Auto-learned domain"
    
    def _extract_features(self, concept: str, knowledge: Dict[str, Any]) -> List[str]:
        """Extract features for the domain"""
        features = [
            "embedding",
            "triad_scoring",
            "semantic_similarity",
            "cross_domain_transformation",
        ]
        
        # Add concept-specific features
        concept_lower = concept.lower()
        
        if any(x in concept_lower for x in ["image", "vision", "visual", "picture"]):
            features.extend(["visual_features", "object_detection"])
        
        if any(x in concept_lower for x in ["text", "document", "nlp", "language"]):
            features.extend(["tokenization", "pos_tagging", "ner"])
        
        if any(x in concept_lower for x in ["code", "program", "software"]):
            features.extend(["ast_parsing", "syntax_analysis"])
        
        if any(x in concept_lower for x in ["audio", "sound", "music", "speech"]):
            features.extend(["spectrogram", "pitch_detection"])
        
        return list(set(features))
    
    def _suggest_encoders(self, concept: str, knowledge: Dict[str, Any]) -> List[str]:
        """Suggest appropriate encoders"""
        encoders = ["base_encoder"]
        
        concept_lower = concept.lower()
        
        # Suggest based on concept type
        if any(x in concept_lower for x in ["image", "vision", "visual"]):
            encoders.extend(["clip", "bge_vision", "nomic_vision"])
        
        if any(x in concept_lower for x in ["text", "document", "nlp"]):
            encoders.extend(["bge_text", "nomic_text", "sentence_transformers"])
        
        if any(x in concept_lower for x in ["code", "program"]):
            encoders.extend(["codebert", "starcoder"])
        
        if any(x in concept_lower for x in ["audio", "sound"]):
            encoders.extend(["wav2vec", "hubert"])
        
        return list(set(encoders))
    
    def _suggest_transformations(self, concept: str) -> Dict[str, str]:
        """Suggest transformations to/from other domains"""
        transformations = {
            "to_text": f"describe_{concept.lower()}",
            "to_embedding": f"embed_{concept.lower()}",
            "to_triad": f"analyze_triad_{concept.lower()}",
        }
        
        return transformations
    
    def _calculate_confidence(self, knowledge: Dict[str, Any]) -> float:
        """Calculate confidence score for learned domain"""
        confidences = []
        
        for source, data in knowledge.get("sources", {}).items():
            if isinstance(data, dict) and "error" not in data:
                conf = data.get("confidence", 0.5)
                confidences.append(conf)
        
        if not confidences:
            return 0.3  # Low confidence if no sources found
        
        return sum(confidences) / len(confidences)
    
    # ========================================================================
    # LEARNING & PERSISTENCE
    # ========================================================================
    
    def register_learned_domain(self, domain: DomainTemplate) -> bool:
        """
        Register a learned domain.
        
        Args:
            domain: DomainTemplate to register
            
        Returns:
            True if successful
        """
        try:
            self.learned_domains[domain.name] = domain
            
            # Log learning event
            self.learning_history.append({
                "event": "domain_created",
                "domain": domain.name,
                "timestamp": datetime.now().isoformat(),
                "confidence": domain.metadata.get("confidence", 0),
            })
            
            logger.info(f"Registered learned domain: {domain.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register domain: {e}")
            return False
    
    def learn_from_interaction(self, concept: str, domain: str, feedback: Dict[str, Any]) -> None:
        """
        Learn from user interactions to improve domains.
        
        Args:
            concept: Concept name
            domain: Domain name
            feedback: User feedback (rating, corrections, etc.)
        """
        self.learning_history.append({
            "event": "user_feedback",
            "concept": concept,
            "domain": domain,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat(),
        })
        
        # Update domain confidence based on feedback
        if domain in self.learned_domains:
            rating = feedback.get("rating", 0.5)
            current_conf = self.learned_domains[domain].metadata.get("confidence", 0.5)
            
            # Exponential moving average
            alpha = 0.3
            new_conf = alpha * rating + (1 - alpha) * current_conf
            self.learned_domains[domain].metadata["confidence"] = new_conf
            
            logger.info(f"Updated domain confidence: {domain} → {new_conf:.2f}")
    
    def save_learned_domains(self, path: str) -> bool:
        """Save learned domains to file"""
        try:
            data = {
                "domains": {
                    name: asdict(domain)
                    for name, domain in self.learned_domains.items()
                },
                "history": self.learning_history,
                "saved_at": datetime.now().isoformat(),
            }
            
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved learned domains to: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save domains: {e}")
            return False
    
    def load_learned_domains(self, path: str) -> bool:
        """Load learned domains from file"""
        try:
            with open(path, "r") as f:
                data = json.load(f)
            
            # Reconstruct domain templates
            for name, domain_dict in data.get("domains", {}).items():
                domain = DomainTemplate(**domain_dict)
                self.learned_domains[name] = domain
            
            self.learning_history = data.get("history", [])
            
            logger.info(f"Loaded {len(self.learned_domains)} learned domains from: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load domains: {e}")
            return False
    
    # ========================================================================
    # STATISTICS & MONITORING
    # ========================================================================
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about learned domains"""
        return {
            "total_learned_domains": len(self.learned_domains),
            "total_interactions": len(self.learning_history),
            "domains": {
                name: {
                    "confidence": domain.metadata.get("confidence", 0),
                    "sources": domain.metadata.get("knowledge_sources", []),
                    "created_at": domain.metadata.get("created_at"),
                }
                for name, domain in self.learned_domains.items()
            },
            "recent_events": self.learning_history[-10:],
        }
    
    def get_domain_info(self, domain_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a learned domain"""
        if domain_name not in self.learned_domains:
            return None
        
        domain = self.learned_domains[domain_name]
        return {
            "name": domain.name,
            "description": domain.description,
            "features": domain.features,
            "encoders": domain.encoders,
            "transformations": domain.transformations,
            "metadata": domain.metadata,
        }


# ============================================================================
# INTEGRATION WITH SYMBOLIC ENGINE
# ============================================================================

def integrate_auto_learning(symbolic_engine) -> AutoLearningEngine:
    """
    Integrate AutoLearningEngine with SymbolicEngine.
    
    Args:
        symbolic_engine: SymbolicEngine instance
        
    Returns:
        AutoLearningEngine instance
    """
    auto_learner = AutoLearningEngine()
    
    # Monkey-patch encode method to detect unknown concepts
    original_encode = symbolic_engine.encode
    
    def encode_with_learning(content, domain=None):
        # Try original encoding
        try:
            return original_encode(content, domain)
        except Exception as e:
            # If domain is unknown, try to learn it
            if "unknown domain" in str(e).lower():
                logger.info("Attempting to learn unknown domain...")
                
                # Detect concept
                known_domains = list(symbolic_engine.domains.keys())
                unknown_concept = auto_learner.detect_unknown_concept(content, known_domains)
                
                if unknown_concept:
                    # Fetch knowledge
                    knowledge = auto_learner.fetch_knowledge(unknown_concept)
                    
                    # Create domain
                    new_domain = auto_learner.create_domain_from_knowledge(unknown_concept, knowledge)
                    
                    # Register domain
                    auto_learner.register_learned_domain(new_domain)
                    
                    logger.info(f"Successfully learned domain: {new_domain.name}")
                    
                    # Try encoding again
                    return original_encode(content, new_domain.name)
            
            raise
    
    symbolic_engine.encode = encode_with_learning
    
    return auto_learner


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    engine = AutoLearningEngine()
    
    # Example: Learn about DNA sequences
    print("Learning about DNA sequences...")
    knowledge = engine.fetch_knowledge("DNA sequence")
    print(f"Fetched knowledge: {json.dumps(knowledge, indent=2)}")
    
    # Create domain
    domain = engine.create_domain_from_knowledge("DNA sequence", knowledge)
    print(f"\nCreated domain: {domain.name}")
    print(f"Description: {domain.description[:100]}...")
    print(f"Features: {domain.features}")
    print(f"Encoders: {domain.encoders}")
    
    # Register domain
    engine.register_learned_domain(domain)
    
    # Get stats
    stats = engine.get_learning_stats()
    print(f"\nLearning stats: {json.dumps(stats, indent=2)}")
