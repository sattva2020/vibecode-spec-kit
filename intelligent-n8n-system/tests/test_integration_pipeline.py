"""
Integration tests for the complete pipeline
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch
import tempfile
import shutil


@pytest.mark.integration
@pytest.mark.slow
class TestPipelineIntegration:
    """Integration tests for the complete pipeline"""

    @pytest.mark.asyncio
    async def test_complete_pipeline_execution(
        self, pipeline_coordinator, temp_project_dir, test_config
    ):
        """Test complete pipeline execution from start to finish"""

        # Mock the workflow generator to return a sample workflow
        mock_workflow = {
            "name": "Test API Workflow",
            "nodes": [
                {
                    "id": "trigger",
                    "name": "Schedule Trigger",
                    "type": "n8n-nodes-base.scheduleTrigger",
                    "parameters": {"rule": {"interval": [{"field": "hours"}]}},
                },
                {
                    "id": "http",
                    "name": "HTTP Request",
                    "type": "n8n-nodes-base.httpRequest",
                    "parameters": {"url": "http://localhost:8000/", "method": "GET"},
                },
            ],
            "connections": {
                "trigger": {"main": [[{"node": "http", "type": "main", "index": 0}]]}
            },
        }

        # Mock the workflow generator
        pipeline_coordinator.workflow_generator.generate_workflows = AsyncMock(
            return_value=[mock_workflow]
        )

        # Mock the validator
        pipeline_coordinator.validator.validate_workflows = AsyncMock(
            return_value={"valid": True, "confidence": 0.9}
        )

        # Execute the pipeline
        result = await pipeline_coordinator.execute_pipeline(
            project_path=temp_project_dir,
            request_id="test-request-123",
            user_id="test-user",
            metadata={"test": True},
        )

        # Verify results
        assert result.success is True
        assert len(result.workflows) == 1
        assert result.workflows[0]["name"] == "Test API Workflow"
        assert result.confidence_score > 0.0
        assert result.execution_time > 0.0

        # Verify all stages were executed
        assert len(result.context.stage_results) == 5
        assert "project_analysis" in str(result.context.stage_results.keys())
        assert "knowledge_query" in str(result.context.stage_results.keys())
        assert "decision_making" in str(result.context.stage_results.keys())
        assert "workflow_generation" in str(result.context.stage_results.keys())
        assert "validation" in str(result.context.stage_results.keys())

    @pytest.mark.asyncio
    async def test_pipeline_error_handling(
        self, pipeline_coordinator, temp_project_dir
    ):
        """Test pipeline error handling and recovery"""

        # Mock the project analyzer to raise an exception
        pipeline_coordinator.project_analyzer.analyze_project = AsyncMock(
            side_effect=Exception("Test error")
        )

        # Execute the pipeline
        result = await pipeline_coordinator.execute_pipeline(
            project_path=temp_project_dir,
            request_id="test-error-request",
            user_id="test-user",
        )

        # Verify error handling
        assert result.success is False
        assert result.error_message is not None
        assert "Test error" in result.error_message
        assert len(result.workflows) == 0

    @pytest.mark.asyncio
    async def test_pipeline_retry_mechanism(
        self, pipeline_coordinator, temp_project_dir
    ):
        """Test pipeline retry mechanism for transient failures"""

        call_count = 0

        async def failing_then_succeeding_analyzer(project_path):
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # Fail first 2 times
                raise Exception("Transient error")
            return {"project_name": "test", "technologies": []}

        # Mock the project analyzer to fail then succeed
        pipeline_coordinator.project_analyzer.analyze_project = (
            failing_then_succeeding_analyzer
        )

        # Mock other components to succeed
        pipeline_coordinator.knowledge_service.query_relevant_knowledge = AsyncMock(
            return_value={"nodes": [], "patterns": [], "confidence": 0.8}
        )
        pipeline_coordinator.decision_engine.make_decisions = AsyncMock(
            return_value={"workflows": [], "confidence": 0.7}
        )
        pipeline_coordinator.workflow_generator.generate_workflows = AsyncMock(
            return_value=[]
        )
        pipeline_coordinator.validator.validate_workflows = AsyncMock(
            return_value={"valid": True, "confidence": 0.9}
        )

        # Execute the pipeline
        result = await pipeline_coordinator.execute_pipeline(
            project_path=temp_project_dir,
            request_id="test-retry-request",
            user_id="test-user",
        )

        # Verify retry mechanism worked
        assert result.success is True
        assert call_count == 3  # Should have retried 2 times

    @pytest.mark.asyncio
    async def test_pipeline_status_monitoring(
        self, pipeline_coordinator, temp_project_dir
    ):
        """Test pipeline status monitoring during execution"""

        request_id = "test-status-request"

        # Start pipeline execution
        pipeline_task = asyncio.create_task(
            pipeline_coordinator.execute_pipeline(
                project_path=temp_project_dir,
                request_id=request_id,
                user_id="test-user",
            )
        )

        # Wait a bit for pipeline to start
        await asyncio.sleep(0.1)

        # Check status
        status = pipeline_coordinator.get_pipeline_status(request_id)
        assert status is not None
        assert status["request_id"] == request_id
        assert "state" in status
        assert "current_stage" in status
        assert "elapsed_time" in status
        assert "progress" in status

        # Wait for completion
        result = await pipeline_task

        # Verify final status
        assert result.success is True

        # Status should be cleaned up after completion
        final_status = pipeline_coordinator.get_pipeline_status(request_id)
        assert final_status is None

    @pytest.mark.asyncio
    async def test_pipeline_with_complex_project(
        self, pipeline_coordinator, test_config
    ):
        """Test pipeline with a complex project structure"""

        # Create a complex project structure
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "complex_project"
            project_path.mkdir(parents=True, exist_ok=True)

            # Create multiple files and directories
            (project_path / "src" / "api").mkdir(parents=True, exist_ok=True)
            (project_path / "src" / "models").mkdir(parents=True, exist_ok=True)
            (project_path / "tests").mkdir(parents=True, exist_ok=True)
            (project_path / "docs").mkdir(parents=True, exist_ok=True)

            # Create various file types
            (project_path / "src" / "api" / "main.py").write_text("""
