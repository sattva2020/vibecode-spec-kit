"""
Configuration for AI Router Service
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from enum import Enum


class ProviderType(str, Enum):
    CLAUDE = "claude"
    OPENAI = "openai"
    OLLAMA = "ollama"
    GITHUB_COPILOT = "github_copilot"
    CURSOR = "cursor"


class Settings(BaseSettings):
    """Application settings"""

    # Server configuration
    ai_router_host: str = Field(default="0.0.0.0", env="AI_ROUTER_HOST")
    ai_router_port: int = Field(default=8081, env="AI_ROUTER_PORT")

    # AI Router configuration
    ai_router_enabled: bool = Field(default=True, env="AI_ROUTER_ENABLED")
    ai_default_provider: ProviderType = Field(
        default=ProviderType.CLAUDE, env="AI_DEFAULT_PROVIDER"
    )
    ai_fallback_provider: ProviderType = Field(
        default=ProviderType.OPENAI, env="AI_FALLBACK_PROVIDER"
    )

    # Anthropic Claude configuration
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    claude_model: str = Field(default="claude-3-5-sonnet-20241022", env="CLAUDE_MODEL")
    claude_max_tokens: int = Field(default=8192, env="CLAUDE_MAX_TOKENS")
    claude_temperature: float = Field(default=0.1, env="CLAUDE_TEMPERATURE")

    # OpenAI configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    openai_code_model: str = Field(
        default="gpt-4-code-interpreter", env="OPENAI_CODE_MODEL"
    )
    openai_max_tokens: int = Field(default=4096, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.2, env="OPENAI_TEMPERATURE")

    # Google Gemini configuration
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    google_model: str = Field(default="gemini-pro", env="GOOGLE_MODEL")
    google_max_tokens: int = Field(default=2048, env="GOOGLE_MAX_TOKENS")

    # Cursor IDE Integration
    cursor_api_key: Optional[str] = Field(default=None, env="CURSOR_API_KEY")
    cursor_api_url: str = Field(
        default="https://api.cursor.sh/v1", env="CURSOR_API_URL"
    )
    cursor_session_name: str = Field(default="n8n-ai-router", env="CURSOR_SESSION_NAME")

    # GitHub Copilot Integration
    github_copilot_api_key: Optional[str] = Field(
        default=None, env="GITHUB_COPILOT_API_KEY"
    )
    github_copilot_api_url: str = Field(
        default="https://api.githubcopilot.com/v1", env="GITHUB_COPILOT_API_URL"
    )
    github_copilot_session_name: str = Field(
        default="n8n-ai-router", env="GITHUB_COPILOT_SESSION_NAME"
    )

    # AI Provider Mode
    ai_provider_mode: str = Field(
        default="subscription_first", env="AI_PROVIDER_MODE"
    )  # subscription_first, paid_only, cursor_only, copilot_only

    # Ollama configuration (only for graph DB)
    ollama_url: str = Field(default="http://localhost:11434", env="OLLAMA_URL")
    ollama_graph_model: str = Field(
        default="nomic-embed-text", env="OLLAMA_GRAPH_MODEL"
    )
    ollama_index_model: str = Field(
        default="qwen2.5-coder:1.5b", env="OLLAMA_INDEX_MODEL"
    )

    # Performance configuration
    request_timeout: int = Field(default=60, env="REQUEST_TIMEOUT")
    max_concurrent_requests: int = Field(default=10, env="MAX_CONCURRENT_REQUESTS")

    # Logging configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")

    class Config:
        env_file = ".env"
        case_sensitive = False
