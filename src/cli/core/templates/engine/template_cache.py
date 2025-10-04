# src/cli/core/templates/engine/template_cache.py
"""
Template caching system for improved performance and template management.
Provides caching, versioning, and template storage functionality.
"""

from typing import Dict, List, Any, Optional
import os
import json
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass
class CacheEntry:
    """Represents a cached template entry."""
    key: str
    template_data: Dict[str, Any]
    complexity_level: int
    template_type: str
    created_at: datetime
    last_accessed: datetime
    access_count: int
    size_bytes: int
    ttl_seconds: int = 86400  # 24 hours default TTL


@dataclass
class CacheStats:
    """Cache statistics and performance metrics."""
    total_entries: int
    total_size_bytes: int
    hit_count: int
    miss_count: int
    eviction_count: int
    last_cleanup: Optional[datetime]


class TemplateCache:
    """
    Template caching system with TTL, LRU eviction, and statistics.
    """
    
    def __init__(self, cache_directory: str = ".template_cache", max_size_mb: int = 100):
        self.cache_directory = cache_directory
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache_entries: Dict[str, CacheEntry] = {}
        self.stats = CacheStats(
            total_entries=0,
            total_size_bytes=0,
            hit_count=0,
            miss_count=0,
            eviction_count=0,
            last_cleanup=None
        )
        
        # Initialize cache directory
        os.makedirs(cache_directory, exist_ok=True)
        
        # Load existing cache
        self._load_cache()
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get template data from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Template data if found and not expired, None otherwise
        """
        if key not in self.cache_entries:
            self.stats.miss_count += 1
            return None
        
        entry = self.cache_entries[key]
        
        # Check if entry has expired
        if self._is_expired(entry):
            self._remove_entry(key)
            self.stats.miss_count += 1
            return None
        
        # Update access information
        entry.last_accessed = datetime.now()
        entry.access_count += 1
        self.stats.hit_count += 1
        
        # Save updated entry
        self._save_entry(entry)
        
        return entry.template_data
    
    def put(self, 
            key: str, 
            template_data: Dict[str, Any], 
            complexity_level: int,
            template_type: str = "generic",
            ttl_seconds: int = 86400) -> bool:
        """
        Store template data in cache.
        
        Args:
            key: Cache key
            template_data: Template data to cache
            complexity_level: Complexity level of the template
            template_type: Type of template
            ttl_seconds: Time to live in seconds
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Calculate data size
            data_json = json.dumps(template_data, default=str)
            size_bytes = len(data_json.encode('utf-8'))
            
            # Check if we need to evict entries
            if self._would_exceed_size_limit(size_bytes):
                self._evict_entries(size_bytes)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                template_data=template_data,
                complexity_level=complexity_level,
                template_type=template_type,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                size_bytes=size_bytes,
                ttl_seconds=ttl_seconds
            )
            
            # Store entry
            self.cache_entries[key] = entry
            self.stats.total_entries += 1
            self.stats.total_size_bytes += size_bytes
            
            # Save to disk
            self._save_entry(entry)
            
            return True
            
        except Exception as e:
            print(f"Error caching template: {e}")
            return False
    
    def generate_key(self, 
                    complexity_level: int, 
                    template_type: str, 
                    description: str = "") -> str:
        """
        Generate a cache key for template data.
        
        Args:
            complexity_level: Complexity level
            template_type: Type of template
            description: Optional description for uniqueness
        
        Returns:
            Generated cache key
        """
        key_data = f"{complexity_level}:{template_type}:{description}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    def invalidate(self, key: str) -> bool:
        """
        Invalidate a cache entry.
        
        Args:
            key: Cache key to invalidate
        
        Returns:
            True if found and removed, False otherwise
        """
        if key in self.cache_entries:
            self._remove_entry(key)
            return True
        return False
    
    def invalidate_by_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching a pattern.
        
        Args:
            pattern: Pattern to match against cache keys
        
        Returns:
            Number of entries invalidated
        """
        keys_to_remove = []
        
        for key in self.cache_entries.keys():
            if pattern in key:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            self._remove_entry(key)
        
        return len(keys_to_remove)
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired cache entries.
        
        Returns:
            Number of entries removed
        """
        keys_to_remove = []
        
        for key, entry in self.cache_entries.items():
            if self._is_expired(entry):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            self._remove_entry(key)
        
        self.stats.last_cleanup = datetime.now()
        
        return len(keys_to_remove)
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self.stats
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information."""
        return {
            "total_entries": self.stats.total_entries,
            "total_size_mb": self.stats.total_size_bytes / (1024 * 1024),
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
            "hit_rate": self._calculate_hit_rate(),
            "oldest_entry": self._get_oldest_entry_age(),
            "newest_entry": self._get_newest_entry_age(),
            "entries_by_level": self._get_entries_by_level(),
            "entries_by_type": self._get_entries_by_type()
        }
    
    def clear(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            Number of entries cleared
        """
        entry_count = len(self.cache_entries)
        
        # Remove all entries
        for key in list(self.cache_entries.keys()):
            self._remove_entry(key)
        
        # Reset stats
        self.stats.total_entries = 0
        self.stats.total_size_bytes = 0
        
        return entry_count
    
    def export_cache(self, file_path: str) -> bool:
        """
        Export cache data to a file.
        
        Args:
            file_path: Path to export file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            export_data = {
                "cache_entries": {},
                "stats": asdict(self.stats),
                "exported_at": datetime.now().isoformat()
            }
            
            # Convert entries to serializable format
            for key, entry in self.cache_entries.items():
                entry_dict = asdict(entry)
                # Convert datetime objects to ISO strings
                entry_dict["created_at"] = entry.created_at.isoformat()
                entry_dict["last_accessed"] = entry.last_accessed.isoformat()
                export_data["cache_entries"][key] = entry_dict
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error exporting cache: {e}")
            return False
    
    def import_cache(self, file_path: str) -> bool:
        """
        Import cache data from a file.
        
        Args:
            file_path: Path to import file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Clear existing cache
            self.clear()
            
            # Import entries
            for key, entry_data in import_data.get("cache_entries", {}).items():
                # Convert ISO strings back to datetime objects
                entry_data["created_at"] = datetime.fromisoformat(entry_data["created_at"])
                entry_data["last_accessed"] = datetime.fromisoformat(entry_data["last_accessed"])
                
                entry = CacheEntry(**entry_data)
                self.cache_entries[key] = entry
            
            # Import stats
            if "stats" in import_data:
                stats_data = import_data["stats"]
                stats_data["last_cleanup"] = (
                    datetime.fromisoformat(stats_data["last_cleanup"]) 
                    if stats_data.get("last_cleanup") else None
                )
                self.stats = CacheStats(**stats_data)
            
            return True
            
        except Exception as e:
            print(f"Error importing cache: {e}")
            return False
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if a cache entry has expired."""
        expiry_time = entry.created_at + timedelta(seconds=entry.ttl_seconds)
        return datetime.now() > expiry_time
    
    def _would_exceed_size_limit(self, new_entry_size: int) -> bool:
        """Check if adding a new entry would exceed size limit."""
        return self.stats.total_size_bytes + new_entry_size > self.max_size_bytes
    
    def _evict_entries(self, required_space: int) -> None:
        """Evict entries to make space for new entry."""
        # Sort entries by last accessed time (LRU)
        sorted_entries = sorted(
            self.cache_entries.items(),
            key=lambda x: x[1].last_accessed
        )
        
        freed_space = 0
        for key, entry in sorted_entries:
            if freed_space >= required_space:
                break
            
            self._remove_entry(key)
            freed_space += entry.size_bytes
            self.stats.eviction_count += 1
    
    def _remove_entry(self, key: str) -> None:
        """Remove an entry from cache."""
        if key in self.cache_entries:
            entry = self.cache_entries[key]
            
            # Update stats
            self.stats.total_entries -= 1
            self.stats.total_size_bytes -= entry.size_bytes
            
            # Remove from memory
            del self.cache_entries[key]
            
            # Remove from disk
            self._delete_entry_file(key)
    
    def _save_entry(self, entry: CacheEntry) -> None:
        """Save cache entry to disk."""
        try:
            entry_file = os.path.join(self.cache_directory, f"{entry.key}.json")
            
            # Convert to serializable format
            entry_data = asdict(entry)
            entry_data["created_at"] = entry.created_at.isoformat()
            entry_data["last_accessed"] = entry.last_accessed.isoformat()
            
            with open(entry_file, 'w', encoding='utf-8') as f:
                json.dump(entry_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving cache entry: {e}")
    
    def _delete_entry_file(self, key: str) -> None:
        """Delete cache entry file from disk."""
        try:
            entry_file = os.path.join(self.cache_directory, f"{key}.json")
            if os.path.exists(entry_file):
                os.remove(entry_file)
        except Exception as e:
            print(f"Error deleting cache entry file: {e}")
    
    def _load_cache(self) -> None:
        """Load cache entries from disk."""
        try:
            if not os.path.exists(self.cache_directory):
                return
            
            for filename in os.listdir(self.cache_directory):
                if filename.endswith('.json'):
                    key = filename[:-5]  # Remove .json extension
                    entry_file = os.path.join(self.cache_directory, filename)
                    
                    with open(entry_file, 'r', encoding='utf-8') as f:
                        entry_data = json.load(f)
                    
                    # Convert ISO strings back to datetime objects
                    entry_data["created_at"] = datetime.fromisoformat(entry_data["created_at"])
                    entry_data["last_accessed"] = datetime.fromisoformat(entry_data["last_accessed"])
                    
                    entry = CacheEntry(**entry_data)
                    
                    # Only load non-expired entries
                    if not self._is_expired(entry):
                        self.cache_entries[key] = entry
                    else:
                        # Remove expired entry file
                        self._delete_entry_file(key)
            
            # Update stats
            self.stats.total_entries = len(self.cache_entries)
            self.stats.total_size_bytes = sum(entry.size_bytes for entry in self.cache_entries.values())
            
        except Exception as e:
            print(f"Error loading cache: {e}")
    
    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_requests = self.stats.hit_count + self.stats.miss_count
        return (self.stats.hit_count / total_requests) if total_requests > 0 else 0.0
    
    def _get_oldest_entry_age(self) -> Optional[timedelta]:
        """Get age of oldest cache entry."""
        if not self.cache_entries:
            return None
        
        oldest_entry = min(self.cache_entries.values(), key=lambda x: x.created_at)
        return datetime.now() - oldest_entry.created_at
    
    def _get_newest_entry_age(self) -> Optional[timedelta]:
        """Get age of newest cache entry."""
        if not self.cache_entries:
            return None
        
        newest_entry = max(self.cache_entries.values(), key=lambda x: x.created_at)
        return datetime.now() - newest_entry.created_at
    
    def _get_entries_by_level(self) -> Dict[int, int]:
        """Get count of entries by complexity level."""
        level_counts = {}
        for entry in self.cache_entries.values():
            level = entry.complexity_level
            level_counts[level] = level_counts.get(level, 0) + 1
        return level_counts
    
    def _get_entries_by_type(self) -> Dict[str, int]:
        """Get count of entries by template type."""
        type_counts = {}
        for entry in self.cache_entries.values():
            template_type = entry.template_type
            type_counts[template_type] = type_counts.get(template_type, 0) + 1
        return type_counts
