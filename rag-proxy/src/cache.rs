use dashmap::DashMap;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use std::time::{Duration, Instant};

#[derive(Debug, Clone)]
pub struct CacheEntry<T> {
    pub value: T,
    pub expires_at: Instant,
    pub created_at: Instant,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CacheStats {
    pub size: usize,
    pub hits: u64,
    pub misses: u64,
    pub evictions: u64,
    pub memory_usage_bytes: usize,
}

pub struct CacheManager {
    cache: Arc<DashMap<String, CacheEntry<String>>>,
    max_size: usize,
    stats: Arc<dashmap::DashMap<String, u64>>,
}

impl CacheManager {
    pub fn new(max_size: usize) -> Self {
        let cache = Arc::new(DashMap::new());
        let stats = Arc::new(dashmap::DashMap::new());
        
        // Initialize stats
        stats.insert("hits".to_string(), 0);
        stats.insert("misses".to_string(), 0);
        stats.insert("evictions".to_string(), 0);
        
        let manager = Self {
            cache,
            max_size,
            stats,
        };
        
        // Start cleanup task
        manager.start_cleanup_task();
        
        manager
    }

    pub async fn get(&self, key: &str) -> Option<String> {
        match self.cache.get(key) {
            Some(entry) => {
                if entry.expires_at > Instant::now() {
                    // Cache hit
                    self.stats.entry("hits".to_string()).and_modify(|v| *v += 1);
                    Some(entry.value.clone())
                } else {
                    // Expired entry
                    self.cache.remove(key);
                    self.stats.entry("misses".to_string()).and_modify(|v| *v += 1);
                    None
                }
            }
            None => {
                // Cache miss
                self.stats.entry("misses".to_string()).and_modify(|v| *v += 1);
                None
            }
        }
    }

    pub async fn set(&self, key: &str, value: String, ttl: Duration) -> Result<(), CacheError> {
        // Check if we need to evict entries
        if self.cache.len() >= self.max_size {
            self.evict_oldest_entries().await;
        }

        let entry = CacheEntry {
            value,
            expires_at: Instant::now() + ttl,
            created_at: Instant::now(),
        };

        self.cache.insert(key.to_string(), entry);
        Ok(())
    }

    pub async fn remove(&self, key: &str) -> bool {
        self.cache.remove(key).is_some()
    }

    pub async fn clear(&self) {
        self.cache.clear();
        self.stats.insert("hits".to_string(), 0);
        self.stats.insert("misses".to_string(), 0);
        self.stats.insert("evictions".to_string(), 0);
    }

    pub async fn get_stats(&self) -> CacheStats {
        let size = self.cache.len();
        let hits = self.stats.get("hits").map(|v| *v).unwrap_or(0);
        let misses = self.stats.get("misses").map(|v| *v).unwrap_or(0);
        let evictions = self.stats.get("evictions").map(|v| *v).unwrap_or(0);
        
        // Estimate memory usage (rough calculation)
        let memory_usage_bytes = self.cache.iter()
            .map(|entry| entry.key().len() + entry.value().value.len())
            .sum();

        CacheStats {
            size,
            hits,
            misses,
            evictions,
            memory_usage_bytes,
        }
    }

    pub async fn get_ttl(&self, key: &str) -> Option<Duration> {
        self.cache.get(key).map(|entry| {
            if entry.expires_at > Instant::now() {
                entry.expires_at - Instant::now()
            } else {
                Duration::ZERO
            }
        })
    }

    pub async fn extend_ttl(&self, key: &str, additional_ttl: Duration) -> bool {
        if let Some(mut entry) = self.cache.get_mut(key) {
            if entry.expires_at > Instant::now() {
                entry.expires_at += additional_ttl;
                return true;
            }
        }
        false
    }

    async fn evict_oldest_entries(&self) {
        // Simple LRU-like eviction: remove entries that are close to expiration
        let now = Instant::now();
        let mut to_remove = Vec::new();
        
        // Find entries that are expired or close to expiration
        for entry in self.cache.iter() {
            if entry.expires_at <= now {
                to_remove.push(entry.key().clone());
            }
        }
        
        // Remove expired entries
        for key in to_remove {
            if self.cache.remove(&key).is_some() {
                self.stats.entry("evictions".to_string()).and_modify(|v| *v += 1);
            }
        }
        
        // If still at capacity, remove oldest entries
        if self.cache.len() >= self.max_size {
            let mut entries: Vec<_> = self.cache.iter()
                .map(|entry| (entry.key().clone(), entry.created_at))
                .collect();
            
            entries.sort_by(|a, b| a.1.cmp(&b.1));
            
            let to_remove_count = (self.max_size as f64 * 0.1) as usize; // Remove 10%
            for (key, _) in entries.iter().take(to_remove_count) {
                if self.cache.remove(key).is_some() {
                    self.stats.entry("evictions".to_string()).and_modify(|v| *v += 1);
                }
            }
        }
    }

