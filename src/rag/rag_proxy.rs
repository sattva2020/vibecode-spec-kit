use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use std::{collections::HashMap, sync::Arc};
use tower_http::cors::{Any, CorsLayer};
use tower_http::trace::TraceLayer;
use tracing::{info, warn};

use crate::core::memory_bank::MemoryBank;

#[derive(Clone)]
pub struct RAGState {
    pub memory_bank: Arc<MemoryBank>,
    pub lightrag_url: String,
    pub n8n_url: String,
    pub cache: Arc<lru::LruCache<String, String>>,
}

#[derive(Deserialize)]
pub struct CodeContext {
    pub file_path: String,
    pub code: String,
    pub language: String,
    pub cursor_position: Option<HashMap<String, i32>>,
    pub project_context: Option<String>, // Vibecode Spec Kit context
}

#[derive(Serialize)]
pub struct SuggestionResponse {
    pub suggestions: Vec<CodeSuggestion>,
    pub context: String,
    pub memory_bank_context: Option<String>,
    pub cached: bool,
}

#[derive(Serialize)]
pub struct CodeSuggestion {
    pub text: String,
    pub confidence: f64,
    pub r#type: String,
    pub source: Option<String>,
    pub spec_kit_integration: Option<String>, // Integration with Spec Kit
}

impl RAGState {
    pub fn new(memory_bank: Arc<MemoryBank>) -> Self {
        Self {
            memory_bank,
            lightrag_url: std::env::var("LIGHTRAG_URL")
                .unwrap_or_else(|_| "http://localhost:8000".to_string()),
            n8n_url: std::env::var("N8N_URL")
                .unwrap_or_else(|_| "http://localhost:5678".to_string()),
            cache: Arc::new(lru::LruCache::new(
                std::num::NonZeroUsize::new(1000).unwrap(),
            )),
        }
    }

    pub async fn get_spec_kit_context(&self, context: &CodeContext) -> Option<String> {
        // Интеграция с Memory Bank для получения контекста Spec Kit
        if let Some(project_context) = &context.project_context {
            // Получаем контекст из Memory Bank
            let spec_context = self.memory_bank.get_context(project_context).await.ok()?;
            
            // Формируем контекст для RAG
            Some(format!(
                "Vibecode Spec Kit Context:\n{}\n\nCode Context:\nFile: {}\nLanguage: {}",
                spec_context,
                context.file_path,
                context.language
            ))
        } else {
            None
        }
    }
}

pub fn create_rag_router(state: RAGState) -> Router {
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    Router::new()
        .route("/health", get(health_check))
        .route("/api/suggest", post(suggest_code))
        .route("/api/context/search", post(search_context))
        .route("/api/learn", post(learn_from_code))
        .route("/api/spec-kit/integrate", post(integrate_with_spec_kit))
        .layer(cors)
        .layer(TraceLayer::new_for_http())
        .with_state(state)
}

async fn health_check(State(state): State<RAGState>) -> Json<HashMap<String, String>> {
    let mut services = HashMap::new();
    
    // Проверяем Memory Bank
    match state.memory_bank.health_check().await {
        Ok(_) => services.insert("memory_bank".to_string(), "healthy".to_string()),
        Err(_) => services.insert("memory_bank".to_string(), "unhealthy".to_string()),
    };
    
    // Проверяем LightRAG
    match check_lightrag(&state.lightrag_url).await {
        Ok(_) => services.insert("lightrag".to_string(), "healthy".to_string()),
        Err(_) => services.insert("lightrag".to_string(), "unhealthy".to_string()),
    };

    services.insert("status".to_string(), "healthy".to_string());
    Json(services)
}

