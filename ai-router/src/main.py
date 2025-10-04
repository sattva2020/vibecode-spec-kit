"""
AI Router Service
Маршрутизирует запросы к различным AI провайдерам в зависимости от типа задачи
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import structlog
from typing import Dict, Any, Optional
import asyncio

from .config import Settings
from .models import AIRequest, AIResponse, TaskType, ProviderType
from .router import AIRouter
from .clients import ClaudeClient, OpenAIClient, OllamaClient
from .health import HealthChecker

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="AI Router Service",
    description="Intelligent routing to AI providers based on task type",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize settings and components
settings = Settings()
health_checker = HealthChecker()

# Initialize AI clients
claude_client = ClaudeClient(settings)
openai_client = OpenAIClient(settings)
ollama_client = OllamaClient(settings)

# Initialize AI router
ai_router = AIRouter(
    claude_client=claude_client,
    openai_client=openai_client,
    ollama_client=ollama_client,
    default_provider=settings.ai_default_provider,
    fallback_provider=settings.ai_fallback_provider,
)


@app.on_event("startup")
async def startup_event():
    """Initialize the service on startup"""
    logger.info("Starting AI Router Service")

    # Check health of all AI providers
    health_status = await health_checker.check_all_providers()
    logger.info("AI providers health status", providers=health_status)

    # Initialize AI router
    await ai_router.initialize()
    logger.info("AI Router Service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AI Router Service")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        providers_health = await health_checker.check_all_providers()
        overall_health = all(providers_health.values())

        return {
            "status": "healthy" if overall_health else "degraded",
            "providers": providers_health,
            "service": "ai-router",
            "version": "1.0.0",
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/providers")
async def list_providers():
    """List available AI providers"""
    return {
        "providers": [
            {
                "name": "claude",
                "status": "available",
                "description": "Anthropic Claude - Best for analysis and complex tasks",
            },
            {
                "name": "openai",
                "status": "available",
                "description": "OpenAI GPT-4 - Best for code generation and quick tasks",
            },
            {
                "name": "ollama",
                "status": "available",
                "description": "Local Ollama - Only for graph database and embeddings",
            },
        ]
    }


@app.post("/route")
async def route_ai_request(request: AIRequest) -> AIResponse:
    """
    Route AI request to appropriate provider based on task type
    """
    try:
        logger.info(
            "Routing AI request",
            task_type=request.task_type,
            complexity=request.complexity,
        )

        # Route the request
        response = await ai_router.route_request(request)

        logger.info(
            "AI request completed",
            provider=response.provider,
            duration=response.duration,
            tokens_used=response.tokens_used,
        )

        return response

    except Exception as e:
        logger.error("AI request failed", error=str(e), task_type=request.task_type)
        raise HTTPException(status_code=500, detail=f"AI request failed: {str(e)}")


@app.post("/n8n/analyze")
async def analyze_for_n8n(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Specialized endpoint for n8n workflow analysis
    Always uses Claude for better architectural understanding
    """
    try:
        # Convert to AI request with n8n-specific parameters
        ai_request = AIRequest(
            task_type=TaskType.PROJECT_ANALYSIS,
            prompt=request.get("prompt", ""),
            context=request.get("context", {}),
            complexity=request.get("complexity", "medium"),
            force_provider=ProviderType.CLAUDE,  # Force Claude for n8n
        )

        response = await ai_router.route_request(ai_request)

        return {
            "analysis": response.content,
            "provider": response.provider,
            "confidence": response.confidence,
            "workflow_suggestions": response.metadata.get("workflow_suggestions", []),
            "api_recommendations": response.metadata.get("api_recommendations", []),
        }

    except Exception as e:
        logger.error("n8n analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"n8n analysis failed: {str(e)}")


@app.post("/code/generate")
async def generate_code(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Specialized endpoint for code generation
    Prefers OpenAI for code generation tasks
    """
    try:
        ai_request = AIRequest(
            task_type=TaskType.CODE_GENERATION,
            prompt=request.get("prompt", ""),
            context=request.get("context", {}),
            complexity=request.get("complexity", "medium"),
            force_provider=ProviderType.OPENAI,  # Force OpenAI for code
        )

        response = await ai_router.route_request(ai_request)

        return {
            "code": response.content,
            "provider": response.provider,
            "language": response.metadata.get("language", "unknown"),
            "explanation": response.metadata.get("explanation", ""),
            "suggestions": response.metadata.get("suggestions", []),
        }

    except Exception as e:
        logger.error("Code generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")


@app.post("/graph/search")
async def graph_search(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Specialized endpoint for knowledge graph search
    Always uses Ollama for local graph operations
    """
    try:
        ai_request = AIRequest(
            task_type=TaskType.SEMANTIC_SEARCH,
            prompt=request.get("query", ""),
            context=request.get("context", {}),
            force_provider=ProviderType.OLLAMA,  # Force Ollama for graph
        )

        response = await ai_router.route_request(ai_request)

        return {
            "results": response.content,
            "provider": response.provider,
            "similarity_scores": response.metadata.get("similarity_scores", []),
            "entities": response.metadata.get("entities", []),
            "relations": response.metadata.get("relations", []),
        }

    except Exception as e:
        logger.error("Graph search failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Graph search failed: {str(e)}")


@app.get("/metrics")
async def get_metrics():
    """Get service metrics"""
    return {
        "total_requests": ai_router.metrics.total_requests,
        "requests_by_provider": ai_router.metrics.requests_by_provider,
        "average_response_time": ai_router.metrics.average_response_time,
        "error_rate": ai_router.metrics.error_rate,
        "uptime": ai_router.metrics.uptime,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081)
