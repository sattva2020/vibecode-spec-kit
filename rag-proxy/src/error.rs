// use std::fmt; // Unused after removing manual Display implementation

#[derive(Debug, thiserror::Error)]
pub enum RAGProxyError {
    #[error("Service unavailable: {0}")]
    ServiceUnavailable(String),
    
    #[error("Service error: {0}")]
    ServiceError(String),
    
    #[error("Configuration error: {0}")]
    ConfigurationError(String),
    
    #[error("Memory Bank error: {0}")]
    MemoryBankError(String),
    
    #[error("Cache error: {0}")]
    CacheError(#[from] crate::cache::CacheError),
    
    #[error("HTTP client error: {0}")]
    HttpError(#[from] reqwest::Error),
    
    #[error("JSON serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),
    
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
    
    #[error("Environment variable error: {0}")]
    EnvVarError(#[from] std::env::VarError),
    
    #[error("Parse error: {0}")]
    ParseError(String),
    
    #[error("Timeout error: {0}")]
    TimeoutError(String),
    
    #[error("Validation error: {0}")]
    ValidationError(String),
    
    #[error("Authentication error: {0}")]
    AuthenticationError(String),
    
    #[error("Rate limit exceeded: {0}")]
    RateLimitError(String),
    
    #[error("Unknown error: {0}")]
    Unknown(String),
}

impl RAGProxyError {
    pub fn service_unavailable<S: Into<String>>(message: S) -> Self {
        Self::ServiceUnavailable(message.into())
    }
    
    pub fn service_error<S: Into<String>>(message: S) -> Self {
        Self::ServiceError(message.into())
    }
    
    pub fn configuration_error<S: Into<String>>(message: S) -> Self {
        Self::ConfigurationError(message.into())
    }
    
    pub fn memory_bank_error<S: Into<String>>(message: S) -> Self {
        Self::MemoryBankError(message.into())
    }
    
    pub fn parse_error<S: Into<String>>(message: S) -> Self {
        Self::ParseError(message.into())
    }
    
    pub fn timeout_error<S: Into<String>>(message: S) -> Self {
        Self::TimeoutError(message.into())
    }
    
    pub fn validation_error<S: Into<String>>(message: S) -> Self {
        Self::ValidationError(message.into())
    }
    
    pub fn authentication_error<S: Into<String>>(message: S) -> Self {
        Self::AuthenticationError(message.into())
    }
    
    pub fn rate_limit_error<S: Into<String>>(message: S) -> Self {
        Self::RateLimitError(message.into())
    }
    
    pub fn unknown<S: Into<String>>(message: S) -> Self {
        Self::Unknown(message.into())
    }
    
    pub fn status_code(&self) -> axum::http::StatusCode {
        match self {
            Self::ServiceUnavailable(_) => axum::http::StatusCode::SERVICE_UNAVAILABLE,
            Self::ServiceError(_) => axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Self::ConfigurationError(_) => axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Self::MemoryBankError(_) => axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Self::CacheError(_) => axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Self::HttpError(_) => axum::http::StatusCode::BAD_GATEWAY,
            Self::SerializationError(_) => axum::http::StatusCode::BAD_REQUEST,
            Self::IoError(_) => axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Self::EnvVarError(_) => axum::http::StatusCode::INTERNAL_SERVER_ERROR,
            Self::ParseError(_) => axum::http::StatusCode::BAD_REQUEST,
            Self::TimeoutError(_) => axum::http::StatusCode::REQUEST_TIMEOUT,
            Self::ValidationError(_) => axum::http::StatusCode::BAD_REQUEST,
            Self::AuthenticationError(_) => axum::http::StatusCode::UNAUTHORIZED,
            Self::RateLimitError(_) => axum::http::StatusCode::TOO_MANY_REQUESTS,
            Self::Unknown(_) => axum::http::StatusCode::INTERNAL_SERVER_ERROR,
        }
    }
    
    pub fn error_code(&self) -> &'static str {
        match self {
            Self::ServiceUnavailable(_) => "SERVICE_UNAVAILABLE",
            Self::ServiceError(_) => "SERVICE_ERROR",
            Self::ConfigurationError(_) => "CONFIGURATION_ERROR",
            Self::MemoryBankError(_) => "MEMORY_BANK_ERROR",
            Self::CacheError(_) => "CACHE_ERROR",
            Self::HttpError(_) => "HTTP_ERROR",
            Self::SerializationError(_) => "SERIALIZATION_ERROR",
            Self::IoError(_) => "IO_ERROR",
            Self::EnvVarError(_) => "ENV_VAR_ERROR",
            Self::ParseError(_) => "PARSE_ERROR",
            Self::TimeoutError(_) => "TIMEOUT_ERROR",
            Self::ValidationError(_) => "VALIDATION_ERROR",
            Self::AuthenticationError(_) => "AUTHENTICATION_ERROR",
            Self::RateLimitError(_) => "RATE_LIMIT_ERROR",
            Self::Unknown(_) => "UNKNOWN_ERROR",
        }
    }
    
    pub fn is_retryable(&self) -> bool {
        match self {
            Self::ServiceUnavailable(_) => true,
            Self::ServiceError(_) => true,
            Self::HttpError(_) => true,
            Self::TimeoutError(_) => true,
            Self::RateLimitError(_) => true,
            _ => false,
        }
    }
    
    pub fn retry_after_seconds(&self) -> Option<u64> {
        match self {
            Self::RateLimitError(_) => Some(60),
            Self::TimeoutError(_) => Some(5),
            Self::ServiceUnavailable(_) => Some(10),
            _ => None,
        }
    }
}

// Display trait is automatically implemented by thiserror::Error

// Conversion from other error types
impl From<anyhow::Error> for RAGProxyError {
    fn from(err: anyhow::Error) -> Self {
        Self::Unknown(err.to_string())
    }
}

// Result type alias for convenience
pub type Result<T> = std::result::Result<T, RAGProxyError>;

// Error response structure for API
#[derive(Debug, serde::Serialize)]
pub struct ErrorResponse {
    pub error: String,
    pub code: String,
    pub message: String,
    pub retryable: bool,
    pub retry_after: Option<u64>,
    pub timestamp: String,
}

impl From<RAGProxyError> for ErrorResponse {
    fn from(err: RAGProxyError) -> Self {
        Self {
            error: err.error_code().to_string(),
            code: err.status_code().as_str().to_string(),
            message: err.to_string(),
            retryable: err.is_retryable(),
            retry_after: err.retry_after_seconds(),
            timestamp: sqlx::types::chrono::Utc::now().to_rfc3339(),
        }
    }
}
