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

#[derive(Clone)]
struct AppState {
    lightrag_url: String,
    n8n_url: String,
    n8n_user: String,
    n8n_password: String,
    cache: Arc<lru::LruCache<String, String>>,
}

#[derive(Deserialize)]
struct CodeContext {
    file_path: String,
    code: String,
    language: String,
    cursor_position: Option<HashMap<String, i32>>,
}

#[derive(Serialize)]
struct SuggestionResponse {
    suggestions: Vec<CodeSuggestion>,
    context: String,
    cached: bool,
}

#[derive(Serialize)]
struct CodeSuggestion {
    text: String,
    confidence: f64,
    r#type: String,
    source: Option<String>,
}

#[derive(Serialize)]
struct HealthResponse {
    status: String,
    services: HashMap<String, String>,
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let state = AppState {
        lightrag_url: std::env::var("LIGHTRAG_URL")
            .unwrap_or_else(|_| "http://lightrag:8000".to_string()),
        n8n_url: std::env::var("N8N_URL")
            .unwrap_or_else(|_| "http://n8n:5678".to_string()),
        n8n_user: std::env::var("N8N_USER")
            .unwrap_or_else(|_| "admin".to_string()),
        n8n_password: std::env::var("N8N_PASSWORD")
            .unwrap_or_else(|_| "admin123".to_string()),
        cache: Arc::new(lru::LruCache::new(
            std::num::NonZeroUsize::new(1000).unwrap(),
        )),
    };

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/health", get(health_check))
        .route("/api/suggest", post(suggest_code))
        .route("/api/context/search", post(search_context))
        .route("/api/context/examples", post(get_examples))
        .route("/api/learn", post(learn_from_code))
        .route("/api/workflow/trigger/:workflow_id", post(trigger_workflow))
        .layer(cors)
        .layer(TraceLayer::new_for_http())
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8000")
        .await
        .unwrap();

    info!("🚀 RAG Proxy server running on http://0.0.0.0:8000");
    
    axum::serve(listener, app).await.unwrap();
}

async fn health_check(State(state): State<AppState>) -> Json<HealthResponse> {
    let mut services = HashMap::new();
    
    // Проверяем LightRAG
    match check_lightrag(&state.lightrag_url).await {
        Ok(_) => services.insert("lightrag".to_string(), "healthy".to_string()),
        Err(_) => services.insert("lightrag".to_string(), "unhealthy".to_string()),
    };
    
    // Проверяем n8n
    match check_n8n(&state.n8n_url).await {
        Ok(_) => services.insert("n8n".to_string(), "healthy".to_string()),
        Err(_) => services.insert("n8n".to_string(), "unhealthy".to_string()),
    };

    Json(HealthResponse {
        status: "healthy".to_string(),
        services,
    })
}

async fn suggest_code(
    State(state): State<AppState>,
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
            cached: true,
        }));
    }

    // Получаем предложения от LightRAG
    let suggestions = get_suggestions_from_lightrag(&state, &context).await
        .unwrap_or_else(|| {
            vec![CodeSuggestion {
                text: "// AI suggestion placeholder".to_string(),
                confidence: 0.7,
                r#type: "completion".to_string(),
                source: Some("lightrag".to_string()),
            }]
        });

    // Кешируем результат
    if let Ok(cached_json) = serde_json::to_string(&suggestions) {
        state.cache.put(cache_key, cached_json);
    }

    Ok(Json(SuggestionResponse {
        suggestions,
        context: context.code,
        cached: false,
    }))
}

async fn search_context(
    State(state): State<AppState>,
    Json(query): Json<HashMap<String, String>>,
) -> Result<Json<HashMap<String, serde_json::Value>>, StatusCode> {
    let query_text = query.get("query").unwrap_or(&"".to_string()).clone();
    
    let client = reqwest::Client::new();
    let response = client
        .post(&format!("{}/query", state.lightrag_url))
        .json(&serde_json::json!({
            "query": query_text,
            "mode": "hybrid",
            "top_k": 5
        }))
        .send()
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let result: HashMap<String, serde_json::Value> = response
        .json()
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(result))
}

async fn get_examples(
    State(_state): State<AppState>,
    Json(query): Json<HashMap<String, String>>,
) -> Result<Json<HashMap<String, Vec<serde_json::Value>>>, StatusCode> {
    let topic = query.get("topic").unwrap_or(&"".to_string()).clone();
    
    // Простые примеры для демонстрации
    let examples = vec![
        serde_json::json!({
            "title": format!("Example for: {}", topic),
            "code": "// Example code here",
            "description": "This is an example",
            "language": "typescript"
        })
    ];

    Ok(Json(HashMap::from([("examples".to_string(), examples)])))
}

async fn learn_from_code(
    State(state): State<AppState>,
    Json(context): Json<CodeContext>,
) -> Result<Json<HashMap<String, String>>, StatusCode> {
    let client = reqwest::Client::new();
    
    let response = client
        .post(&format!("{}/insert_code", state.lightrag_url))
        .json(&context)
        .send()
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let result: HashMap<String, String> = response
        .json()
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(result))
}

async fn trigger_workflow(
    State(state): State<AppState>,
    Path(workflow_id): Path<String>,
    Json(payload): Json<HashMap<String, serde_json::Value>>,
) -> Result<Json<HashMap<String, serde_json::Value>>, StatusCode> {
    let client = reqwest::Client::new();
    
    let response = client
        .post(&format!("{}/webhook/{}", state.n8n_url, workflow_id))
        .basic_auth(&state.n8n_user, Some(&state.n8n_password))
        .json(&payload)
        .send()
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let result: HashMap<String, serde_json::Value> = response
        .json()
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(result))
}

async fn get_suggestions_from_lightrag(
    state: &AppState,
    context: &CodeContext,
) -> Option<Vec<CodeSuggestion>> {
    let client = reqwest::Client::new();
    
    let response = client
        .post(&format!("{}/suggest", state.lightrag_url))
        .json(&serde_json::json!({
            "context": context.code,
            "cursor_position": context.cursor_position,
            "language": context.language
        }))
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

async fn check_n8n(url: &str) -> Result<(), reqwest::Error> {
    reqwest::get(&format!("{}/healthz", url)).await?;
    Ok(())
}
