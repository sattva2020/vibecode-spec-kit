use axum::{
    extract::State,
    http::{StatusCode, Method},
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
// use serde::{Deserialize, Serialize}; // Unused imports
use std::collections::HashMap;
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::time::timeout;
use tracing::{info, error};
use tower_http::cors::{CorsLayer, Any};

mod config;
mod memory_bank;
mod rag;
mod cache;
mod error;
mod types;

use types::*;
use crate::config::Config;
use crate::memory_bank::MemoryBankClient;
use crate::rag::RAGService;
use crate::cache::CacheManager;

#[derive(Clone)]
pub struct AppState {
    pub config: Config,
    pub memory_bank: Arc<MemoryBankClient>,
    pub rag_service: Arc<RAGService>,
    pub cache: Arc<CacheManager>,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    info!("Starting RAG Proxy...");

    // Load configuration
    let config = Config::from_env()?;

    // Initialize services
    let memory_bank = Arc::new(MemoryBankClient::new("memory-bank")?);
    let rag_service = Arc::new(RAGService::new(&config).await?);
    let cache = Arc::new(CacheManager::new(1000));

    let app_state = AppState {
        config,
        memory_bank,
        rag_service,
        cache,
    };

    // Build router
    let app = Router::new()
        .route("/health", get(health_check))
        .route("/api/suggest", post(suggest_code))
        .route("/api/search", post(search_context))
        .route("/api/learn", post(learn_from_code))
        .route("/api/explain", post(explain_code))
        .with_state(app_state)
        .layer(
            CorsLayer::new()
                .allow_methods([Method::GET, Method::POST])
                .allow_headers(Any)
                .allow_origin(Any),
        );

    // Start server
    let addr = format!("{}:{}", "0.0.0.0", "8000");
    info!("RAG Proxy listening on {}", addr);
    
    let listener = tokio::net::TcpListener::bind(&addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

async fn health_check(State(state): State<AppState>) -> impl IntoResponse {
    let start_time = Instant::now();
    
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
            services.insert("memory_bank".to_string(), ServiceStatus {
                status: format!("unhealthy: {}", e),
                response_time_ms: Some(start_time.elapsed().as_millis() as u64),
                last_check: timestamp.clone(),
            });
        }
    }

    // Check RAG service
    match state.rag_service.health_check().await {
        Ok(_rag_health) => {
            services.insert("rag_service".to_string(), ServiceStatus {
                status: "healthy".to_string(),
                response_time_ms: Some(start_time.elapsed().as_millis() as u64),
                last_check: timestamp.clone(),
            });
        }
        Err(e) => {
            services.insert("rag_service".to_string(), ServiceStatus {
                status: format!("unhealthy: {}", e),
                response_time_ms: Some(start_time.elapsed().as_millis() as u64),
                last_check: timestamp.clone(),
            });
        }
    }

    let overall_status = if services.values().all(|s| s.status == "healthy") {
        "healthy"
    } else {
        "degraded"
    };

    Json(HealthResponse {
        status: overall_status.to_string(),
        services,
        timestamp,
        uptime_seconds: 0, // TODO: Implement actual uptime tracking
    })
}

async fn suggest_code(
    State(state): State<AppState>,
    Json(request): Json<CodeContextRequest>,
) -> Result<Json<SuggestionResponse>, StatusCode> {
    let start_time = Instant::now();
    
    // Check cache first
    let cache_key = format!("suggest:{}:{}", request.file_path, request.code.len());
    if let Some(cached_response) = state.cache.get(&cache_key).await {
        let suggestions: Vec<CodeSuggestion> = serde_json::from_str(&cached_response).unwrap_or_default();
        return Ok(Json(SuggestionResponse {
            suggestions,
            context: request.code.clone(),
            memory_bank_context: None,
            cached: true,
            processing_time_ms: start_time.elapsed().as_millis() as u64,
        }));
    }

    // Get suggestions from RAG service
    let suggestions = match timeout(
        Duration::from_secs(10),
        state.rag_service.suggest_code(&request, &None)
    ).await {
        Ok(Ok(suggestions)) => suggestions,
        Ok(Err(e)) => {
            error!("RAG service error: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
        Err(_) => {
            error!("Request timeout");
            return Err(StatusCode::REQUEST_TIMEOUT);
        }
    };

    // Cache the result
    state.cache.set(&cache_key, serde_json::to_string(&suggestions).unwrap_or_default(), Duration::from_secs(3600)).await;

    Ok(Json(SuggestionResponse {
        suggestions,
        context: request.code,
        memory_bank_context: None,
        cached: false,
        processing_time_ms: start_time.elapsed().as_millis() as u64,
    }))
}

async fn search_context(
    State(state): State<AppState>,
    Json(request): Json<SearchRequest>,
) -> Result<Json<SearchResponse>, StatusCode> {
    let _start_time = Instant::now();

    // Check cache first
    let cache_key = format!("search:{}", request.query);
    if let Some(cached_response) = state.cache.get(&cache_key).await {
        let response: SearchResponse = serde_json::from_str(&cached_response).unwrap_or_default();
        return Ok(Json(response));
    }

    // Perform search
    let results = match timeout(
        Duration::from_secs(15),
        state.rag_service.search_context(&request.query, &request.spec_kit_context, request.limit.unwrap_or(10))
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

    let total = results.len();
    let response = SearchResponse {
        results,
        total,
        query: request.query,
        spec_kit_enriched: request.spec_kit_context.is_some(),
    };

    // Cache the result
    state.cache.set(&cache_key, serde_json::to_string(&response).unwrap_or_default(), Duration::from_secs(1800)).await;

    Ok(Json(response))
}

async fn learn_from_code(
    State(state): State<AppState>,
    Json(request): Json<LearnRequest>,
) -> Result<Json<LearnResponse>, StatusCode> {
    let start_time = Instant::now();

    // Learn from code using RAG service
    match timeout(
        Duration::from_secs(20),
        state.rag_service.learn_from_code(&request)
    ).await {
        Ok(Ok(_)) => {
            info!("Successfully learned from code: {}", request.file_path);
            Ok(Json(LearnResponse {
                message: "Code learned successfully".to_string(),
                status: "success".to_string(),
                processing_time_ms: start_time.elapsed().as_millis() as u64,
            }))
        }
        Ok(Err(e)) => {
            error!("Learn error: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
        Err(_) => {
            error!("Learn timeout");
            Err(StatusCode::REQUEST_TIMEOUT)
        }
    }
}

async fn explain_code(
    State(state): State<AppState>,
    Json(request): Json<CodeContextRequest>,
) -> Result<Json<ExplanationResponse>, StatusCode> {
    let start_time = Instant::now();

    // Explain code using RAG service
    let explanation = match timeout(
        Duration::from_secs(20),
        state.rag_service.explain_code(&request, &None)
    ).await {
        Ok(Ok(explanation)) => explanation,
        Ok(Err(e)) => {
            error!("Code explanation error: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
        Err(_) => {
            error!("Explanation timeout");
            return Err(StatusCode::REQUEST_TIMEOUT);
        }
    };

    Ok(Json(ExplanationResponse {
        explanation: explanation.get("explanation").unwrap_or(&"No explanation available".to_string()).clone(),
        methodology: Some("General Development".to_string()),
        spec_kit_integration: Some("basic".to_string()),
        processing_time_ms: start_time.elapsed().as_millis() as u64,
    }))
}
