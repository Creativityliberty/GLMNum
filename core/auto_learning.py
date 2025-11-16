"""
Auto-Learning Engine for GLM v4.0
==================================

Automatically discovers and learns new domains from concepts.
Integrates seamlessly with SymbolicEngine and UnifiedGLM.

Architecture:
  - Concept Detection: Identifies unknown concepts in text
  - Knowledge Gathering: Fetches from Wikipedia, PyPI, NPM, arXiv
  - Domain Creation: Synthesizes knowledge into new Domain classes
  - Registration: Registers learned domains with SymbolicEngine

This module is the "meta-layer" that makes GLM truly extensible.
"""

import logging
from typing import Dict, Any, Optional, List
import numpy as np
import networkx as nx
import re

logger = logging.getLogger(__name__)


# ============================================================================
# KNOWLEDGE SOURCES
# ============================================================================

class KnowledgeSource:
    """Base class for knowledge sources"""
    
    @property
    def name(self) -> str:
        return self.__class__.__name__
    
    def query(self, concept: str) -> Optional[Dict[str, Any]]:
        """Query knowledge source for a concept"""
        raise NotImplementedError


class WikipediaSource(KnowledgeSource):
    """Fetch knowledge from Wikipedia"""
    
    def query(self, concept: str) -> Optional[Dict[str, Any]]:
        try:
            import requests
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{concept}"
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            text = data.get("extract", "") or ""
            
            return {
                "source": "wikipedia",
                "description": text[:500],
                "keywords": self._extract_keywords(text),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
            }
        except Exception as e:
            logger.debug(f"Wikipedia query failed: {e}")
            return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        words = [w.strip(".,;()").lower() for w in text.split()]
        keywords = [w for w in words if len(w) > 4 and w.isalpha()]
        return list(set(keywords))[:20]


class PyPISource(KnowledgeSource):
    """Fetch knowledge from PyPI (Python packages)"""
    
    def query(self, concept: str) -> Optional[Dict[str, Any]]:
        try:
            import requests
            url = f"https://pypi.org/pypi/{concept}/json"
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                return None
            
            info = response.json().get("info", {})
            
            return {
                "source": "pypi",
                "description": info.get("summary", ""),
                "keywords": (info.get("keywords") or "").split(","),
                "libraries": [concept],
                "url": info.get("home_page", ""),
            }
        except Exception as e:
            logger.debug(f"PyPI query failed: {e}")
            return None


class NPMSource(KnowledgeSource):
    """Fetch knowledge from NPM (JavaScript packages)"""
    
    def query(self, concept: str) -> Optional[Dict[str, Any]]:
        try:
            import requests
            url = f"https://registry.npmjs.org/{concept}"
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            return {
                "source": "npm",
                "description": data.get("description", ""),
                "keywords": data.get("keywords", []),
                "libraries": [concept],
                "url": data.get("homepage", ""),
            }
        except Exception as e:
            logger.debug(f"NPM query failed: {e}")
            return None


class ArXivSource(KnowledgeSource):
    """Fetch knowledge from arXiv (research papers)"""
    
    def query(self, concept: str) -> Optional[Dict[str, Any]]:
        try:
            import requests
            url = f"http://export.arxiv.org/api/query?search_query=all:{concept}&max_results=1"
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                return None
            
            # Simple XML parsing
            text = response.text
            if "<entry>" in text:
                return {
                    "source": "arxiv",
                    "description": f"Research papers about {concept}",
                    "keywords": [concept],
                    "papers": [concept],
                }
            
            return None
        except Exception as e:
            logger.debug(f"arXiv query failed: {e}")
            return None


# ============================================================================
# LEARNED DOMAIN CLASS
# ============================================================================

