use axum::{
    extract::State,
    http::{StatusCode, Method},
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::{collections::HashMap, sync::Arc, time::Duration};
use tokio::time::timeout;
use tower_http::cors::{Any, CorsLayer};
use tower_http::trace::TraceLayer;
use tracing::{info, warn, error, Level};
use tracing_subscriber::FmtSubscriber;

use crate::config::Config;
use crate::memory_bank::MemoryBankClient;
use crate::rag::RAGService;
use crate::cache::CacheManager;

mod config;
mod memory_bank;
mod rag;
mod cache;
mod error;
mod types;

use types::*;

#[derive(Clone)]
pub struct AppState {
    pub config: Config,
    pub memory_bank: Arc<MemoryBankClient>,
    pub rag_service: Arc<RAGService>,
    pub cache: Arc<CacheManager>,
}

#[derive(Deserialize, Debug)]
pub struct CodeContextRequest {
    pub file_path: String,
    pub code: String,
    pub language: String,
    pub cursor_position: Option<HashMap<String, i32>>,
    pub project_context: Option<String>,
}

#[derive(Serialize, Debug)]
pub struct SuggestionResponse {
    pub suggestions: Vec<CodeSuggestion>,
    pub context: String,
    pub memory_bank_context: Option<String>,
    pub cached: bool,
    pub processing_time_ms: u64,
}

#[derive(Serialize, Debug, Clone, Deserialize)]
pub struct CodeSuggestion {
    pub text: String,
    pub confidence: f64,
    pub r#type: String,
    pub source: Option<String>,
    pub spec_kit_integration: Option<String>,
    pub methodology: Option<String>,
}

#[derive(Deserialize, Debug)]
pub struct SearchRequest {
    pub query: String,
    pub spec_kit_context: Option<String>,
    pub limit: Option<usize>,
}

#[derive(Serialize, Debug, Clone, Default, Deserialize)]
pub struct SearchResponse {
    pub results: Vec<SearchResult>,
    pub total: usize,
    pub query: String,
    pub spec_kit_enriched: bool,
}

#[derive(Serialize, Debug, Clone)]
pub struct SearchResult {
    pub content: String,
    pub relevance: f64,
    pub source: String,
    pub metadata: HashMap<String, String>,
}

#[derive(Deserialize, Debug)]
pub struct LearnRequest {
    pub file_path: String,
    pub code: String,
    pub language: String,
    pub context: Option<HashMap<String, serde_json::Value>>,
}

#[derive(Serialize, Debug)]
pub struct LearnResponse {
    pub status: String,
    pub message: String,
    pub memory_bank_integration: String,
    pub rag_indexed: bool,
}

#[derive(Serialize, Debug)]
pub struct HealthResponse {
    pub status: String,
    pub timestamp: String,
    pub services: HashMap<String, ServiceStatus>,
    pub memory_bank: MemoryBankStatus,
}

#[derive(Serialize, Debug)]
pub struct ServiceStatus {
    pub status: String,
    pub response_time_ms: Option<u64>,
    pub last_check: String,
}

#[derive(Serialize, Debug)]
pub struct MemoryBankStatus {
    pub initialized: bool,
    pub current_mode: String,
    pub rag_enabled: bool,
    pub issues: Vec<String>,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize tracing
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();
    tracing::subscriber::set_global_default(subscriber)?;

    info!("🚀 Starting RAG Proxy for Vibecode Spec Kit...");

    // Load configuration
    let config = Config::from_env()?;
    info!("Configuration loaded: RAG Proxy on port {}", config.server.port);

    // Initialize services
    let memory_bank = Arc::new(MemoryBankClient::new(&config.memory_bank.path)?);
    let rag_service = Arc::new(RAGService::new(&config).await?);
    let cache = Arc::new(CacheManager::new(config.cache.max_size));

    // Initialize Memory Bank if needed
    if !memory_bank.is_initialized().await? {
        info!("Initializing Memory Bank...");
        memory_bank.initialize().await?;
    }

    let app_state = AppState {
        config,
        memory_bank,
        rag_service,
        cache,
    };

    // Create router
    let app = create_router(app_state);

    // Start server
    let addr = format!("{}:{}", "0.0.0.0", 8000);
    info!("🌐 RAG Proxy listening on {}", addr);

    let listener = tokio::net::TcpListener::bind(&addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

fn create_router(state: AppState) -> Router {
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods([Method::GET, Method::POST, Method::PUT, Method::DELETE])
        .allow_headers(Any);

    Router::new()
        // Health and status endpoints
        .route("/health", get(health_check))
        .route("/status", get(status))
        .route("/memory-bank/status", get(memory_bank_status))
        
        // RAG core endpoints
        .route("/api/suggest", post(suggest_code))
        .route("/api/search", post(search_context))
        .route("/api/learn", post(learn_from_code))
        .route("/api/explain", post(explain_code))
        
        // Spec Kit integration endpoints
        .route("/api/spec-kit/integrate", post(integrate_with_spec_kit))
        .route("/api/spec-kit/context", get(get_spec_kit_context))
        .route("/api/spec-kit/methodologies", get(get_methodologies))
        
        // Memory Bank integration endpoints
        .route("/api/memory-bank/context", get(get_memory_bank_context))
        .route("/api/memory-bank/update", post(update_memory_bank_context))
        
        // Cache management
        .route("/api/cache/stats", get(cache_stats))
        .route("/api/cache/clear", post(clear_cache))
        
        .layer(cors)
        .layer(TraceLayer::new_for_http())
        .with_state(state)
}

async fn health_check(State(state): State<AppState>) -> impl IntoResponse {
    let start_time = std::time::Instant::now();
    
    let mut services = HashMap::new();
    let timestamp = sqlx::types::chrono::Utc::now().to_rfc3339();

    // Check Memory Bank
    match state.memory_bank.health_check().await {
        Ok(_mb_health) => {
            services.insert("memory_bank".to_string(), ServiceStatus {
                status: "healthy".to_string(),
                response_time_ms: Some(start_time.elapsed().as_millis() as u64),
                last_check: timestamp.clone(),
            });
        }
        Err(e) => {
            warn!("Memory Bank health check failed: {}", e);
            services.insert("memory_bank".to_string(), ServiceStatus {
                status: "unhealthy".to_string(),
                response_time_ms: Some(start_time.elapsed().as_millis() as u64),
                last_check: timestamp.clone(),
            });
        }
    }

    // Check RAG services
    match state.rag_service.health_check().await {
        Ok(rag_health) => {
            services.insert("rag_service".to_string(), ServiceStatus {
                status: rag_health.status.clone(),
                response_time_ms: Some(start_time.elapsed().as_millis() as u64),
                last_check: timestamp.clone(),
            });
        }
        Err(e) => {
            warn!("RAG service health check failed: {}", e);
            services.insert("rag_service".to_string(), ServiceStatus {
                status: "unhealthy".to_string(),
                response_time_ms: Some(start_time.elapsed().as_millis() as u64),
                last_check: timestamp.clone(),
            });
        }
    }

    let memory_bank_status = match state.memory_bank.get_status().await {
        Ok(status) => MemoryBankStatus {
            initialized: status.initialized,
            current_mode: status.current_mode,
            rag_enabled: true,
            issues: status.issues,
        },
        Err(_) => MemoryBankStatus {
            initialized: false,
            current_mode: "unknown".to_string(),
            rag_enabled: false,
            issues: vec!["Failed to get status".to_string()],
        },
    };

    Json(HealthResponse {
        status: "healthy".to_string(),
        timestamp,
        services,
        memory_bank: memory_bank_status,
    })
}

async fn suggest_code(
    State(state): State<AppState>,
    Json(request): Json<CodeContextRequest>,
) -> Result<Json<SuggestionResponse>, StatusCode> {
    let start_time = std::time::Instant::now();
    
    // Check cache first
    let cache_key = format!("suggest:{}:{}", request.file_path, request.code.len());
    if let Some(cached_response) = state.cache.get(&cache_key).await {
        return Ok(Json(SuggestionResponse {
            suggestions: serde_json::from_str(&cached_response).unwrap_or_default(),
            context: request.code.clone(),
            memory_bank_context: None,
            cached: true,
            processing_time_ms: start_time.elapsed().as_millis() as u64,
        }));
    }

    // Get Spec Kit context from Memory Bank
    let spec_kit_context = match state.memory_bank.get_rag_context("code suggestion").await {
        Ok(context) => Some(context),
        Err(e) => {
            warn!("Failed to get Spec Kit context: {}", e);
            None
        }
    };

    // Get suggestions from RAG service
    let suggestions = match timeout(
        Duration::from_secs(10),
        state.rag_service.suggest_code(&request, &spec_kit_context.as_ref().unwrap_or(&None))
    ).await {
        Ok(Ok(suggestions)) => suggestions,
        Ok(Err(e)) => {
            error!("RAG service error: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
        Err(_) => {
            error!("RAG service timeout");
            return Err(StatusCode::REQUEST_TIMEOUT);
        }
    };

    // Cache the result
    state.cache.set(&cache_key, suggestions.clone(), Duration::from_secs(3600)).await;

    Ok(Json(SuggestionResponse {
        suggestions,
        context: request.code,
        memory_bank_context: spec_kit_context.as_ref().unwrap_or(&None).clone(),
        cached: false,
        processing_time_ms: start_time.elapsed().as_millis() as u64,
    }))
}

async fn search_context(
    State(state): State<AppState>,
    Json(request): Json<SearchRequest>,
) -> Result<Json<SearchResponse>, StatusCode> {
    let start_time = std::time::Instant::now();

    // Check cache first
    let cache_key = format!("search:{}", request.query);
    if let Some(cached_response) = state.cache.get(&cache_key).await {
        return Ok(Json(serde_json::from_str(&cached_response).unwrap_or_default()));
    }

    // Get Spec Kit context for enhanced search
    let spec_kit_context = if request.spec_kit_context.is_none() {
        match state.memory_bank.get_rag_context(&request.query).await {
            Ok(context) => Some(Some(context)),
            Err(e) => {
                warn!("Failed to get Spec Kit context for search: {}", e);
                Some(None)
            }
        }
    } else {
        Some(Some(request.spec_kit_context))
    };

    // Perform search
    let results = match timeout(
        Duration::from_secs(15),
        state.rag_service.search_context(&request.query, &spec_kit_context.as_ref().unwrap_or(&None), request.limit.unwrap_or(10))
    ).await {
        Ok(Ok(results)) => results,
        Ok(Err(e)) => {
            error!("Search error: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
        Err(_) => {
            error!("Search timeout");
            return Err(StatusCode::REQUEST_TIMEOUT);
        }
    };

    let response = SearchResponse {
        results,
        total: results.len(),
        query: request.query,
        spec_kit_enriched: spec_kit_context.is_some(),
    };

    // Cache the result
    state.cache.set(&cache_key, serde_json::to_string(&response).unwrap_or_default(), Duration::from_secs(1800)).await;

    Ok(Json(response))
}

async fn learn_from_code(
    State(state): State<AppState>,
    Json(request): Json<LearnRequest>,
) -> Result<Json<LearnResponse>, StatusCode> {
    let start_time = std::time::Instant::now();

    // Extract Spec Kit context from request
    let spec_type = request.context
        .as_ref()
        .and_then(|ctx| ctx.get("spec_type"))
        .and_then(|v| v.as_str())
        .unwrap_or("general");

    // Integrate with Memory Bank first
    let memory_bank_integration = match state.memory_bank.integrate_rag_context(spec_type, &request.code).await {
        Ok(result) => result,
        Err(e) => {
            error!("Memory Bank integration failed: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    };

    // Learn from code using RAG service
    let rag_indexed = match timeout(
        Duration::from_secs(30),
        state.rag_service.learn_from_code(&request)
    ).await {
        Ok(Ok(_)) => true,
        Ok(Err(e)) => {
            error!("RAG learning failed: {}", e);
            false
        }
        Err(_) => {
            error!("RAG learning timeout");
            false
        }
    };

    Ok(Json(LearnResponse {
        status: "success".to_string(),
        message: format!("Code learned in {}ms", start_time.elapsed().as_millis()),
        memory_bank_integration,
        rag_indexed,
    }))
}

async fn explain_code(
    State(state): State<AppState>,
    Json(request): Json<CodeContextRequest>,
) -> Result<Json<HashMap<String, String>>, StatusCode> {
    // Get Spec Kit context
    let spec_kit_context = match state.memory_bank.get_rag_context("code explanation").await {
        Ok(context) => Some(context),
        Err(e) => {
            warn!("Failed to get Spec Kit context: {}", e);
            None
        }
    };

    // Explain code using RAG service
    let explanation = match timeout(
        Duration::from_secs(20),
        state.rag_service.explain_code(&request, &spec_kit_context.as_ref().unwrap_or(&None))
    ).await {
        Ok(Ok(explanation)) => explanation,
        Ok(Err(e)) => {
            error!("Code explanation error: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
        Err(_) => {
            error!("Code explanation timeout");
            return Err(StatusCode::REQUEST_TIMEOUT);
        }
    };

    Ok(Json(explanation))
}

async fn integrate_with_spec_kit(
    State(state): State<AppState>,
    Json(request): Json<HashMap<String, serde_json::Value>>,
) -> Result<Json<HashMap<String, String>>, StatusCode> {
    let spec_type = request.get("spec_type")
        .and_then(|v| v.as_str())
        .unwrap_or("unknown");
    
    let code = request.get("code")
        .and_then(|v| v.as_str())
        .unwrap_or("");

    // Integrate with Memory Bank
    match state.memory_bank.integrate_rag_context(spec_type, code).await {
        Ok(result) => {
            let mut response = HashMap::new();
            response.insert("status".to_string(), "success".to_string());
            response.insert("integration".to_string(), result);
            response.insert("spec_type".to_string(), spec_type.to_string());
            response.insert("memory_bank_connected".to_string(), "true".to_string());
            Ok(Json(response))
        }
        Err(e) => {
            error!("Failed to integrate with Spec Kit: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

async fn get_spec_kit_context(State(state): State<AppState>) -> Result<Json<HashMap<String, String>>, StatusCode> {
    match state.memory_bank.get_context().await {
        Ok(context) => Ok(Json(context)),
        Err(e) => {
            error!("Failed to get Spec Kit context: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

async fn get_methodologies(State(_state): State<AppState>) -> Result<Json<HashMap<String, Vec<String>>>, StatusCode> {
    let methodologies = HashMap::from([
        ("level1".to_string(), vec![
            "Quick Bug Fix".to_string(),
            "Simple Enhancement".to_string(),
        ]),
        ("level2".to_string(), vec![
            "Intermediate Feature".to_string(),
            "Component Integration".to_string(),
        ]),
        ("level3".to_string(), vec![
            "Complex System".to_string(),
            "Architecture Change".to_string(),
        ]),
        ("level4".to_string(), vec![
            "Enterprise Solution".to_string(),
            "Platform Migration".to_string(),
        ]),
    ]);
    
    Ok(Json(methodologies))
}

async fn get_memory_bank_context(State(state): State<AppState>) -> Result<Json<HashMap<String, String>>, StatusCode> {
    match state.memory_bank.get_context().await {
        Ok(context) => Ok(Json(context)),
        Err(e) => {
            error!("Failed to get Memory Bank context: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

async fn update_memory_bank_context(
    State(state): State<AppState>,
    Json(context_data): Json<HashMap<String, serde_json::Value>>,
) -> Result<Json<HashMap<String, String>>, StatusCode> {
    match state.memory_bank.update_context(context_data).await {
        Ok(_) => {
            let mut response = HashMap::new();
            response.insert("status".to_string(), "success".to_string());
            response.insert("message".to_string(), "Memory Bank context updated".to_string());
            Ok(Json(response))
        }
        Err(e) => {
            error!("Failed to update Memory Bank context: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

async fn memory_bank_status(State(state): State<AppState>) -> Result<Json<MemoryBankStatus>, StatusCode> {
    match state.memory_bank.get_status().await {
        Ok(status) => Ok(Json(MemoryBankStatus {
            initialized: status.initialized,
            current_mode: status.current_mode,
            rag_enabled: true,
            issues: status.issues,
        })),
        Err(e) => {
            error!("Failed to get Memory Bank status: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

async fn status(State(state): State<AppState>) -> impl IntoResponse {
    let cache_stats = state.cache.get_stats().await;
    let memory_bank_status = state.memory_bank.get_status().await.unwrap_or_default();
    
    let mut status = HashMap::new();
    status.insert("service".to_string(), "rag-proxy".to_string());
    status.insert("version".to_string(), "1.0.0".to_string());
    status.insert("memory_bank_initialized".to_string(), memory_bank_status.initialized.to_string());
    status.insert("memory_bank_mode".to_string(), memory_bank_status.current_mode);
    status.insert("cache_size".to_string(), cache_stats.size.to_string());
    status.insert("cache_hits".to_string(), cache_stats.hits.to_string());
    status.insert("cache_misses".to_string(), cache_stats.misses.to_string());
    
    Json(status)
}

async fn cache_stats(State(state): State<AppState>) -> impl IntoResponse {
    let stats = state.cache.get_stats().await;
    Json(stats)
}

async fn clear_cache(State(state): State<AppState>) -> impl IntoResponse {
    state.cache.clear().await;
    let mut response = HashMap::new();
    response.insert("status".to_string(), "success".to_string());
    response.insert("message".to_string(), "Cache cleared".to_string());
    Json(response)
}
