"""
Validation cache for storing validation results and assessments
"""

import os
import json
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class ValidationCache:
    """Cache system for validation results"""
    
    def __init__(self, cache_directory: str = "memory-bank/.validation_cache"):
        self.cache_directory = cache_directory
        self.validation_ttl = 3600  # 1 hour in seconds (validation results change more frequently)
        self.max_cache_entries = 500
        
        # Ensure cache directory exists
        os.makedirs(self.cache_directory, exist_ok=True)
        
        # Validation metadata
        self.metadata_file = os.path.join(self.cache_directory, "validation_metadata.json")
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load validation cache metadata"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return {
            'created_at': datetime.now().isoformat(),
            'total_validations': 0,
            'validation_types': {},
            'last_cleanup': datetime.now().isoformat()
        }
    
    def _save_metadata(self):
        """Save validation cache metadata"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save validation metadata: {e}")
    
    def _generate_validation_key(self, validation_type: str, data_hash: str) -> str:
        """Generate cache key for validation"""
        key_string = f"{validation_type}_{data_hash}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_validation_file_path(self, validation_key: str) -> str:
        """Get file path for validation cache entry"""
        return os.path.join(self.cache_directory, f"{validation_key}.json")
    
    def _calculate_data_hash(self, data: Any) -> str:
        """Calculate hash of data for cache key"""
        if isinstance(data, dict):
            # Sort keys for consistent hashing
            sorted_data = json.dumps(data, sort_keys=True)
        else:
            sorted_data = json.dumps(data)
        
        return hashlib.md5(sorted_data.encode()).hexdigest()
    
    def store_validation(self, 
                        validation_type: str,
                        data: Any,
                        validation_result: Dict[str, Any]) -> bool:
        """
        Store validation result in cache
        
        Args:
            validation_type: Type of validation (e.g., 'source', 'research', 'content')
            data: Data that was validated
            validation_result: Validation result to cache
        
        Returns:
            True if successfully cached, False otherwise
        """
        try:
            data_hash = self._calculate_data_hash(data)
            validation_key = self._generate_validation_key(validation_type, data_hash)
            validation_file = self._get_validation_file_path(validation_key)
            
            # Prepare cache entry
            cache_entry = {
                'validation_key': validation_key,
                'validation_type': validation_type,
                'data_hash': data_hash,
                'cached_at': datetime.now().isoformat(),
                'validation_result': validation_result,
                'metadata': {
                    'score': validation_result.get('overall_score', 0.0),
                    'is_valid': validation_result.get('is_valid', False),
                    'errors_count': len(validation_result.get('errors', [])),
                    'warnings_count': len(validation_result.get('warnings', []))
                }
            }
            
            # Write to cache file
            with open(validation_file, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, indent=2)
            
            # Update metadata
            self.metadata['total_validations'] += 1
            
            if validation_type not in self.metadata['validation_types']:
                self.metadata['validation_types'][validation_type] = 0
            self.metadata['validation_types'][validation_type] += 1
            
            # Check if cleanup is needed
            if self.metadata['total_validations'] > self.max_cache_entries:
                self._cleanup_cache()
            
            return True
            
        except (IOError, json.JSONEncodeError) as e:
            print(f"Warning: Could not cache validation result: {e}")
            return False
    
    def get_validation(self, validation_type: str, data: Any) -> Optional[Dict[str, Any]]:
        """
        Retrieve validation result from cache
        
        Args:
            validation_type: Type of validation
            data: Data that was validated
        
        Returns:
            Cached validation result or None if not found/invalid
        """
        data_hash = self._calculate_data_hash(data)
        validation_key = self._generate_validation_key(validation_type, data_hash)
        validation_file = self._get_validation_file_path(validation_key)
        
        if not os.path.exists(validation_file):
            return None
        
        try:
            with open(validation_file, 'r', encoding='utf-8') as f:
                cache_entry = json.load(f)
            
            # Check if cache is still valid
            cached_at = datetime.fromisoformat(cache_entry['cached_at'])
            if datetime.now() - cached_at > timedelta(seconds=self.validation_ttl):
                # Remove expired cache
                os.remove(validation_file)
                self.metadata['total_validations'] = max(0, self.metadata['total_validations'] - 1)
                return None
            
            return cache_entry['validation_result']
            
        except (IOError, json.JSONDecodeError, ValueError):
            return None
    
    def search_validations_by_type(self, validation_type: str) -> List[Dict[str, Any]]:
        """
        Search cached validations by type
        
        Args:
            validation_type: Type of validation to search for
        
        Returns:
            List of cached validations of the specified type
        """
        validations = []
        
        # Scan all validation cache files
        for filename in os.listdir(self.cache_directory):
            if filename.endswith('.json') and filename != 'validation_metadata.json':
                validation_file = os.path.join(self.cache_directory, filename)
                
                try:
                    with open(validation_file, 'r', encoding='utf-8') as f:
                        cache_entry = json.load(f)
                    
                    if cache_entry.get('validation_type') == validation_type:
                        validations.append({
                            'validation_result': cache_entry['validation_result'],
                            'cached_at': cache_entry['cached_at'],
                            'score': cache_entry['metadata']['score']
                        })
                
                except (IOError, json.JSONDecodeError):
                    continue
        
        # Sort by score (highest first)
        validations.sort(key=lambda x: x['score'], reverse=True)
        
        return validations
    
    def search_validations_by_score(self, 
                                   min_score: float = 0.0,
                                   max_score: float = 1.0) -> List[Dict[str, Any]]:
        """
        Search cached validations by score range
        
        Args:
            min_score: Minimum score threshold
            max_score: Maximum score threshold
        
        Returns:
            List of cached validations within score range
        """
        validations = []
        
        # Scan all validation cache files
        for filename in os.listdir(self.cache_directory):
            if filename.endswith('.json') and filename != 'validation_metadata.json':
                validation_file = os.path.join(self.cache_directory, filename)
                
                try:
                    with open(validation_file, 'r', encoding='utf-8') as f:
                        cache_entry = json.load(f)
                    
                    score = cache_entry['metadata']['score']
                    if min_score <= score <= max_score:
                        validations.append({
                            'validation_result': cache_entry['validation_result'],
                            'validation_type': cache_entry['validation_type'],
                            'cached_at': cache_entry['cached_at'],
                            'score': score
                        })
                
                except (IOError, json.JSONDecodeError):
                    continue
        
        # Sort by score (highest first)
        validations.sort(key=lambda x: x['score'], reverse=True)
        
        return validations
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation cache statistics"""
        stats = {
            'total_validations': self.metadata['total_validations'],
            'validation_types': self.metadata['validation_types'],
            'validation_ttl_hours': self.validation_ttl / 3600,
            'max_cache_entries': self.max_cache_entries,
            'created_at': self.metadata['created_at'],
            'last_cleanup': self.metadata['last_cleanup']
        }
        
        # Calculate additional statistics
        total_files = 0
        total_size = 0
        
        for filename in os.listdir(self.cache_directory):
            if filename.endswith('.json') and filename != 'validation_metadata.json':
                validation_file = os.path.join(self.cache_directory, filename)
                if os.path.exists(validation_file):
                    total_files += 1
                    total_size += os.path.getsize(validation_file)
        
        stats['cached_files'] = total_files
        stats['total_size_bytes'] = total_size
        stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        
        return stats
    
    def _cleanup_cache(self):
        """Internal cache cleanup"""
        self.cleanup_expired_validations()
    
    def cleanup_expired_validations(self) -> Dict[str, int]:
        """Clean up expired validation cache entries"""
        cleanup_stats = {
            'expired_removed': 0,
            'total_removed': 0,
            'remaining_validations': 0
        }
        
        try:
            current_time = datetime.now()
            
            for filename in os.listdir(self.cache_directory):
                if filename.endswith('.json') and filename != 'validation_metadata.json':
                    validation_file = os.path.join(self.cache_directory, filename)
                    
                    try:
                        with open(validation_file, 'r', encoding='utf-8') as f:
                            cache_entry = json.load(f)
                        
                        cached_at = datetime.fromisoformat(cache_entry['cached_at'])
                        if current_time - cached_at > timedelta(seconds=self.validation_ttl):
                            os.remove(validation_file)
                            cleanup_stats['expired_removed'] += 1
                        
                    except (IOError, json.JSONDecodeError, ValueError):
                        # Remove corrupted files
                        os.remove(validation_file)
                        cleanup_stats['expired_removed'] += 1
            
            cleanup_stats['total_removed'] = cleanup_stats['expired_removed']
            
            # Update metadata
            self.metadata['total_validations'] = max(0, self.metadata['total_validations'] - cleanup_stats['total_removed'])
            self.metadata['last_cleanup'] = datetime.now().isoformat()
            self._save_metadata()
            
            # Count remaining validations
            remaining_files = [f for f in os.listdir(self.cache_directory) 
                             if f.endswith('.json') and f != 'validation_metadata.json']
            cleanup_stats['remaining_validations'] = len(remaining_files)
            
        except Exception as e:
            print(f"Error during validation cache cleanup: {e}")
        
        return cleanup_stats
    
    def clear_cache(self) -> bool:
        """Clear all cached validation data"""
        try:
            # Remove all validation cache files except metadata
            for filename in os.listdir(self.cache_directory):
                if filename.endswith('.json') and filename != 'validation_metadata.json':
                    validation_file = os.path.join(self.cache_directory, filename)
                    os.remove(validation_file)
            
            # Reset metadata
            self.metadata['total_validations'] = 0
            self.metadata['validation_types'] = {}
            self._save_metadata()
            
            return True
            
        except IOError as e:
            print(f"Error clearing validation cache: {e}")
            return False
    
    def invalidate_validation(self, validation_type: str, data: Any) -> bool:
        """Invalidate specific validation cache entry"""
        data_hash = self._calculate_data_hash(data)
        validation_key = self._generate_validation_key(validation_type, data_hash)
        validation_file = self._get_validation_file_path(validation_key)
        
        if os.path.exists(validation_file):
            try:
                os.remove(validation_file)
                self.metadata['total_validations'] = max(0, self.metadata['total_validations'] - 1)
                return True
            except IOError:
                return False
        
        return False
