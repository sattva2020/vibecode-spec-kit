"""
Pytest configuration and fixtures for integration tests
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Generator
import httpx
import os
from unittest.mock import AsyncMock, MagicMock

from src.core.config import get_config, Config
from src.core.pipeline_coordinator import PipelineCoordinator, PipelineContext
from src.analyzers.project_analyzer import ProjectAnalyzer
from src.knowledge.lightrag_service import LightRAGService
from src.decision.ensemble_decision_engine import EnsembleDecisionEngine
from src.generators.workflow_generator import WorkflowGenerator


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config() -> Config:
    """Create test configuration"""
    # Override config for testing
    os.environ.update(
        {
            "DEBUG": "True",
            "LOG_LEVEL": "DEBUG",
            "LIGHTRAG_URL": "http://localhost:8000",
            "SUPABASE_URL": "http://localhost:54321",
            "N8N_URL": "http://localhost:5678",
            "OLLAMA_BASE_URL": "http://localhost:11434",
        }
    )
    return get_config()


@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """Create a temporary project directory for testing"""
    temp_dir = tempfile.mkdtemp()
    project_path = Path(temp_dir) / "test_project"
    project_path.mkdir(parents=True, exist_ok=True)

    # Create sample files
    (project_path / "main.py").write_text("""
import fastapi
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
""")

    (project_path / "requirements.txt").write_text("""
fastapi==0.104.1
uvicorn==0.24.0
""")

    (project_path / "README.md").write_text("""
# Test Project
A sample FastAPI project for testing.
""")

    yield project_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_lightrag_service():
    """Mock LightRAG service for testing"""
    from src.knowledge.lightrag_service import (
        KnowledgeQueryResult,
        N8nNodeInfo,
        WorkflowPattern,
    )

    service = AsyncMock(spec=LightRAGService)
    service.initialize_knowledge_base = AsyncMock(return_value=True)
    service.query_relevant_knowledge = AsyncMock(
        return_value=KnowledgeQueryResult(
            nodes=[
                N8nNodeInfo(
                    name="httpRequest",
                    display_name="HTTP Request",
                    description="Make HTTP requests",
                    category="core",
                    version="1.0",
                    parameters=[],
                    outputs=["main"],
                    inputs=["main"],
                    documentation="Make HTTP requests",
                    examples=[],
                    tags=["http", "api"],
                    confidence=0.9,
                )
            ],
            patterns=[
                WorkflowPattern(
                    name="API Integration",
                    description="Integrate with APIs",
                    category="integration",
                    nodes=["httpRequest", "function"],
                    connections=[],
                    use_cases=["api_monitoring"],
                    complexity="medium",
                    confidence=0.8,
                )
            ],
            related_concepts=["api", "http", "integration"],
            confidence=0.85,
            query_time=0.1,
        )
    )
    return service


@pytest.fixture
def mock_n8n_client():
    """Mock n8n API client for testing"""
    client = AsyncMock()
    client.get_workflows = AsyncMock(return_value=[])
    client.create_workflow = AsyncMock(return_value={"id": "test-workflow-123"})
    client.update_workflow = AsyncMock(return_value={"id": "test-workflow-123"})
    client.delete_workflow = AsyncMock(return_value=True)
    return client


@pytest.fixture
def pipeline_coordinator(test_config, mock_lightrag_service):
    """Create a pipeline coordinator for testing"""
    coordinator = PipelineCoordinator()

    # Set up mock services
    coordinator.set_knowledge_service(mock_lightrag_service)
    coordinator.set_project_analyzer(ProjectAnalyzer())
    coordinator.set_decision_engine(EnsembleDecisionEngine())
    coordinator.set_workflow_generator(WorkflowGenerator())
    coordinator.set_validator(AsyncMock())

    return coordinator


@pytest.fixture
def sample_project_analysis():
    """Sample project analysis data"""
    return {
        "project_path": "/test/project",
        "project_name": "test_project",
        "languages": {"python": 2, "markdown": 1},
        "technologies": [
            {
                "name": "fastapi",
                "type": "framework",
                "confidence": 0.9,
                "usage_patterns": ["api", "web"],
            }
        ],
        "architecture_type": "api",
        "complexity_score": 0.3,
        "automation_potential": 0.8,
        "suggested_workflows": ["api_monitoring", "deployment_automation"],
        "metadata": {"total_files": 3, "total_size": 1024},
    }


@pytest.fixture
def sample_workflow():
    """Sample n8n workflow for testing"""
    return {
        "name": "Test Workflow",
        "nodes": [
            {
                "id": "node1",
                "name": "Schedule Trigger",
                "type": "n8n-nodes-base.scheduleTrigger",
                "position": [100, 100],
                "parameters": {"rule": {"interval": [{"field": "hours"}]}},
            },
            {
                "id": "node2",
                "name": "HTTP Request",
                "type": "n8n-nodes-base.httpRequest",
                "position": [300, 100],
                "parameters": {"url": "http://localhost:8000/", "method": "GET"},
            },
        ],
        "connections": {
            "node1": {"main": [[{"node": "node2", "type": "main", "index": 0}]]}
        },
    }


@pytest.fixture
def http_client():
    """HTTP client for testing"""
    return httpx.AsyncClient(timeout=30.0)


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client for testing"""
    client = AsyncMock()
    client.generate = AsyncMock(
        return_value={"response": "This is a test response", "done": True}
    )
    client.embeddings = AsyncMock(
        return_value={
            "embeddings": [[0.1, 0.2, 0.3] * 512]  # Mock embedding vector
        }
    )
    return client


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing"""
    client = AsyncMock()
    client.table = AsyncMock()
    client.table().select = AsyncMock()
    client.table().insert = AsyncMock()
    client.table().update = AsyncMock()
    client.table().delete = AsyncMock()
    return client


@pytest.fixture(scope="session")
def test_docker_services():
    """Check if Docker services are running"""
    services = {
        "lightrag": "http://localhost:8000",
        "supabase": "http://localhost:54321",
        "n8n": "http://localhost:5678",
        "ollama": "http://localhost:11434",
    }

    return services


@pytest.fixture
def integration_test_data():
    """Test data for integration tests"""
    return {
        "test_project": {
            "path": "/tmp/test_project",
            "files": {
                "main.py": "import fastapi\napp = FastAPI()",
                "requirements.txt": "fastapi==0.104.1",
                "docker-compose.yml": "version: '3.8'\nservices:\n  app:\n    image: python:3.9",
            },
        },
        "expected_workflows": [
            "api_monitoring_workflow",
            "deployment_automation",
            "health_check_workflow",
        ],
        "expected_nodes": ["httpRequest", "scheduleTrigger", "function", "webhook"],
    }


# Test markers
pytest.mark.integration = pytest.mark.integration
pytest.mark.unit = pytest.mark.unit
pytest.mark.slow = pytest.mark.slow
pytest.mark.docker = pytest.mark.docker