class LearnedDomain:
    """
    Dynamically created domain from learned knowledge.
    Integrates with SymbolicRepresentation (∆∞Ο).
    """
    
    def __init__(
        self,
        concept_name: str,
        knowledge: Dict[str, Any],
        embedding_dim: int = 128,
    ):
        self.concept_name = concept_name
        self.knowledge = knowledge
        self.embedding_dim = embedding_dim
        self.name = f"{concept_name.lower().replace(' ', '_')}_domain"
        
        logger.info(f"Created LearnedDomain: {self.name}")
    
    def has_notion_of(self, concept: str) -> bool:
        """Check if domain has notion of a concept"""
        all_concepts = (
            self.knowledge.get("keywords", []) +
            self.knowledge.get("related_concepts", []) +
            [self.concept_name]
        )
        return concept.lower() in [x.lower() for x in all_concepts]
    
    def encode(self, obj: Any) -> Dict[str, Any]:
        """
        Encode object into SymbolicRepresentation (∆∞Ο).
        
        Returns:
            {
                "delta": np.ndarray,      # Specificity
                "infinity": nx.Graph,     # Generality (concept graph)
                "omega": np.ndarray,      # Context
                "metadata": dict
            }
        """
        text = str(obj)
        
        delta = self._extract_delta(text)
        infinity = self._build_concept_graph(text)
        omega = self._create_omega(text)
        
        return {
            "delta": delta,
            "infinity": infinity,
            "omega": omega,
            "metadata": {
                "domain": self.name,
                "concept": self.concept_name,
                "learned": True,
                "description": self.knowledge.get("description", ""),
                "source": self.knowledge.get("source", "unknown"),
            },
        }
    
    def decode(self, symbolic: Dict[str, Any]) -> str:
        """Decode symbolic representation back to text"""
        return f"{self.concept_name} representation (auto-learned)"
    
    # ========================================================================
    # SYMBOLIC REPRESENTATION COMPONENTS
    # ========================================================================
    
    def _extract_delta(self, text: str) -> np.ndarray:
        """
        ∆ (Delta): Specificity - essence via keyword presence.
        
        Returns:
            Vector indicating which keywords are present in text.
        """
        keywords = self.knowledge.get("keywords", [])
        v = np.zeros(self.embedding_dim, dtype=np.float32)
        
        for i, kw in enumerate(keywords[:self.embedding_dim]):
            if kw.lower() in text.lower():
                v[i] = 1.0
        
        # Normalize
        norm = np.linalg.norm(v)
        if norm > 0:
            v /= norm
        
        return v
    
    def _build_concept_graph(self, text: str) -> nx.Graph:
        """
        ∞ (Infinity): Generality - concept co-occurrence graph.
        
        Returns:
            NetworkX graph with concepts as nodes and co-occurrences as edges.
        """
        g = nx.Graph()
        keywords = self.knowledge.get("keywords", [])
        
        # Add nodes
        for i, kw in enumerate(keywords):
            g.add_node(i, label=kw, present=kw.lower() in text.lower())
        
        # Add edges for co-occurrences
        for i, kw1 in enumerate(keywords):
            for j, kw2 in enumerate(keywords[i + 1:], start=i + 1):
                if (kw1.lower() in text.lower() and kw2.lower() in text.lower()):
                    g.add_edge(i, j, relation="co-occurrence", weight=1.0)
        
        return g
    
    def _create_omega(self, text: str) -> np.ndarray:
        """
        Ο (Omega): Context - bag-of-words embedding on keywords.
        
        Returns:
            Vector with keyword frequencies normalized.
        """
        v = np.zeros(self.embedding_dim, dtype=np.float32)
        keywords = self.knowledge.get("keywords", [])
        
        for i, kw in enumerate(keywords[:self.embedding_dim]):
            count = text.lower().count(kw.lower())
            v[i] = min(count / 10.0, 1.0)  # Normalize to [0, 1]
        
        # Normalize
        norm = np.linalg.norm(v)
        if norm > 0:
            v /= norm
        
        return v


# ============================================================================
# AUTO-LEARNING ENGINE
# ============================================================================

