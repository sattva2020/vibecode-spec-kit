use serde::{Deserialize, Serialize};
use std::env;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub server: ServerConfig,
    pub rag: RAGConfig,
    pub memory_bank: MemoryBankConfig,
    pub cache: CacheConfig,
    pub lightrag: LightRAGConfig,
    pub n8n: N8nConfig,
    pub supabase: SupabaseConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
    pub workers: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RAGConfig {
    pub max_suggestions: usize,
    pub timeout_seconds: u64,
    pub enable_caching: bool,
    pub cache_ttl_seconds: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryBankConfig {
    pub path: String,
    pub auto_sync: bool,
    pub sync_interval_seconds: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CacheConfig {
    pub max_size: usize,
    pub default_ttl_seconds: u64,
    pub enable_metrics: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LightRAGConfig {
    pub url: String,
    pub timeout_seconds: u64,
    pub retry_attempts: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct N8nConfig {
    pub url: String,
    pub username: String,
    pub password: String,
    pub timeout_seconds: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SupabaseConfig {
    pub url: String,
    pub anon_key: String,
    pub service_key: String,
    pub timeout_seconds: u64,
}

impl Config {
    pub fn from_env() -> anyhow::Result<Self> {
        dotenvy::dotenv().ok();

        let config = Config {
            server: ServerConfig {
                host: env::var("HOST").unwrap_or_else(|_| "0.0.0.0".to_string()),
                port: env::var("PORT")
                    .unwrap_or_else(|_| "8000".to_string())
                    .parse()
                    .unwrap_or(8000),
                workers: env::var("WORKERS")
                    .unwrap_or_else(|_| "4".to_string())
                    .parse()
                    .unwrap_or(4),
            },
            rag: RAGConfig {
                max_suggestions: env::var("RAG_MAX_SUGGESTIONS")
                    .unwrap_or_else(|_| "10".to_string())
                    .parse()
                    .unwrap_or(10),
                timeout_seconds: env::var("RAG_TIMEOUT_SECONDS")
                    .unwrap_or_else(|_| "30".to_string())
                    .parse()
                    .unwrap_or(30),
                enable_caching: env::var("RAG_ENABLE_CACHING")
                    .unwrap_or_else(|_| "true".to_string())
                    .parse()
                    .unwrap_or(true),
                cache_ttl_seconds: env::var("RAG_CACHE_TTL_SECONDS")
                    .unwrap_or_else(|_| "3600".to_string())
                    .parse()
                    .unwrap_or(3600),
            },
            memory_bank: MemoryBankConfig {
                path: env::var("MEMORY_BANK_PATH")
                    .unwrap_or_else(|_| "./memory-bank".to_string()),
                auto_sync: env::var("MEMORY_BANK_AUTO_SYNC")
                    .unwrap_or_else(|_| "true".to_string())
                    .parse()
                    .unwrap_or(true),
                sync_interval_seconds: env::var("MEMORY_BANK_SYNC_INTERVAL")
                    .unwrap_or_else(|_| "300".to_string())
                    .parse()
                    .unwrap_or(300),
            },
            cache: CacheConfig {
                max_size: env::var("CACHE_MAX_SIZE")
                    .unwrap_or_else(|_| "1000".to_string())
                    .parse()
                    .unwrap_or(1000),
                default_ttl_seconds: env::var("CACHE_DEFAULT_TTL")
                    .unwrap_or_else(|_| "1800".to_string())
                    .parse()
                    .unwrap_or(1800),
                enable_metrics: env::var("CACHE_ENABLE_METRICS")
                    .unwrap_or_else(|_| "true".to_string())
                    .parse()
                    .unwrap_or(true),
            },
            lightrag: LightRAGConfig {
                url: env::var("LIGHTRAG_URL")
                    .unwrap_or_else(|_| "http://localhost:8000".to_string()),
                timeout_seconds: env::var("LIGHTRAG_TIMEOUT_SECONDS")
                    .unwrap_or_else(|_| "30".to_string())
                    .parse()
                    .unwrap_or(30),
                retry_attempts: env::var("LIGHTRAG_RETRY_ATTEMPTS")
                    .unwrap_or_else(|_| "3".to_string())
                    .parse()
                    .unwrap_or(3),
            },
            n8n: N8nConfig {
                url: env::var("N8N_URL")
                    .unwrap_or_else(|_| "http://localhost:5678".to_string()),
                username: env::var("N8N_USER")
                    .unwrap_or_else(|_| "admin".to_string()),
                password: env::var("N8N_PASSWORD")
                    .unwrap_or_else(|_| "admin123".to_string()),
                timeout_seconds: env::var("N8N_TIMEOUT_SECONDS")
                    .unwrap_or_else(|_| "30".to_string())
                    .parse()
                    .unwrap_or(30),
            },
            supabase: SupabaseConfig {
                url: env::var("SUPABASE_URL")
                    .unwrap_or_else(|_| "http://localhost:8000".to_string()),
                anon_key: env::var("SUPABASE_ANON_KEY")
                    .unwrap_or_else(|_| "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0".to_string()),
                service_key: env::var("SUPABASE_SERVICE_KEY")
                    .unwrap_or_else(|_| "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU".to_string()),
                timeout_seconds: env::var("SUPABASE_TIMEOUT_SECONDS")
                    .unwrap_or_else(|_| "30".to_string())
                    .parse()
                    .unwrap_or(30),
            },
        };

        Ok(config)
    }
}
