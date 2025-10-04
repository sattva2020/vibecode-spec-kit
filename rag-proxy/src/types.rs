use serde::{Deserialize, Serialize};
use std::collections::HashMap;

// Request types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CodeContextRequest {
    pub file_path: String,
    pub code: String,
    pub language: String,
    pub project_context: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LearnRequest {
    pub file_path: String,
    pub code: String,
    pub language: String,
    pub context: Option<HashMap<String, String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchRequest {
    pub query: String,
    pub spec_kit_context: Option<String>,
    pub limit: Option<usize>,
}

// Response types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CodeSuggestion {
    pub text: String,
    pub confidence: f64,
    pub r#type: String,
    pub source: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub content: String,
    pub relevance: f64,
    pub source: String,
    pub metadata: HashMap<String, String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct SearchResponse {
    pub results: Vec<SearchResult>,
    pub total: usize,
    pub query: String,
    pub spec_kit_enriched: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SuggestionResponse {
    pub suggestions: Vec<CodeSuggestion>,
    pub context: String,
    pub memory_bank_context: Option<String>,
    pub cached: bool,
    pub processing_time_ms: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LearnResponse {
    pub message: String,
    pub status: String,
    pub processing_time_ms: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExplanationResponse {
    pub explanation: String,
    pub methodology: Option<String>,
    pub spec_kit_integration: Option<String>,
    pub processing_time_ms: u64,
}

// Health check types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServiceStatus {
    pub status: String,
    pub response_time_ms: Option<u64>,
    pub last_check: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HealthResponse {
    pub status: String,
    pub services: HashMap<String, ServiceStatus>,
    pub timestamp: String,
    pub uptime_seconds: u64,
}
