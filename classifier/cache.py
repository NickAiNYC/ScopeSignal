"""
Simple file-based cache for classification results.
Reduces API costs and improves response time for repeated queries.
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional


class ResultCache:
    """
    File-based cache for classification results.
    Uses cache_key from classifier to identify unique update+trade combinations.
    """
    
    def __init__(self, cache_dir: str = ".scopesignal_cache", ttl_seconds: int = 86400):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_seconds: Time-to-live for cache entries (default: 24 hours)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl_seconds = ttl_seconds
    
    def get(self, cache_key: str) -> Optional[Dict]:
        """
        Retrieve cached result if it exists and is not expired.
        
        Args:
            cache_key: SHA256 hash of update+trade
            
        Returns:
            Cached result dict or None if not found/expired
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
            
            # Check expiration
            cached_time = cached.get("_cache_timestamp", 0)
            age = time.time() - cached_time
            
            if age > self.ttl_seconds:
                # Expired - clean up
                cache_file.unlink()
                return None
            
            # Remove cache metadata before returning
            result = cached.copy()
            result.pop("_cache_timestamp", None)
            
            # Mark as cache hit
            if "_metadata" not in result:
                result["_metadata"] = {}
            result["_metadata"]["cache_hit"] = True
            result["_metadata"]["cache_age_seconds"] = int(age)
            
            return result
            
        except (json.JSONDecodeError, OSError):
            # Corrupted cache file - remove it
            cache_file.unlink(missing_ok=True)
            return None
    
    def set(self, cache_key: str, result: Dict) -> None:
        """
        Store result in cache.
        
        Args:
            cache_key: SHA256 hash of update+trade
            result: Classification result to cache
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        # Add timestamp
        cached_result = result.copy()
        cached_result["_cache_timestamp"] = time.time()
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cached_result, f, indent=2)
        except OSError:
            # Cache write failed - not critical, just log
            pass
    
    def clear(self) -> int:
        """
        Clear all cached results.
        
        Returns:
            Number of cache entries removed
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        return count
    
    def stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache size, oldest/newest entries
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        
        if not cache_files:
            return {
                "entries": 0,
                "size_bytes": 0
            }
        
        total_size = sum(f.stat().st_size for f in cache_files)
        timestamps = []
        
        for cache_file in cache_files:
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                    if "_cache_timestamp" in cached:
                        timestamps.append(cached["_cache_timestamp"])
            except (json.JSONDecodeError, OSError):
                pass
        
        now = time.time()
        
        return {
            "entries": len(cache_files),
            "size_bytes": total_size,
            "oldest_age_seconds": int(now - min(timestamps)) if timestamps else 0,
            "newest_age_seconds": int(now - max(timestamps)) if timestamps else 0
        }


if __name__ == "__main__":
    # Quick test
    cache = ResultCache(cache_dir="/tmp/test_cache")
    
    # Test set/get
    test_result = {
        "classification": "CLOSED",
        "confidence": 85,
        "reasoning": "Test result"
    }
    
    cache.set("test_key_123", test_result)
    retrieved = cache.get("test_key_123")
    
    assert retrieved is not None
    assert retrieved["classification"] == "CLOSED"
    # Check that cache_hit metadata was added
    assert "_metadata" in retrieved
    assert retrieved["_metadata"]["cache_hit"] is True
    
    # Test stats
    stats = cache.stats()
    print(f"Cache stats: {stats}")
    
    # Test clear
    cleared = cache.clear()
    print(f"Cleared {cleared} entries")
    
    print("✓ Cache tests passed")
