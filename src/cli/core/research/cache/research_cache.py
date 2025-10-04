"""
Research cache for storing and retrieving research results
"""

import os
import json
import hashlib
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class ResearchCache:
    """Cache system for research results"""
    
    def __init__(self, cache_directory: str = "memory-bank/.research_cache"):
        self.cache_directory = cache_directory
        self.cache_ttl = 86400  # 24 hours in seconds
        self.max_cache_size = 1000  # Maximum number of cached items
        self.compression_enabled = False  # Could be enabled for large caches
        
        # Ensure cache directory exists
        os.makedirs(self.cache_directory, exist_ok=True)
        
        # Cache metadata
        self.metadata_file = os.path.join(self.cache_directory, "cache_metadata.json")
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return {
            'created_at': datetime.now().isoformat(),
            'last_cleanup': datetime.now().isoformat(),
            'total_entries': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def _save_metadata(self):
        """Save cache metadata"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save cache metadata: {e}")
    
    def _generate_cache_key(self, query: str, research_type: str, **kwargs) -> str:
        """Generate cache key for research query"""
        # Create a deterministic key from query parameters
        key_data = {
            'query': query.lower().strip(),
            'research_type': research_type,
            **kwargs
        }
        
        # Sort keys for consistent hashing
        sorted_key_data = json.dumps(key_data, sort_keys=True)
        
        # Generate hash
        return hashlib.md5(sorted_key_data.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> str:
        """Get file path for cache entry"""
        return os.path.join(self.cache_directory, f"{cache_key}.json")
    
    def _is_cache_valid(self, cache_file: str) -> bool:
        """Check if cache entry is still valid"""
        if not os.path.exists(cache_file):
            return False
        
        # Check file modification time
        file_time = os.path.getmtime(cache_file)
        current_time = time.time()
        
        return (current_time - file_time) < self.cache_ttl
    
    def store_research(self, cache_key: str, research_data: Dict[str, Any]) -> bool:
        """
        Store research data in cache
        
        Args:
            cache_key: Cache key for the research
            research_data: Research data to cache
        
        Returns:
            True if successfully cached, False otherwise
        """
        try:
            cache_file = self._get_cache_file_path(cache_key)
            
            # Prepare cache entry
            cache_entry = {
                'cache_key': cache_key,
                'created_at': datetime.now().isoformat(),
                'data': research_data,
                'metadata': {
                    'size': len(json.dumps(research_data)),
                    'compressed': self.compression_enabled
                }
            }
            
            # Write to cache file
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, indent=2)
            
            # Update metadata
            self.metadata['total_entries'] += 1
            
            # Check if cleanup is needed
            if self.metadata['total_entries'] > self.max_cache_size:
                self._cleanup_cache()
            
            return True
            
        except (IOError, json.JSONEncodeError) as e:
            print(f"Warning: Could not cache research data: {e}")
            return False
    
    def get_research(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve research data from cache
        
        Args:
            cache_key: Cache key for the research
        
        Returns:
            Cached research data or None if not found/invalid
        """
        cache_file = self._get_cache_file_path(cache_key)
        
        if not self._is_cache_valid(cache_file):
            if os.path.exists(cache_file):
                # Remove expired cache file
                os.remove(cache_file)
                self.metadata['total_entries'] = max(0, self.metadata['total_entries'] - 1)
            
            self.metadata['cache_misses'] += 1
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_entry = json.load(f)
            
            # Update access time
            cache_entry['last_accessed'] = datetime.now().isoformat()
            
            # Rewrite with updated access time
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, indent=2)
            
            self.metadata['cache_hits'] += 1
            return cache_entry['data']
            
        except (IOError, json.JSONDecodeError) as e:
            print(f"Warning: Could not read cache file: {e}")
            self.metadata['cache_misses'] += 1
            return None
    
    def search_research(self, query: str) -> List[Dict[str, Any]]:
        """
        Search cached research by query
        
        Args:
            query: Search query
        
        Returns:
            List of matching cached research entries
        """
        results = []
        query_lower = query.lower()
        
        # Scan all cache files
        for filename in os.listdir(self.cache_directory):
            if filename.endswith('.json') and filename != 'cache_metadata.json':
                cache_file = os.path.join(self.cache_directory, filename)
                
                if not self._is_cache_valid(cache_file):
                    continue
                
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_entry = json.load(f)
                    
                    research_data = cache_entry.get('data', {})
                    
                    # Search in various fields
                    searchable_text = []
                    
                    # Extract searchable content
                    if 'query' in research_data:
                        searchable_text.append(research_data['query'].lower())
                    
                    if 'synthesized_summary' in research_data:
                        searchable_text.append(research_data['synthesized_summary'].lower())
                    
                    if 'key_insights' in research_data:
                        searchable_text.extend([insight.lower() for insight in research_data['key_insights']])
                    
                    if 'recommendations' in research_data:
                        searchable_text.extend([rec.lower() for rec in research_data['recommendations']])
                    
                    # Check if query matches
                    combined_text = ' '.join(searchable_text)
                    if query_lower in combined_text:
                        results.append({
                            'cache_key': cache_entry['cache_key'],
                            'research_data': research_data,
                            'created_at': cache_entry['created_at'],
                            'match_score': self._calculate_match_score(query_lower, combined_text)
                        })
                
                except (IOError, json.JSONDecodeError):
                    continue
        
        # Sort by match score and creation time
        results.sort(key=lambda x: (x['match_score'], x['created_at']), reverse=True)
        
        return results[:10]  # Limit to top 10 results
    
    def _calculate_match_score(self, query: str, text: str) -> float:
        """Calculate match score for search results"""
        if not query or not text:
            return 0.0
        
        # Simple scoring based on query word matches
        query_words = set(query.split())
        text_words = set(text.split())
        
        if not query_words:
            return 0.0
        
        # Calculate overlap ratio
        overlap = len(query_words.intersection(text_words))
        return overlap / len(query_words)
    
    def get_recent_research(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent research entries
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of recent research entries
        """
        entries = []
        
        # Scan all cache files
        for filename in os.listdir(self.cache_directory):
            if filename.endswith('.json') and filename != 'cache_metadata.json':
                cache_file = os.path.join(self.cache_directory, filename)
                
                if not self._is_cache_valid(cache_file):
                    continue
                
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_entry = json.load(f)
                    
                    entries.append({
                        'cache_key': cache_entry['cache_key'],
                        'research_data': cache_entry.get('data', {}),
                        'created_at': cache_entry['created_at'],
                        'last_accessed': cache_entry.get('last_accessed')
                    })
                
                except (IOError, json.JSONDecodeError):
                    continue
        
        # Sort by creation time
        entries.sort(key=lambda x: x['created_at'], reverse=True)
        
        return entries[:limit]
    
    def clear_cache(self) -> bool:
        """Clear all cached research data"""
        try:
            # Remove all cache files except metadata
            for filename in os.listdir(self.cache_directory):
                if filename.endswith('.json') and filename != 'cache_metadata.json':
                    cache_file = os.path.join(self.cache_directory, filename)
                    os.remove(cache_file)
            
            # Reset metadata
            self.metadata['total_entries'] = 0
            self._save_metadata()
            
            return True
            
        except IOError as e:
            print(f"Error clearing cache: {e}")
            return False
    
    def cleanup_cache(self) -> Dict[str, Any]:
        """Clean up expired and old cache entries"""
        cleanup_stats = {
            'expired_removed': 0,
            'old_removed': 0,
            'total_removed': 0,
            'remaining_entries': 0
        }
        
        try:
            current_time = time.time()
            entries_with_age = []
            
            # Collect all cache files with their ages
            for filename in os.listdir(self.cache_directory):
                if filename.endswith('.json') and filename != 'cache_metadata.json':
                    cache_file = os.path.join(self.cache_directory, filename)
                    
                    try:
                        file_time = os.path.getmtime(cache_file)
                        age_seconds = current_time - file_time
                        
                        # Remove expired entries
                        if age_seconds > self.cache_ttl:
                            os.remove(cache_file)
                            cleanup_stats['expired_removed'] += 1
                            continue
                        
                        entries_with_age.append((cache_file, age_seconds))
                    
                    except (IOError, OSError):
                        continue
            
            # If still too many entries, remove oldest ones
            if len(entries_with_age) > self.max_cache_size:
                # Sort by age (oldest first)
                entries_with_age.sort(key=lambda x: x[1], reverse=True)
                
                # Remove oldest entries
                to_remove = len(entries_with_age) - self.max_cache_size
                for cache_file, _ in entries_with_age[:to_remove]:
                    try:
                        os.remove(cache_file)
                        cleanup_stats['old_removed'] += 1
                    except (IOError, OSError):
                        continue
            
            cleanup_stats['total_removed'] = cleanup_stats['expired_removed'] + cleanup_stats['old_removed']
            cleanup_stats['remaining_entries'] = len(entries_with_age) - cleanup_stats['old_removed']
            
            # Update metadata
            self.metadata['total_entries'] = cleanup_stats['remaining_entries']
            self.metadata['last_cleanup'] = datetime.now().isoformat()
            self._save_metadata()
            
        except Exception as e:
            print(f"Error during cache cleanup: {e}")
        
        return cleanup_stats
    
    def _cleanup_cache(self):
        """Internal cache cleanup"""
        self.cleanup_cache()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_files = 0
        total_size = 0
        
        # Count files and calculate size
        for filename in os.listdir(self.cache_directory):
            if filename.endswith('.json') and filename != 'cache_metadata.json':
                cache_file = os.path.join(self.cache_directory, filename)
                if os.path.exists(cache_file):
                    total_files += 1
                    total_size += os.path.getsize(cache_file)
        
        # Calculate hit rate
        total_requests = self.metadata['cache_hits'] + self.metadata['cache_misses']
        hit_rate = (self.metadata['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_entries': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_hits': self.metadata['cache_hits'],
            'cache_misses': self.metadata['cache_misses'],
            'hit_rate_percent': round(hit_rate, 2),
            'cache_ttl_hours': self.cache_ttl / 3600,
            'max_cache_size': self.max_cache_size,
            'created_at': self.metadata['created_at'],
            'last_cleanup': self.metadata['last_cleanup']
        }
    
    def invalidate_research(self, cache_key: str) -> bool:
        """Invalidate specific research cache entry"""
        cache_file = self._get_cache_file_path(cache_key)
        
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                self.metadata['total_entries'] = max(0, self.metadata['total_entries'] - 1)
                return True
            except IOError:
                return False
        
        return False