from fastapi import FastAPI
from sqlalchemy import create_engine
import redis

app = FastAPI()
engine = create_engine("postgresql://user:pass@localhost/db")
redis_client = redis.Redis(host='localhost', port=6379)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
""")

            (project_path / "src" / "models" / "user.py").write_text("""
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100))
""")

            (project_path / "requirements.txt").write_text("""
fastapi==0.104.1
sqlalchemy==2.0.23
redis==5.0.1
psycopg2-binary==2.9.9
""")

            (project_path / "docker-compose.yml").write_text("""
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/app
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
  
  redis:
    image: redis:7-alpine
""")

            (project_path / "README.md").write_text("""
# Complex API Project

A FastAPI application with PostgreSQL and Redis integration.

## Features
- REST API endpoints
- Database integration
- Caching with Redis
- Docker support
""")

            # Mock workflow generation for complex project
            complex_workflows = [
                {
                    "name": "Database Backup Workflow",
                    "category": "database",
                    "nodes": ["scheduleTrigger", "postgres", "httpRequest"],
                },
                {
                    "name": "API Health Check Workflow",
                    "category": "monitoring",
                    "nodes": ["scheduleTrigger", "httpRequest", "function"],
                },
                {
                    "name": "Cache Cleanup Workflow",
                    "category": "maintenance",
                    "nodes": ["scheduleTrigger", "redis", "function"],
                },
            ]

            pipeline_coordinator.workflow_generator.generate_workflows = AsyncMock(
                return_value=complex_workflows
            )

            # Execute pipeline
            result = await pipeline_coordinator.execute_pipeline(
                project_path=project_path,
                request_id="complex-project-test",
                user_id="test-user",
            )

            # Verify results for complex project
            assert result.success is True
            assert len(result.workflows) == 3

            # Verify that complex project analysis was performed
            project_analysis = result.context.stage_results.get("project_analysis")
            assert project_analysis is not None
            assert project_analysis["complexity_score"] > 0.5  # Should be more complex
            assert (
                project_analysis["automation_potential"] > 0.5
            )  # Should have high automation potential

            # Verify technologies were detected
            technologies = project_analysis.get("technologies", [])
            tech_names = [tech["name"] for tech in technologies]
            assert "fastapi" in tech_names
            assert "postgresql" in tech_names
            assert "redis" in tech_names
            assert "docker" in tech_names
