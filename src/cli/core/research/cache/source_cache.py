"""
Source cache for storing and managing research sources
"""

import os
import json
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class SourceCache:
    """Cache system for research sources"""
    
    def __init__(self, cache_directory: str = "memory-bank/.source_cache"):
        self.cache_directory = cache_directory
        self.source_ttl = 604800  # 7 days in seconds
        self.max_sources_per_domain = 100
        
        # Ensure cache directory exists
        os.makedirs(self.cache_directory, exist_ok=True)
        
        # Source metadata
        self.metadata_file = os.path.join(self.cache_directory, "source_metadata.json")
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load source cache metadata"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return {
            'created_at': datetime.now().isoformat(),
            'total_sources': 0,
            'domains': {},
            'last_cleanup': datetime.now().isoformat()
        }
    
    def _save_metadata(self):
        """Save source cache metadata"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save source metadata: {e}")
    
    def _generate_source_key(self, url: str) -> str:
        """Generate cache key for source URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_source_file_path(self, source_key: str) -> str:
        """Get file path for source cache entry"""
        return os.path.join(self.cache_directory, f"{source_key}.json")
    
    def store_source(self, source_data: Dict[str, Any]) -> bool:
        """
        Store source data in cache
        
        Args:
            source_data: Source data to cache
        
        Returns:
            True if successfully cached, False otherwise
        """
        try:
            url = source_data.get('url', '')
            if not url:
                return False
            
            source_key = self._generate_source_key(url)
            source_file = self._get_source_file_path(source_key)
            
            # Prepare cache entry
            cache_entry = {
                'source_key': source_key,
                'url': url,
                'cached_at': datetime.now().isoformat(),
                'source_data': source_data,
                'metadata': {
                    'domain': source_data.get('domain', ''),
                    'title': source_data.get('title', ''),
                    'size': len(json.dumps(source_data))
                }
            }
            
            # Write to cache file
            with open(source_file, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, indent=2)
            
            # Update metadata
            self.metadata['total_sources'] += 1
            
            domain = source_data.get('domain', 'unknown')
            if domain not in self.metadata['domains']:
                self.metadata['domains'][domain] = 0
            self.metadata['domains'][domain] += 1
            
            return True
            
        except (IOError, json.JSONEncodeError) as e:
            print(f"Warning: Could not cache source data: {e}")
            return False
    
    def get_source(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve source data from cache
        
        Args:
            url: Source URL
        
        Returns:
            Cached source data or None if not found/invalid
        """
        source_key = self._generate_source_key(url)
        source_file = self._get_source_file_path(source_key)
        
        if not os.path.exists(source_file):
            return None
        
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                cache_entry = json.load(f)
            
            # Check if cache is still valid
            cached_at = datetime.fromisoformat(cache_entry['cached_at'])
            if datetime.now() - cached_at > timedelta(seconds=self.source_ttl):
                # Remove expired cache
                os.remove(source_file)
                self.metadata['total_sources'] = max(0, self.metadata['total_sources'] - 1)
                return None
            
            return cache_entry['source_data']
            
        except (IOError, json.JSONDecodeError, ValueError):
            return None
    
    def search_sources_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """
        Search cached sources by domain
        
        Args:
            domain: Domain to search for
        
        Returns:
            List of cached sources from the domain
        """
        sources = []
        
        # Scan all source cache files
        for filename in os.listdir(self.cache_directory):
            if filename.endswith('.json') and filename != 'source_metadata.json':
                source_file = os.path.join(self.cache_directory, filename)
                
                try:
                    with open(source_file, 'r', encoding='utf-8') as f:
                        cache_entry = json.load(f)
                    
                    source_data = cache_entry.get('source_data', {})
                    if source_data.get('domain', '').lower() == domain.lower():
                        sources.append(source_data)
                
                except (IOError, json.JSONDecodeError):
                    continue
        
        return sources
    
    def search_sources_by_content(self, query: str) -> List[Dict[str, Any]]:
        """
        Search cached sources by content
        
        Args:
            query: Search query
        
        Returns:
            List of matching cached sources
        """
        results = []
        query_lower = query.lower()
        
        # Scan all source cache files
        for filename in os.listdir(self.cache_directory):
            if filename.endswith('.json') and filename != 'source_metadata.json':
                source_file = os.path.join(self.cache_directory, filename)
                
                try:
                    with open(source_file, 'r', encoding='utf-8') as f:
                        cache_entry = json.load(f)
                    
                    source_data = cache_entry.get('source_data', {})
                    
                    # Search in title and content
                    searchable_text = []
                    if source_data.get('title'):
                        searchable_text.append(source_data['title'].lower())
                    if source_data.get('content'):
                        searchable_text.append(source_data['content'].lower())
                    
                    combined_text = ' '.join(searchable_text)
                    if query_lower in combined_text:
                        results.append({
                            'source_data': source_data,
                            'match_score': self._calculate_match_score(query_lower, combined_text),
                            'cached_at': cache_entry['cached_at']
                        })
                
                except (IOError, json.JSONDecodeError):
                    continue
        
        # Sort by match score
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        return results[:20]  # Limit to top 20 results
    
    def _calculate_match_score(self, query: str, text: str) -> float:
        """Calculate match score for search results"""
        if not query or not text:
            return 0.0
        
        query_words = set(query.split())
        text_words = set(text.split())
        
        if not query_words:
            return 0.0
        
        overlap = len(query_words.intersection(text_words))
        return overlap / len(query_words)
    
    def get_domain_stats(self) -> Dict[str, Any]:
        """Get statistics by domain"""
        return {
            'domains': self.metadata['domains'],
            'total_domains': len(self.metadata['domains']),
            'most_common_domains': sorted(
                self.metadata['domains'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    def cleanup_expired_sources(self) -> Dict[str, int]:
        """Clean up expired source cache entries"""
        cleanup_stats = {
            'expired_removed': 0,
            'total_removed': 0,
            'remaining_sources': 0
        }
        
        try:
            current_time = datetime.now()
            
            for filename in os.listdir(self.cache_directory):
                if filename.endswith('.json') and filename != 'source_metadata.json':
                    source_file = os.path.join(self.cache_directory, filename)
                    
                    try:
                        with open(source_file, 'r', encoding='utf-8') as f:
                            cache_entry = json.load(f)
                        
                        cached_at = datetime.fromisoformat(cache_entry['cached_at'])
                        if current_time - cached_at > timedelta(seconds=self.source_ttl):
                            os.remove(source_file)
                            cleanup_stats['expired_removed'] += 1
                        
                    except (IOError, json.JSONDecodeError, ValueError):
                        # Remove corrupted files
                        os.remove(source_file)
                        cleanup_stats['expired_removed'] += 1
            
            cleanup_stats['total_removed'] = cleanup_stats['expired_removed']
            
            # Update metadata
            self.metadata['total_sources'] = max(0, self.metadata['total_sources'] - cleanup_stats['total_removed'])
            self.metadata['last_cleanup'] = datetime.now().isoformat()
            self._save_metadata()
            
            # Count remaining sources
            remaining_files = [f for f in os.listdir(self.cache_directory) 
                             if f.endswith('.json') and f != 'source_metadata.json']
            cleanup_stats['remaining_sources'] = len(remaining_files)
            
        except Exception as e:
            print(f"Error during source cache cleanup: {e}")
        
        return cleanup_stats
    
    def clear_cache(self) -> bool:
        """Clear all cached source data"""
        try:
            # Remove all source cache files except metadata
            for filename in os.listdir(self.cache_directory):
                if filename.endswith('.json') and filename != 'source_metadata.json':
                    source_file = os.path.join(self.cache_directory, filename)
                    os.remove(source_file)
            
            # Reset metadata
            self.metadata['total_sources'] = 0
            self.metadata['domains'] = {}
            self._save_metadata()
            
            return True
            
        except IOError as e:
            print(f"Error clearing source cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get source cache statistics"""
        total_files = 0
        total_size = 0
        
        # Count files and calculate size
        for filename in os.listdir(self.cache_directory):
            if filename.endswith('.json') and filename != 'source_metadata.json':
                source_file = os.path.join(self.cache_directory, filename)
                if os.path.exists(source_file):
                    total_files += 1
                    total_size += os.path.getsize(source_file)
        
        return {
            'total_sources': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'total_domains': len(self.metadata['domains']),
            'source_ttl_hours': self.source_ttl / 3600,
            'created_at': self.metadata['created_at'],
            'last_cleanup': self.metadata['last_cleanup']
        }
