"""
Persistent Storage for GLM v4.0
================================

Saves and restores engine state, cache, and learned domains.
Enables continuity across restarts.

Features:
- State serialization
- Cache persistence
- Learned domains storage
- Checkpoint management
- Recovery mechanisms
"""

import json
import pickle
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class PersistentStorage:
    """
    Manages persistent storage for GLM engine state.
    """
    
    def __init__(self, storage_dir: str = "./glm_storage"):
        """
        Initialize persistent storage.
        
        Args:
            storage_dir: Root directory for storage
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.domains_dir = self.storage_dir / "domains"
        self.cache_dir = self.storage_dir / "cache"
        self.checkpoints_dir = self.storage_dir / "checkpoints"
        self.metadata_dir = self.storage_dir / "metadata"
        
        for d in [self.domains_dir, self.cache_dir, self.checkpoints_dir, self.metadata_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Persistent storage initialized at: {self.storage_dir}")
    
    # ========================================================================
    # STATE MANAGEMENT
    # ========================================================================
    
    def save_engine_state(self, engine_state: Dict[str, Any], checkpoint_name: Optional[str] = None) -> str:
        """
        Save complete engine state.
        
        Args:
            engine_state: Engine state dictionary
            checkpoint_name: Optional checkpoint name
            
        Returns:
            Checkpoint ID
        """
        checkpoint_id = checkpoint_name or self._generate_checkpoint_id()
        checkpoint_path = self.checkpoints_dir / f"{checkpoint_id}.json"
        
        try:
            # Add metadata
            state_with_meta = {
                "checkpoint_id": checkpoint_id,
                "timestamp": datetime.now().isoformat(),
                "state": engine_state,
            }
            
            with open(checkpoint_path, "w") as f:
                json.dump(state_with_meta, f, indent=2, default=str)
            
            logger.info(f"Saved engine state: {checkpoint_id}")
            return checkpoint_id
        except Exception as e:
            logger.error(f"Failed to save engine state: {e}")
            raise
    
    def load_engine_state(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        Load engine state from checkpoint.
        
        Args:
            checkpoint_id: Checkpoint ID to load
            
        Returns:
            Engine state dictionary
        """
        checkpoint_path = self.checkpoints_dir / f"{checkpoint_id}.json"
        
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_id}")
        
        try:
            with open(checkpoint_path, "r") as f:
                data = json.load(f)
            
            logger.info(f"Loaded engine state: {checkpoint_id}")
            return data["state"]
        except Exception as e:
            logger.error(f"Failed to load engine state: {e}")
            raise
    
    def get_latest_checkpoint(self) -> Optional[str]:
        """Get the most recent checkpoint ID"""
        checkpoints = list(self.checkpoints_dir.glob("*.json"))
        
        if not checkpoints:
            return None
        
        # Sort by modification time
        latest = max(checkpoints, key=lambda p: p.stat().st_mtime)
        return latest.stem
    
    # ========================================================================
    # DOMAIN STORAGE
    # ========================================================================
    
    def save_domain(self, domain_name: str, domain_data: Dict[str, Any]) -> bool:
        """
        Save domain configuration.
        
        Args:
            domain_name: Domain name
            domain_data: Domain data dictionary
            
        Returns:
            True if successful
        """
        try:
            domain_path = self.domains_dir / f"{domain_name}.json"
            
            with open(domain_path, "w") as f:
                json.dump(domain_data, f, indent=2, default=str)
            
            logger.info(f"Saved domain: {domain_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save domain: {e}")
            return False
    
    def load_domain(self, domain_name: str) -> Optional[Dict[str, Any]]:
        """
        Load domain configuration.
        
        Args:
            domain_name: Domain name
            
        Returns:
            Domain data dictionary or None
        """
        try:
            domain_path = self.domains_dir / f"{domain_name}.json"
            
            if not domain_path.exists():
                return None
            
            with open(domain_path, "r") as f:
                data = json.load(f)
            
            logger.info(f"Loaded domain: {domain_name}")
            return data
        except Exception as e:
            logger.error(f"Failed to load domain: {e}")
            return None
    
    def list_domains(self) -> List[str]:
        """List all saved domains"""
        domains = [p.stem for p in self.domains_dir.glob("*.json")]
        return sorted(domains)
    
    def delete_domain(self, domain_name: str) -> bool:
        """Delete a domain"""
        try:
            domain_path = self.domains_dir / f"{domain_name}.json"
            if domain_path.exists():
                domain_path.unlink()
                logger.info(f"Deleted domain: {domain_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete domain: {e}")
            return False
    
    # ========================================================================
    # CACHE MANAGEMENT
    # ========================================================================
    
    def save_cache(self, cache_key: str, cache_data: Any) -> bool:
        """
        Save cache entry.
        
        Args:
            cache_key: Cache key
            cache_data: Data to cache
            
        Returns:
            True if successful
        """
        try:
            cache_path = self.cache_dir / f"{self._hash_key(cache_key)}.pkl"
            
            with open(cache_path, "wb") as f:
                pickle.dump(cache_data, f)
            
            logger.debug(f"Cached: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to cache: {e}")
            return False
    
    def load_cache(self, cache_key: str) -> Optional[Any]:
        """
        Load cache entry.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached data or None
        """
        try:
            cache_path = self.cache_dir / f"{self._hash_key(cache_key)}.pkl"
            
            if not cache_path.exists():
                return None
            
            with open(cache_path, "rb") as f:
                data = pickle.load(f)
            
            logger.debug(f"Cache hit: {cache_key}")
            return data
        except Exception as e:
            logger.debug(f"Cache miss: {cache_key}")
            return None
    
    def clear_cache(self) -> bool:
        """Clear all cache"""
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            
            logger.info("Cleared cache")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob("*.pkl"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "cache_entries": len(cache_files),
            "total_size_mb": total_size / (1024 * 1024),
            "cache_dir": str(self.cache_dir),
        }
    
    # ========================================================================
    # METADATA MANAGEMENT
    # ========================================================================
    
    def save_metadata(self, metadata_key: str, metadata: Dict[str, Any]) -> bool:
        """
        Save metadata.
        
        Args:
            metadata_key: Metadata key
            metadata: Metadata dictionary
            
        Returns:
            True if successful
        """
        try:
            metadata_path = self.metadata_dir / f"{metadata_key}.json"
            
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2, default=str)
            
            logger.info(f"Saved metadata: {metadata_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            return False
    
    def load_metadata(self, metadata_key: str) -> Optional[Dict[str, Any]]:
        """
        Load metadata.
        
        Args:
            metadata_key: Metadata key
            
        Returns:
            Metadata dictionary or None
        """
        try:
            metadata_path = self.metadata_dir / f"{metadata_key}.json"
            
            if not metadata_path.exists():
                return None
            
            with open(metadata_path, "r") as f:
                data = json.load(f)
            
            logger.info(f"Loaded metadata: {metadata_key}")
            return data
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            return None
    
    # ========================================================================
    # BACKUP & RECOVERY
    # ========================================================================
    
    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """
        Create a full backup.
        
        Args:
            backup_name: Optional backup name
            
        Returns:
            Backup ID
        """
        import shutil
        
        backup_id = backup_name or self._generate_backup_id()
        backup_path = self.storage_dir / f"backup_{backup_id}"
        
        try:
            shutil.copytree(self.storage_dir, backup_path, dirs_exist_ok=True)
            logger.info(f"Created backup: {backup_id}")
            return backup_id
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise
    
    def restore_backup(self, backup_id: str) -> bool:
        """
        Restore from backup.
        
        Args:
            backup_id: Backup ID to restore
            
        Returns:
            True if successful
        """
        import shutil
        
        backup_path = self.storage_dir / f"backup_{backup_id}"
        
        if not backup_path.exists():
            logger.error(f"Backup not found: {backup_id}")
            return False
        
        try:
            # Create recovery backup first
            self.create_backup("pre_restore")
            
            # Restore
            for item in backup_path.iterdir():
                if item.name != f"backup_{backup_id}":
                    dest = self.storage_dir / item.name
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
            
            logger.info(f"Restored backup: {backup_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
    
    def list_backups(self) -> List[str]:
        """List all backups"""
        backups = [
            d.name.replace("backup_", "")
            for d in self.storage_dir.iterdir()
            if d.is_dir() and d.name.startswith("backup_")
        ]
        return sorted(backups)
    
    # ========================================================================
    # STATISTICS & MONITORING
    # ========================================================================
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        def get_dir_size(path):
            total = 0
            for item in path.rglob("*"):
                if item.is_file():
                    total += item.stat().st_size
            return total
        
        return {
            "storage_dir": str(self.storage_dir),
            "total_size_mb": get_dir_size(self.storage_dir) / (1024 * 1024),
            "domains": {
                "count": len(self.list_domains()),
                "size_mb": get_dir_size(self.domains_dir) / (1024 * 1024),
            },
            "cache": self.get_cache_stats(),
            "checkpoints": {
                "count": len(list(self.checkpoints_dir.glob("*.json"))),
                "size_mb": get_dir_size(self.checkpoints_dir) / (1024 * 1024),
            },
            "backups": {
                "count": len(self.list_backups()),
                "size_mb": get_dir_size(self.storage_dir / "backup_*") / (1024 * 1024) if any(self.storage_dir.glob("backup_*")) else 0,
            },
        }
    
    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================
    
    def _generate_checkpoint_id(self) -> str:
        """Generate unique checkpoint ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"checkpoint_{timestamp}"
    
    def _generate_backup_id(self) -> str:
        """Generate unique backup ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"backup_{timestamp}"
    
    def _hash_key(self, key: str) -> str:
        """Hash cache key"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def cleanup_old_checkpoints(self, keep_count: int = 10) -> int:
        """
        Remove old checkpoints, keeping only the most recent.
        
        Args:
            keep_count: Number of checkpoints to keep
            
        Returns:
            Number of checkpoints deleted
        """
        checkpoints = sorted(
            self.checkpoints_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        deleted = 0
        for checkpoint in checkpoints[keep_count:]:
            checkpoint.unlink()
            deleted += 1
        
        if deleted > 0:
            logger.info(f"Deleted {deleted} old checkpoints")
        
        return deleted


# ============================================================================
# INTEGRATION WITH SYMBOLIC ENGINE
# ============================================================================

class PersistentSymbolicEngine:
    """
    Wrapper around SymbolicEngine that adds persistence.
    """
    
    def __init__(self, base_engine, storage_dir: str = "./glm_storage"):
        """
        Initialize persistent engine.
        
        Args:
            base_engine: SymbolicEngine instance
            storage_dir: Storage directory
        """
        self.engine = base_engine
        self.storage = PersistentStorage(storage_dir)
        
        # Try to restore from latest checkpoint
        latest = self.storage.get_latest_checkpoint()
        if latest:
            try:
                state = self.storage.load_engine_state(latest)
                self._restore_state(state)
                logger.info(f"Restored engine from checkpoint: {latest}")
            except Exception as e:
                logger.warning(f"Failed to restore checkpoint: {e}")
    
    def _restore_state(self, state: Dict[str, Any]) -> None:
        """Restore engine state"""
        # Restore domains
        for domain_name, domain_data in state.get("domains", {}).items():
            self.engine.register_domain(domain_name, domain_data)
    
    def _get_state(self) -> Dict[str, Any]:
        """Get current engine state"""
        return {
            "domains": {
                name: domain.__dict__
                for name, domain in self.engine.domains.items()
            },
            "timestamp": datetime.now().isoformat(),
        }
    
    def save_checkpoint(self, name: Optional[str] = None) -> str:
        """Save checkpoint"""
        state = self._get_state()
        return self.storage.save_engine_state(state, name)
    
    def load_checkpoint(self, checkpoint_id: str) -> bool:
        """Load checkpoint"""
        try:
            state = self.storage.load_engine_state(checkpoint_id)
            self._restore_state(state)
            return True
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return False
    
    def __getattr__(self, name):
        """Delegate to base engine"""
        return getattr(self.engine, name)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    storage = PersistentStorage()
    
    # Save some data
    storage.save_domain("test_domain", {"features": ["f1", "f2"]})
    storage.save_cache("test_key", {"data": "value"})
    storage.save_metadata("test_meta", {"version": "1.0"})
    
    # Load data
    domain = storage.load_domain("test_domain")
    print(f"Loaded domain: {domain}")
    
    cache = storage.load_cache("test_key")
    print(f"Loaded cache: {cache}")
    
    # Get stats
    stats = storage.get_storage_stats()
    print(f"Storage stats: {json.dumps(stats, indent=2)}")
