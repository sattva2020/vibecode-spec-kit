"""
AI Router Service - Main routing logic
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import asyncio
import logging

from .config import Settings
from .models import AIRequest, AIResponse, TaskType, ProviderType
from .clients.github_copilot_client import GitHubCopilotAPIClient
from .clients.cursor_client import CursorAPIClient

logger = logging.getLogger(__name__)

class AIRouter:
    """AI Router Service"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.github_copilot_client = None
        self.cursor_client = None
        
    async def initialize(self):
        """Initialize AI Router and clients"""
        try:
            # Initialize GitHub Copilot client
            if self.settings.github_copilot_api_key:
                self.github_copilot_client = GitHubCopilotAPIClient(self.settings)
                await self.github_copilot_client.initialize()
                logger.info("GitHub Copilot client initialized")
            
            # Initialize Cursor client
            if self.settings.cursor_api_key:
                self.cursor_client = CursorAPIClient(self.settings)
                await self.cursor_client.initialize()
                logger.info("Cursor client initialized")
                
            logger.info("AI Router initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Router: {e}")
            raise
    
    async def route_request(self, request: AIRequest) -> AIResponse:
        """Route AI request to appropriate provider"""
        try:
            # Determine provider based on task type and settings
            provider = self._select_provider(request.task_type)
            
            # Route to appropriate client
            if provider == ProviderType.GITHUB_COPILOT and self.github_copilot_client:
                return await self._route_to_github_copilot(request)
            elif provider == ProviderType.CURSOR and self.cursor_client:
                return await self._route_to_cursor(request)
            else:
                raise HTTPException(
                    status_code=503, 
                    detail=f"Provider {provider} not available"
                )
                
        except Exception as e:
            logger.error(f"Error routing request: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _select_provider(self, task_type: TaskType) -> ProviderType:
        """Select appropriate provider for task type"""
        # GitHub Copilot preferred for code generation
        if task_type == TaskType.CODE_GENERATION:
            return ProviderType.GITHUB_COPILOT
        # Cursor preferred for project analysis
        elif task_type == TaskType.PROJECT_ANALYSIS:
            return ProviderType.CURSOR
        # Default to GitHub Copilot
        else:
            return ProviderType.GITHUB_COPILOT
    
    async def _route_to_github_copilot(self, request: AIRequest) -> AIResponse:
        """Route request to GitHub Copilot"""
        if request.task_type == TaskType.CODE_GENERATION:
            return await self.github_copilot_client.generate_code(request)
        else:
            return await self.github_copilot_client.analyze_for_n8n(request)
    
    async def _route_to_cursor(self, request: AIRequest) -> AIResponse:
        """Route request to Cursor"""
        if request.task_type == TaskType.CODE_GENERATION:
            return await self.cursor_client.generate_code(request)
        else:
            return await self.cursor_client.analyze_for_n8n(request)
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "providers": {
                "github_copilot": self.github_copilot_client is not None,
                "cursor": self.cursor_client is not None
            },
            "settings": {
                "default_provider": self.settings.ai_default_provider,
                "provider_mode": self.settings.ai_provider_mode
            }
        }

# Global router instance
router_instance: Optional[AIRouter] = None

async def get_router() -> AIRouter:
    """Get router instance"""
    global router_instance
    if router_instance is None:
        settings = Settings()
        router_instance = AIRouter(settings)
        await router_instance.initialize()
    return router_instance
