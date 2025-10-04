"""
Configuration management for Intelligent n8n Workflow Creation System
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class ServerConfig(BaseSettings):
    """Server configuration"""

    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")


class LightRAGConfig(BaseSettings):
    """LightRAG configuration"""

    url: str = Field(default="http://localhost:8000", env="LIGHTRAG_URL")
    api_key: Optional[str] = Field(default=None, env="LIGHTRAG_API_KEY")
    workspace: str = Field(default="/workspace/lightrag", env="LIGHTRAG_WORKSPACE")
    
    # Documentation sources configuration
    n8n_docs_url: str = Field(
        default="https://docs.n8n.io", env="N8N_DOCS_URL"
    )
    n8n_nodes_repo: str = Field(
        default="https://github.com/n8n-io/n8n-nodes-base", env="N8N_NODES_REPO"
    )
    n8n_community_nodes_repo: str = Field(
        default="https://github.com/n8n-io/n8n-nodes-community", env="N8N_COMMUNITY_NODES_REPO"
    )
    n8n_api_docs_url: str = Field(
        default="https://docs.n8n.io/api", env="N8N_API_DOCS_URL"
    )
    documentation_cache_dir: str = Field(
        default="./data/documentation", env="DOCS_CACHE_DIR"
    )
    update_interval_hours: int = Field(
        default=24, env="DOCS_UPDATE_INTERVAL_HOURS"
    )


class SupabaseConfig(BaseSettings):
    """Supabase configuration"""

    url: str = Field(default="http://localhost:54321", env="SUPABASE_URL")
    anon_key: str = Field(
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0",
        env="SUPABASE_ANON_KEY",
    )
    service_key: str = Field(
        default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU",
        env="SUPABASE_SERVICE_KEY",
    )


class N8nConfig(BaseSettings):
    """n8n configuration"""

    url: str = Field(default="http://localhost:5678", env="N8N_URL")
    user: str = Field(default="admin", env="N8N_USER")
    password: str = Field(default="admin123", env="N8N_PASSWORD")
    api_key: Optional[str] = Field(default=None, env="N8N_API_KEY")


class OllamaConfig(BaseSettings):
    """Ollama configuration"""

    model_config = {"protected_namespaces": ("settings_",)}

    base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    model_code: str = Field(default="llama3.2:3b", env="OLLAMA_MODEL_CODE")
    model_embedding: str = Field(
        default="nomic-embed-text:latest", env="OLLAMA_MODEL_EMBEDDING"
    )
    model_analysis: str = Field(default="llama3.2:7b", env="OLLAMA_MODEL_ANALYSIS")


class OpenAIConfig(BaseSettings):
    """OpenAI configuration (optional fallback)"""

    api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    embedding_model: str = Field(
        default="text-embedding-3-small", env="OPENAI_EMBEDDING_MODEL"
    )


class DatabaseConfig(BaseSettings):
    """Database configuration"""

    url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/intelligent_n8n",
        env="DATABASE_URL",
    )
    vector_dimension: int = Field(default=1536, env="VECTOR_DIMENSION")


class MLConfig(BaseSettings):
    """ML model configuration"""

    model_config = {"protected_namespaces": ("settings_",)}

    model_path: str = Field(default="./models", env="ML_MODEL_PATH")
    training_data_path: str = Field(default="./data/training", env="TRAINING_DATA_PATH")
    feedback_data_path: str = Field(default="./data/feedback", env="FEEDBACK_DATA_PATH")


class CacheConfig(BaseSettings):
    """Cache configuration"""

    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    ttl: int = Field(default=3600, env="CACHE_TTL")


class SecurityConfig(BaseSettings):
    """Security configuration"""

    secret_key: str = Field(default="your_secret_key_here", env="SECRET_KEY")
    jwt_secret: str = Field(default="your_jwt_secret_here", env="JWT_SECRET")
    access_token_expire_minutes: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )


class FileProcessingConfig(BaseSettings):
    """File processing configuration"""

    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    supported_extensions: str = Field(
        default=".py,.js,.ts,.tsx,.jsx,.json,.yaml,.yml,.md,.txt",
        env="SUPPORTED_EXTENSIONS",
    )

    @property
    def supported_extensions_list(self) -> list[str]:
        """Get supported extensions as a list"""
        return [ext.strip() for ext in self.supported_extensions.split(",")]


class PerformanceConfig(BaseSettings):
    """Performance configuration"""

    max_concurrent_analyses: int = Field(default=5, env="MAX_CONCURRENT_ANALYSES")
    analysis_timeout: int = Field(default=300, env="ANALYSIS_TIMEOUT")  # 5 minutes
    workflow_generation_timeout: int = Field(
        default=120, env="WORKFLOW_GENERATION_TIMEOUT"
    )  # 2 minutes


class Config(BaseSettings):
    """Main configuration class"""

    server: ServerConfig = ServerConfig()
    lightrag: LightRAGConfig = LightRAGConfig()
    supabase: SupabaseConfig = SupabaseConfig()
    n8n: N8nConfig = N8nConfig()
    ollama: OllamaConfig = OllamaConfig()
    openai: OpenAIConfig = OpenAIConfig()
    database: DatabaseConfig = DatabaseConfig()
    ml: MLConfig = MLConfig()
    cache: CacheConfig = CacheConfig()
    security: SecurityConfig = SecurityConfig()
    file_processing: FileProcessingConfig = FileProcessingConfig()
    performance: PerformanceConfig = PerformanceConfig()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global config instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance"""
    return config


def setup_directories(config: Config) -> None:
    """Setup required directories"""
    directories = [
        config.ml.model_path,
        config.ml.training_data_path,
        config.ml.feedback_data_path,
        config.lightrag.workspace,
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
