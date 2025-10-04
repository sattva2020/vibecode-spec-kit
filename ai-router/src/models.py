"""
Data models for AI Router Service
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum
import time


class TaskType(str, Enum):
    """Types of AI tasks"""

    PROJECT_ANALYSIS = "project_analysis"
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DOCUMENTATION = "documentation"
    SEMANTIC_SEARCH = "semantic_search"
    WORKFLOW_CREATION = "workflow_creation"
    API_INTEGRATION = "api_integration"
    TESTING = "testing"
    REFACTORING = "refactoring"
    DEBUGGING = "debugging"


class ProviderType(str, Enum):
    """AI providers"""

    CURSOR = "cursor"
    GITHUB_COPILOT = "github_copilot"
    CLAUDE = "claude"
    OPENAI = "openai"
    OLLAMA = "ollama"
    GEMINI = "gemini"


class Complexity(str, Enum):
    """Task complexity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ENTERPRISE = "enterprise"


class AIRequest(BaseModel):
    """Request for AI processing"""

    task_type: TaskType
    prompt: str
    context: Dict[str, Any] = Field(default_factory=dict)
    complexity: Complexity = Complexity.MEDIUM
    force_provider: Optional[ProviderType] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: bool = False

    class Config:
        use_enum_values = True


class AIResponse(BaseModel):
    """Response from AI processing"""

    content: str
    provider: ProviderType
    model: str
    task_type: TaskType
    duration: float = Field(description="Processing time in seconds")
    tokens_used: Optional[int] = None
    confidence: Optional[float] = Field(ge=0.0, le=1.0, description="Confidence score")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

    class Config:
        use_enum_values = True


class ProviderHealth(BaseModel):
    """Health status of an AI provider"""

    provider: ProviderType
    status: str  # "healthy", "degraded", "unhealthy"
    response_time: Optional[float] = None
    last_check: float = Field(default_factory=time.time)
    error_message: Optional[str] = None


class RouterMetrics(BaseModel):
    """Metrics for AI router"""

    total_requests: int = 0
    requests_by_provider: Dict[str, int] = Field(default_factory=dict)
    requests_by_task_type: Dict[str, int] = Field(default_factory=dict)
    average_response_time: float = 0.0
    error_rate: float = 0.0
    uptime: float = 0.0
    last_reset: float = Field(default_factory=time.time)


class TaskRouting(BaseModel):
    """Task routing configuration"""

    task_type: TaskType
    preferred_provider: ProviderType
    fallback_provider: ProviderType
    min_complexity_for_provider: Optional[Complexity] = None

    class Config:
        use_enum_values = True


# Default routing rules
DEFAULT_ROUTING_RULES = [
    # n8n and architecture tasks - Cursor first, then GitHub Copilot, then Claude
    TaskRouting(
        task_type=TaskType.PROJECT_ANALYSIS,
        preferred_provider=ProviderType.CURSOR,
        fallback_provider=ProviderType.GITHUB_COPILOT,
    ),
    TaskRouting(
        task_type=TaskType.WORKFLOW_CREATION,
        preferred_provider=ProviderType.CURSOR,
        fallback_provider=ProviderType.GITHUB_COPILOT,
    ),
    TaskRouting(
        task_type=TaskType.API_INTEGRATION,
        preferred_provider=ProviderType.GITHUB_COPILOT,
        fallback_provider=ProviderType.CURSOR,
    ),
    # Code generation - GitHub Copilot first, then OpenAI
    TaskRouting(
        task_type=TaskType.CODE_GENERATION,
        preferred_provider=ProviderType.GITHUB_COPILOT,
        fallback_provider=ProviderType.OPENAI,
    ),
    TaskRouting(
        task_type=TaskType.REFACTORING,
        preferred_provider=ProviderType.OPENAI,
        fallback_provider=ProviderType.CLAUDE,
    ),
    TaskRouting(
        task_type=TaskType.DEBUGGING,
        preferred_provider=ProviderType.OPENAI,
        fallback_provider=ProviderType.CLAUDE,
    ),
    # Documentation - Claude
    TaskRouting(
        task_type=TaskType.DOCUMENTATION,
        preferred_provider=ProviderType.CLAUDE,
        fallback_provider=ProviderType.OPENAI,
    ),
    TaskRouting(
        task_type=TaskType.CODE_REVIEW,
        preferred_provider=ProviderType.CLAUDE,
        fallback_provider=ProviderType.OPENAI,
    ),
    # Graph operations - Ollama only
    TaskRouting(
        task_type=TaskType.SEMANTIC_SEARCH,
        preferred_provider=ProviderType.OLLAMA,
        fallback_provider=ProviderType.OLLAMA,
    ),
]
