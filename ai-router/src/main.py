"""
AI Router Service - Simplified Version
Маршрутизирует запросы к различным AI провайдерам в зависимости от типа задачи
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import asyncio
import logging

from .config import Settings
from .models import AIRequest, AIResponse, TaskType, ProviderType
from .router import AIRouter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Global router instance
router = None

@app.on_event("startup")
async def startup_event():
    """Initialize the service on startup"""
    global router
    logger.info("Starting AI Router Service")
    
    try:
        settings = Settings()
        router = AIRouter(settings)
        await router.initialize()
        logger.info("AI Router Service started successfully")
    except Exception as e:
        logger.error(f"Failed to start AI Router Service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AI Router Service")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if router:
            health_data = await router.health_check()
            return health_data
        else:
            return {"status": "unhealthy", "error": "Router not initialized"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/providers")
async def list_providers():
    """List available AI providers"""
    return {
        "providers": [
            {
                "name": "github_copilot",
                "status": "available",
                "description": "GitHub Copilot - Best for code generation",
            },
            {
                "name": "cursor",
                "status": "available", 
                "description": "Cursor IDE - Best for project analysis",
            },
            {
                "name": "ollama",
                "status": "available",
                "description": "Local Ollama - For graph database and embeddings",
            },
        ]
    }

@app.post("/route")
async def route_ai_request(request: AIRequest) -> AIResponse:
    """
    Route AI request to appropriate provider based on task type
    """
    try:
        if not router:
            raise HTTPException(status_code=503, detail="Router not initialized")
            
        logger.info(f"Routing AI request: {request.task_type}")
        
        # Route the request
        response = await router.route_request(request)
        
        logger.info(f"AI request completed: {response.provider}")
        return response
        
    except Exception as e:
        logger.error(f"AI request failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI request failed: {str(e)}")

@app.post("/n8n/analyze")
async def analyze_for_n8n(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Specialized endpoint for n8n workflow analysis
    """
    try:
        if not router:
            raise HTTPException(status_code=503, detail="Router not initialized")
            
        # Convert to AI request
        ai_request = AIRequest(
            task_type=TaskType.PROJECT_ANALYSIS,
            prompt=request.get("prompt", ""),
            context=request.get("context", {}),
            complexity=request.get("complexity", "medium"),
        )

        response = await router.route_request(ai_request)

        return {
            "analysis": response.content,
            "provider": response.provider,
            "confidence": response.confidence,
        }

    except Exception as e:
        logger.error(f"n8n analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"n8n analysis failed: {str(e)}")

@app.post("/code/generate")
async def generate_code(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Specialized endpoint for code generation
    """
    try:
        if not router:
            raise HTTPException(status_code=503, detail="Router not initialized")
            
        ai_request = AIRequest(
            task_type=TaskType.CODE_GENERATION,
            prompt=request.get("prompt", ""),
            context=request.get("context", {}),
            complexity=request.get("complexity", "medium"),
        )

        response = await router.route_request(ai_request)

        return {
            "code": response.content,
            "provider": response.provider,
            "explanation": response.metadata.get("explanation", ""),
        }

    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)