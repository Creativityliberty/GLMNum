"""
GLM Prototype - Enhanced Memory System
======================================
Three-level memory with ∆∞Ο integration and ultra-rapid access.
"""

import time
import hashlib
from typing import Dict, List, Any, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class UltraRapidEmbedding:
    """
    Implements ultra-rapid information embedding across ∆∞Ο domains
    Embeds information with infinite-dimensional richness
    """
    def __init__(self):
        self.embedding_store = {
            "delta": {},      # Probabilistic embeddings
            "infinity": {},   # Transformational embeddings
            "omicron": {}     # Definite embeddings
        }
        self.cross_domain_links = defaultdict(lambda: defaultdict(list))
        self.embedding_count = 0
        
    def embed_information(self, content: Any, content_type: str, domains: List[str] = None) -> str:
        """
        Embed information across specified domains simultaneously
        Returns embedding key for rapid recall
        """
        if domains is None:
            domains = ["delta", "infinity", "omicron"]  # Embed in all by default
        
        # Generate unique embedding key
        embedding_key = self._generate_key(content, content_type)
        
        embedding_data = {
            "content": content,
            "type": content_type,
            "timestamp": time.time(),
            "access_count": 0
        }
        
        # Embed in each specified domain
        for domain in domains:
            if domain in self.embedding_store:
                self.embedding_store[domain][embedding_key] = embedding_data.copy()
                # Add domain-specific metadata
                if domain == "delta":
                    self.embedding_store[domain][embedding_key]["probability"] = 1.0
                elif domain == "infinity":
                    self.embedding_store[domain][embedding_key]["transformation_applicable"] = True
                elif domain == "omicron":
                    self.embedding_store[domain][embedding_key]["definite"] = True
        
        # Create cross-domain links
        for i, domain1 in enumerate(domains):
            for domain2 in domains[i+1:]:
                self.cross_domain_links[domain1][embedding_key].append(domain2)
                self.cross_domain_links[domain2][embedding_key].append(domain1)
        
        self.embedding_count += 1
        return embedding_key
    
    def _generate_key(self, content: Any, content_type: str) -> str:
        """Generate unique embedding key"""
        content_str = str(content) + content_type + str(time.time())
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]
    
    def rapid_recall(self, embedding_key: str, domain: str = "omicron") -> Optional[Dict]:
        """
        Ultra-rapid recall from specified domain
        O(1) hash lookup time
        """
        if domain not in self.embedding_store:
            return None
        
        if embedding_key in self.embedding_store[domain]:
            data = self.embedding_store[domain][embedding_key]
            data["access_count"] += 1
            return data
        
        return None
    
    def context_aware_search(self, query: str, domain: Optional[str] = None, 
                            content_type: Optional[str] = None) -> List[Dict]:
        """
        Search embeddings by context (domain and/or content type)
        """
        results = []
        
        # Determine which stores to search
        stores_to_search = [domain] if domain else ["delta", "infinity", "omicron"]
        
        for store_name in stores_to_search:
            store = self.embedding_store.get(store_name, {})
            for key, data in store.items():
                # Filter by content type if specified
                if content_type and data.get("type") != content_type:
                    continue
                
                # Simple relevance check (can be enhanced with semantic similarity)
                if query.lower() in str(data.get("content", "")).lower():
                    results.append({
                        "key": key,
                        "data": data,
                        "domain": store_name
                    })
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get embedding system statistics"""
        return {
            "total_embeddings": self.embedding_count,
            "delta_count": len(self.embedding_store["delta"]),
            "infinity_count": len(self.embedding_store["infinity"]),
            "omicron_count": len(self.embedding_store["omicron"]),
            "cross_domain_links": sum(len(links) for links in self.cross_domain_links.values())
        }


class EnhancedMemorySystem:
    """
    Three-level memory with ∆∞Ο integration and ultra-rapid access
    """
    def __init__(self):
        # Traditional memory levels
        self.working_memory = {}  # Current active information
        self.episodic_memory = []  # Past experiences
        self.semantic_memory = {}  # General knowledge
        
        # ∆∞Ο-enhanced components
        self.ultra_rapid_embedding = UltraRapidEmbedding()
        
        # Associative connections
        self.associations = defaultdict(list)
        
    def store_working(self, key: str, value: Any):
        """Store in working memory with ultra-rapid embedding"""
        self.working_memory[key] = value
        # Also embed for rapid cross-domain access
        embedding_key = self.ultra_rapid_embedding.embed_information(
            value, "working_memory", ["delta", "omicron"]
        )
        self.associations[key].append(embedding_key)
    
    def store_episodic(self, episode: Dict):
        """Store episodic memory with full ∆∞Ο embedding"""
        self.episodic_memory.append(episode)
        # Embed episode across all domains
        embedding_key = self.ultra_rapid_embedding.embed_information(
            episode, "episode", ["delta", "infinity", "omicron"]
        )
        # Create associations with query if present
        if "query" in episode:
            self.associations[episode["query"]].append(embedding_key)
    
    def store_semantic(self, concept: str, knowledge: Any):
        """Store semantic knowledge"""
        self.semantic_memory[concept] = knowledge
        embedding_key = self.ultra_rapid_embedding.embed_information(
            knowledge, "semantic", ["infinity", "omicron"]
        )
        self.associations[concept].append(embedding_key)
    
    def rapid_retrieve(self, key: str, memory_type: str = "working") -> Any:
        """Ultra-rapid retrieval from specified memory type"""
        if memory_type == "working":
            return self.working_memory.get(key)
        elif memory_type == "semantic":
            return self.semantic_memory.get(key)
        else:
            return None
    
    def context_search(self, query: str, domain: Optional[str] = None) -> List[Dict]:
        """Context-aware search across all memory"""
        return self.ultra_rapid_embedding.context_aware_search(query, domain)
    
    def get_memory_stats(self) -> Dict:
        """Get comprehensive memory statistics"""
        return {
            "working_items": len(self.working_memory),
            "episodes": len(self.episodic_memory),
            "semantic_concepts": len(self.semantic_memory),
            "embedding_stats": self.ultra_rapid_embedding.get_statistics(),
            "associations": len(self.associations)
        }