    fn start_cleanup_task(&self) {
        let cache = self.cache.clone();
        let stats = self.stats.clone();
        
        tokio::spawn(async move {
            let mut interval = tokio::time::interval(Duration::from_secs(300)); // Every 5 minutes
            
            loop {
                interval.tick().await;
                
                // Clean up expired entries
                let now = Instant::now();
                let mut expired_keys = Vec::new();
                
                for entry in cache.iter() {
                    if entry.expires_at <= now {
                        expired_keys.push(entry.key().clone());
                    }
                }
                
                for key in expired_keys {
                    if cache.remove(&key).is_some() {
                        stats.entry("evictions".to_string()).and_modify(|v| *v += 1);
                    }
                }
            }
        });
    }

    pub async fn warm_up(&self, entries: Vec<(String, String, Duration)>) -> Result<(), CacheError> {
        for (key, value, ttl) in entries {
            self.set(&key, value, ttl).await?;
        }
        Ok(())
    }

    pub async fn get_keys(&self) -> Vec<String> {
        self.cache.iter()
            .map(|entry| entry.key().clone())
            .collect()
    }

    pub async fn contains(&self, key: &str) -> bool {
        self.cache.contains_key(key)
    }

    pub async fn size(&self) -> usize {
        self.cache.len()
    }

    pub async fn capacity(&self) -> usize {
        self.max_size
    }

    pub async fn is_full(&self) -> bool {
        self.cache.len() >= self.max_size
    }

    pub async fn hit_rate(&self) -> f64 {
        let hits = self.stats.get("hits").map(|v| *v).unwrap_or(0);
        let misses = self.stats.get("misses").map(|v| *v).unwrap_or(0);
        
        if hits + misses == 0 {
            0.0
        } else {
            hits as f64 / (hits + misses) as f64
        }
    }
}

#[derive(Debug, thiserror::Error)]
pub enum CacheError {
    #[error("Cache is full and cannot accept new entries")]
    CacheFull,
    #[error("Invalid TTL: {0}")]
    InvalidTTL(String),
    #[error("Serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),
}

#[cfg(test)]
mod tests {
    use super::*;
    use tokio::time::sleep;

    #[tokio::test]
    async fn test_cache_basic_operations() {
        let cache = CacheManager::new(100);
        
        // Test set and get
        cache.set("key1", "value1".to_string(), Duration::from_secs(60)).await.unwrap();
        assert_eq!(cache.get("key1").await, Some("value1".to_string()));
        
        // Test miss
        assert_eq!(cache.get("key2").await, None);
        
        // Test removal
        assert!(cache.remove("key1").await);
        assert_eq!(cache.get("key1").await, None);
    }

    #[tokio::test]
    async fn test_cache_expiration() {
        let cache = CacheManager::new(100);
        
        // Set with short TTL
        cache.set("key1", "value1".to_string(), Duration::from_millis(100)).await.unwrap();
        
        // Should be available immediately
        assert_eq!(cache.get("key1").await, Some("value1".to_string()));
        
        // Wait for expiration
        sleep(Duration::from_millis(150)).await;
        
        // Should be expired
        assert_eq!(cache.get("key1").await, None);
    }

    #[tokio::test]
    async fn test_cache_stats() {
        let cache = CacheManager::new(100);
        
        // Initial stats
        let stats = cache.get_stats().await;
        assert_eq!(stats.hits, 0);
        assert_eq!(stats.misses, 0);
        
        // Cache miss
        cache.get("nonexistent").await;
        
        // Cache hit
        cache.set("key1", "value1".to_string(), Duration::from_secs(60)).await.unwrap();
        cache.get("key1").await;
        
        let stats = cache.get_stats().await;
        assert_eq!(stats.hits, 1);
        assert_eq!(stats.misses, 1);
    }
}