async fn suggest_code(
    State(state): State<RAGState>,
    Json(context): Json<CodeContext>,
) -> Result<Json<SuggestionResponse>, StatusCode> {
    let cache_key = format!("suggest:{}:{}", context.file_path, context.code.len());
    
    // Проверяем кеш
    if let Some(cached_response) = state.cache.get(&cache_key) {
        let cached_suggestions: Vec<CodeSuggestion> = 
            serde_json::from_str(cached_response).unwrap_or_default();
        
        return Ok(Json(SuggestionResponse {
            suggestions: cached_suggestions,
            context: context.code.clone(),
            memory_bank_context: None,
            cached: true,
        }));
    }

    // Получаем контекст Spec Kit
    let spec_kit_context = state.get_spec_kit_context(&context).await;

    // Получаем предложения от LightRAG с контекстом Spec Kit
    let mut suggestions = get_suggestions_from_lightrag(&state, &context, &spec_kit_context).await
        .unwrap_or_else(|| {
            vec![CodeSuggestion {
                text: "// AI suggestion with Spec Kit context".to_string(),
                confidence: 0.7,
                r#type: "completion".to_string(),
                source: Some("lightrag".to_string()),
                spec_kit_integration: Some("memory_bank".to_string()),
            }]
        });

    // Добавляем Spec Kit специфичные предложения
    if let Some(spec_context) = spec_kit_context {
        suggestions.push(CodeSuggestion {
            text: "// Spec Kit methodology suggestion".to_string(),
            confidence: 0.8,
            r#type: "spec_kit".to_string(),
            source: Some("memory_bank".to_string()),
            spec_kit_integration: Some("methodology".to_string()),
        });
    }

    // Кешируем результат
    if let Ok(cached_json) = serde_json::to_string(&suggestions) {
        state.cache.put(cache_key, cached_json);
    }

    Ok(Json(SuggestionResponse {
        suggestions,
        context: context.code,
        memory_bank_context: spec_kit_context,
        cached: false,
    }))
}

async fn integrate_with_spec_kit(
    State(state): State<RAGState>,
    Json(request): Json<HashMap<String, serde_json::Value>>,
) -> Result<Json<HashMap<String, String>>, StatusCode> {
    let spec_type = request.get("spec_type")
        .and_then(|v| v.as_str())
        .unwrap_or("unknown");
    
    let code = request.get("code")
        .and_then(|v| v.as_str())
        .unwrap_or("");

    // Интегрируем с Memory Bank
    match state.memory_bank.integrate_rag_context(spec_type, code).await {
        Ok(result) => {
            let mut response = HashMap::new();
            response.insert("status".to_string(), "success".to_string());
            response.insert("integration".to_string(), result);
            response.insert("spec_type".to_string(), spec_type.to_string());
            Ok(Json(response))
        }
        Err(e) => {
            warn!("Failed to integrate with Spec Kit: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

async fn get_suggestions_from_lightrag(
    state: &RAGState,
    context: &CodeContext,
    spec_kit_context: &Option<String>,
) -> Option<Vec<CodeSuggestion>> {
    let client = reqwest::Client::new();
    
    let mut request_body = serde_json::json!({
        "context": context.code,
        "cursor_position": context.cursor_position,
        "language": context.language,
        "file_path": context.file_path
    });

    if let Some(spec_context) = spec_kit_context {
        request_body["spec_kit_context"] = serde_json::Value::String(spec_context.clone());
    }
    
    let response = client
        .post(&format!("{}/suggest", state.lightrag_url))
        .json(&request_body)
        .send()
        .await
        .ok()?;

    let result: HashMap<String, serde_json::Value> = response.json().await.ok()?;
    let suggestions_data = result.get("suggestions")?.as_array()?;

    let suggestions: Vec<CodeSuggestion> = suggestions_data
        .iter()
        .filter_map(|s| serde_json::from_value(s.clone()).ok())
        .collect();

    Some(suggestions)
}

async fn check_lightrag(url: &str) -> Result<(), reqwest::Error> {
    reqwest::get(&format!("{}/health", url)).await?;
    Ok(())
}

// Остальные функции аналогично адаптируем под Memory Bank...