class AutoLearningEngine:
    """
    Main auto-learning engine.
    
    Responsibilities:
      1. Detect unknown concepts in text
      2. Gather knowledge from multiple sources
      3. Create domain templates
      4. Register with SymbolicEngine
    """
    
    def __init__(self, symbolic_engine):
        """
        Initialize AutoLearningEngine.
        
        Args:
            symbolic_engine: SymbolicEngine instance to register domains with
        """
        self.engine = symbolic_engine
        self.learned_domains: Dict[str, LearnedDomain] = {}
        
        self.knowledge_sources = [
            WikipediaSource(),
            PyPISource(),
            NPMSource(),
            ArXivSource(),
        ]
        
        logger.info("AutoLearningEngine initialized")
    
    def detect_unknown_concept(self, text: str) -> Optional[str]:
        """
        Detect unknown concept in text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Unknown concept name or None
        """
        keywords = self._extract_keywords(text)
        
        for kw in keywords:
            # Check if known by any existing domain
            known = False
            for domain in self.engine.domains.values():
                if hasattr(domain, "has_notion_of"):
                    if domain.has_notion_of(kw):
                        known = True
                        break
            
            # Check if already learned
            if kw in self.learned_domains:
                known = True
            
            if not known:
                logger.info(f"Detected unknown concept: {kw}")
                return kw
        
        return None
    
    def learn_domain(self, concept: str) -> Optional[LearnedDomain]:
        """
        Learn a new domain from a concept.
        
        Args:
            concept: Concept name (e.g., "DNA", "Kubernetes")
            
        Returns:
            LearnedDomain instance or None
        """
        logger.info(f"🔍 Learning new concept: {concept}")
        
        # Gather knowledge
        knowledge = self._gather_knowledge(concept)
        
        if not knowledge or not knowledge.get("keywords"):
            logger.warning(f"Could not gather knowledge about: {concept}")
            return None
        
        # Create domain
        domain = LearnedDomain(concept, knowledge)
        
        # Register with engine
        self.engine.register_domain(domain)
        self.learned_domains[concept] = domain
        
        logger.info(f"✅ Successfully learned domain: {domain.name}")
        return domain
    
    def _gather_knowledge(self, concept: str) -> Dict[str, Any]:
        """
        Gather knowledge from all sources.
        
        Args:
            concept: Concept to research
            
        Returns:
            Aggregated knowledge dictionary
        """
        knowledge = {
            "concept": concept,
            "description": None,
            "keywords": [],
            "related_concepts": [],
            "examples": [],
            "libraries": [],
            "papers": [],
            "sources": [],
        }
        
        for source in self.knowledge_sources:
            try:
                logger.debug(f"Querying {source.name} for: {concept}")
                data = source.query(concept)
                
                if data:
                    knowledge = self._merge_knowledge(knowledge, data)
                    knowledge["sources"].append(source.name)
            except Exception as e:
                logger.warning(f"Error querying {source.name}: {e}")
        
        return knowledge
    
    def _merge_knowledge(
        self,
        base: Dict[str, Any],
        new: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge knowledge from multiple sources"""
        merged = dict(base)
        
        # Merge lists
        for key in ["keywords", "related_concepts", "examples", "libraries", "papers"]:
            if key in new and new[key]:
                merged[key] = list(set(merged.get(key, []) + new[key]))
        
        # Use first non-empty description
        if new.get("description") and not merged.get("description"):
            merged["description"] = new["description"]
        
        return merged
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract potential concept keywords from text.
        
        Patterns:
          - Capitalized words (proper nouns)
          - Technical terms (CamelCase)
          - Quoted phrases
        """
        keywords = []
        
        # Pattern 1: Capitalized words
        caps = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)
        keywords.extend(caps)
        
        # Pattern 2: CamelCase
        camel = re.findall(r"\b[a-z]+[A-Z][a-zA-Z]*\b", text)
        keywords.extend(camel)
        
        # Pattern 3: Quoted phrases
        quoted = re.findall(r'"([^"]+)"', text)
        keywords.extend(quoted)
        
        # Remove duplicates and limit
        keywords = list(set(keywords))[:15]
        
        return keywords
    
    def get_learned_domains(self) -> List[str]:
        """Get list of learned domain names"""
        return list(self.learned_domains.keys())
    
    def get_domain_info(self, concept: str) -> Optional[Dict[str, Any]]:
        """Get information about a learned domain"""
        if concept not in self.learned_domains:
            return None
        
        domain = self.learned_domains[concept]
        return {
            "name": domain.name,
            "concept": domain.concept_name,
            "description": domain.knowledge.get("description", ""),
            "keywords": domain.knowledge.get("keywords", []),
            "sources": domain.knowledge.get("sources", []),
        }


# ============================================================================
# INTEGRATION HELPER
# ============================================================================

def integrate_auto_learning(symbolic_engine) -> AutoLearningEngine:
    """
    Integrate AutoLearningEngine with SymbolicEngine.
    
    Args:
        symbolic_engine: SymbolicEngine instance
        
    Returns:
        AutoLearningEngine instance
    """
    auto_learner = AutoLearningEngine(symbolic_engine)
    logger.info("AutoLearningEngine integrated with SymbolicEngine")
    return auto_learner


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    from symbolic import SymbolicEngine
    
    engine = SymbolicEngine()
    auto_learner = integrate_auto_learning(engine)
    
    # Learn about DNA
    print("\n🧬 Learning about DNA sequences...")
    domain = auto_learner.learn_domain("DNA")
    
    if domain:
        # Encode something
        result = domain.encode("ATCG sequence with GC content")
        print(f"\n✅ Encoded result:")
        print(f"  Delta shape: {result['delta'].shape}")
        print(f"  Infinity nodes: {domain._build_concept_graph('ATCG').number_of_nodes()}")
        print(f"  Metadata: {result['metadata']}")
        
        # Get info
        info = auto_learner.get_domain_info("DNA")
        print(f"\n📚 Domain info: {info}")
