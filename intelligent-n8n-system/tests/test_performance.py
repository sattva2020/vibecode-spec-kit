"""
Performance and load testing
"""

import pytest
import asyncio
import time
import tempfile
import statistics
from pathlib import Path
from unittest.mock import AsyncMock, patch
import psutil
import gc


@pytest.mark.performance
@pytest.mark.slow
class TestPerformance:
    """Performance and load tests"""

    @pytest.fixture
    def large_project_structure(self):
        """Create a large project structure for performance testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "large_project"
            project_path.mkdir(parents=True, exist_ok=True)

            # Create multiple directories and files
            for i in range(10):  # 10 subdirectories
                subdir = project_path / f"module_{i}"
                subdir.mkdir(parents=True, exist_ok=True)

                for j in range(20):  # 20 files per subdirectory
                    file_path = subdir / f"file_{j}.py"
                    file_path.write_text(f"""
import asyncio
import json
from typing import Dict, List, Optional
from pathlib import Path

class Module{i}Class{j}:
    def __init__(self):
        self.data = {{"module": {i}, "file": {j}}}
    
    async def process_data(self, data: Dict) -> Dict:
        await asyncio.sleep(0.001)  # Simulate some work
        return {{"processed": True, "original": data}}
    
    def validate_input(self, input_data: str) -> bool:
        return len(input_data) > 0 and input_data.isalnum()

def function_{i}_{j}(param1: str, param2: int = 42) -> str:
    return f"{{param1}}_{{param2}}"

async def async_function_{i}_{j}():
    await asyncio.sleep(0.001)
    return "async_result"
""")

            # Create configuration files
            (project_path / "requirements.txt").write_text(
                "\n".join([f"package{i}==1.0.{i}" for i in range(50)])
            )

            (project_path / "pyproject.toml").write_text("""
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "large-project"
version = "1.0.0"
dependencies = [
    "fastapi>=0.100.0",
    "sqlalchemy>=2.0.0",
    "redis>=5.0.0",
    "pydantic>=2.0.0",
    "httpx>=0.25.0",
    "asyncio>=3.4.3",
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "flake8>=6.0.0"
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
""")

            yield project_path

    @pytest.mark.asyncio
    async def test_project_analysis_performance(
        self, large_project_structure, test_config
    ):
        """Test project analysis performance with large projects"""
        from src.analyzers.project_analyzer import ProjectAnalyzer

        analyzer = ProjectAnalyzer()

        # Measure analysis time
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        analysis = await analyzer.analyze_project(large_project_structure)

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        analysis_time = end_time - start_time
        memory_usage = end_memory - start_memory

        # Verify performance requirements
        assert analysis_time < 30.0, (
            f"Analysis took {analysis_time:.2f}s, should be < 30s"
        )
        assert memory_usage < 500.0, (
            f"Memory usage {memory_usage:.2f}MB, should be < 500MB"
        )

        # Verify analysis results
        assert len(analysis.file_analyses) > 100  # Should analyze many files
        assert analysis.complexity_score > 0.0
        assert analysis.automation_potential > 0.0

        print(f"Project Analysis Performance:")
        print(f"  Files analyzed: {len(analysis.file_analyses)}")
        print(f"  Analysis time: {analysis_time:.2f}s")
        print(f"  Memory usage: {memory_usage:.2f}MB")
        print(f"  Files per second: {len(analysis.file_analyses) / analysis_time:.2f}")

    @pytest.mark.asyncio
    async def test_pipeline_execution_performance(
        self, large_project_structure, test_config
    ):
        """Test complete pipeline execution performance"""
        from src.core.pipeline_coordinator import PipelineCoordinator

        coordinator = PipelineCoordinator()

        # Mock all services for performance testing
        coordinator.set_project_analyzer(AsyncMock())
        coordinator.set_knowledge_service(AsyncMock())
        coordinator.set_decision_engine(AsyncMock())
        coordinator.set_workflow_generator(AsyncMock())
        coordinator.set_validator(AsyncMock())

        # Mock service responses
        coordinator.project_analyzer.analyze_project = AsyncMock(
            return_value={
                "project_name": "large_project",
                "technologies": [],
                "complexity_score": 0.8,
            }
        )
        coordinator.knowledge_service.query_relevant_knowledge = AsyncMock(
            return_value={"nodes": [], "patterns": [], "confidence": 0.8}
        )
        coordinator.decision_engine.make_decisions = AsyncMock(
            return_value={"workflows": [], "confidence": 0.8}
        )
        coordinator.workflow_generator.generate_workflows = AsyncMock(return_value=[])
        coordinator.validator.validate_workflows = AsyncMock(
            return_value={"valid": True}
        )

        # Measure pipeline execution time
        start_time = time.time()

        result = await coordinator.execute_pipeline(
            project_path=large_project_structure,
            request_id="performance-test",
            user_id="test-user",
        )

        end_time = time.time()
        execution_time = end_time - start_time

        # Verify performance requirements
        assert execution_time < 60.0, (
            f"Pipeline execution took {execution_time:.2f}s, should be < 60s"
        )
        assert result.success is True

        print(f"Pipeline Execution Performance:")
        print(f"  Execution time: {execution_time:.2f}s")
        print(f"  Success: {result.success}")
        print(f"  Confidence: {result.confidence_score}")

    @pytest.mark.asyncio
    async def test_concurrent_pipeline_executions(
        self, large_project_structure, test_config
    ):
        """Test concurrent pipeline executions"""
        from src.core.pipeline_coordinator import PipelineCoordinator

        # Create multiple coordinators
        coordinators = []
        for i in range(5):
            coordinator = PipelineCoordinator()
            coordinator.set_project_analyzer(AsyncMock())
            coordinator.set_knowledge_service(AsyncMock())
            coordinator.set_decision_engine(AsyncMock())
            coordinator.set_workflow_generator(AsyncMock())
            coordinator.set_validator(AsyncMock())

            # Mock services
            coordinator.project_analyzer.analyze_project = AsyncMock(
                return_value={
                    "project_name": f"project_{i}",
                    "technologies": [],
                    "complexity_score": 0.5,
                }
            )
            coordinator.knowledge_service.query_relevant_knowledge = AsyncMock(
                return_value={"nodes": [], "patterns": [], "confidence": 0.8}
            )
            coordinator.decision_engine.make_decisions = AsyncMock(
                return_value={"workflows": [], "confidence": 0.8}
            )
            coordinator.workflow_generator.generate_workflows = AsyncMock(
                return_value=[]
            )
            coordinator.validator.validate_workflows = AsyncMock(
                return_value={"valid": True}
            )

            coordinators.append(coordinator)

        # Execute concurrent pipelines
        start_time = time.time()

        tasks = [
            coordinator.execute_pipeline(
                project_path=large_project_structure,
                request_id=f"concurrent-test-{i}",
                user_id="test-user",
            )
            for i, coordinator in enumerate(coordinators)
        ]

        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # Verify all executions succeeded
        assert len(results) == 5
        assert all(result.success for result in results)

        # Verify performance under load
        assert total_time < 120.0, (
            f"Concurrent execution took {total_time:.2f}s, should be < 120s"
        )

        print(f"Concurrent Pipeline Performance:")
        print(f"  Concurrent executions: {len(results)}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Average time per execution: {total_time / len(results):.2f}s")

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, large_project_structure, test_config):
        """Test memory usage under load"""
        from src.analyzers.project_analyzer import ProjectAnalyzer

        analyzer = ProjectAnalyzer()

        # Measure memory usage during multiple analyses
        memory_measurements = []

        for i in range(10):  # Run 10 analyses
            gc.collect()  # Force garbage collection
            memory_before = psutil.Process().memory_info().rss / 1024 / 1024  # MB

            # Create a copy of the project structure for each analysis
            with tempfile.TemporaryDirectory() as temp_dir:
                test_project = Path(temp_dir) / f"test_project_{i}"
                test_project.mkdir(parents=True, exist_ok=True)
                (test_project / "main.py").write_text("print('test')")

                analysis = await analyzer.analyze_project(test_project)

            gc.collect()  # Force garbage collection
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB

            memory_usage = memory_after - memory_before
            memory_measurements.append(memory_usage)

        # Verify memory usage is reasonable
        avg_memory_usage = statistics.mean(memory_measurements)
        max_memory_usage = max(memory_measurements)

        assert avg_memory_usage < 50.0, (
            f"Average memory usage {avg_memory_usage:.2f}MB too high"
        )
        assert max_memory_usage < 100.0, (
            f"Max memory usage {max_memory_usage:.2f}MB too high"
        )

        print(f"Memory Usage Under Load:")
        print(f"  Average memory usage: {avg_memory_usage:.2f}MB")
        print(f"  Max memory usage: {max_memory_usage:.2f}MB")
        print(f"  Memory measurements: {memory_measurements}")

    @pytest.mark.asyncio
    async def test_api_response_times(self, test_config):
        """Test API response times"""
        from fastapi.testclient import TestClient
        from src.main import app

        client = TestClient(app)

        # Test various API endpoints
        endpoints = [
            ("/health", "GET"),
            ("/api/v1/status", "GET"),
            ("/api/v1/workflows", "GET"),
            ("/api/v1/projects", "GET"),
        ]

        response_times = []

        for endpoint, method in endpoints:
            start_time = time.time()

            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})

            end_time = time.time()
            response_time = end_time - start_time

            response_times.append(
                {
                    "endpoint": endpoint,
                    "method": method,
                    "response_time": response_time,
                    "status_code": response.status_code,
                }
            )

        # Verify response times
        for result in response_times:
            assert result["response_time"] < 5.0, (
                f"Endpoint {result['endpoint']} took {result['response_time']:.2f}s, should be < 5s"
            )

        avg_response_time = statistics.mean(
            [r["response_time"] for r in response_times]
        )

        print(f"API Response Times:")
        for result in response_times:
            print(
                f"  {result['method']} {result['endpoint']}: {result['response_time']:.3f}s"
            )
        print(f"  Average response time: {avg_response_time:.3f}s")

    @pytest.mark.asyncio
    async def test_database_query_performance(self, test_config):
        """Test database query performance"""
        from src.integrations.supabase_client import SupabaseClient

        # Mock Supabase client for performance testing
        with patch("src.integrations.supabase_client.create_client") as mock_create:
            mock_client = AsyncMock()
            mock_create.return_value = mock_client

            # Mock query responses
            mock_client.table.return_value.select.return_value.execute.return_value = {
                "data": [{"id": i, "name": f"item_{i}"} for i in range(1000)]
            }

            client = SupabaseClient(
                test_config.supabase.url, test_config.supabase.anon_key
            )

            # Test query performance
            query_times = []

            for i in range(10):  # Run 10 queries
                start_time = time.time()

                result = await client.query_table("test_table", {"limit": 1000})

                end_time = time.time()
                query_time = end_time - start_time
                query_times.append(query_time)

            # Verify query performance
            avg_query_time = statistics.mean(query_times)
            max_query_time = max(query_times)

            assert avg_query_time < 2.0, (
                f"Average query time {avg_query_time:.3f}s too slow"
            )
            assert max_query_time < 5.0, (
                f"Max query time {max_query_time:.3f}s too slow"
            )

            print(f"Database Query Performance:")
            print(f"  Average query time: {avg_query_time:.3f}s")
            print(f"  Max query time: {max_query_time:.3f}s")

    @pytest.mark.asyncio
    async def test_workflow_generation_performance(self, test_config):
        """Test workflow generation performance"""
        from src.generators.workflow_generator import WorkflowGenerator

        generator = WorkflowGenerator()

        # Mock decision data
        decisions = {
            "workflow_decisions": [
                {
                    "workflow_type": f"workflow_{i}",
                    "decision": "create",
                    "confidence": 0.9,
                    "suggested_nodes": ["trigger", "httpRequest", "function"],
                    "suggested_connections": [
                        {"from": "trigger", "to": "httpRequest"},
                        {"from": "httpRequest", "to": "function"},
                    ],
                }
                for i in range(50)  # Generate 50 workflows
            ],
            "confidence": 0.85,
        }

        # Mock project analysis
        project_analysis = {
            "project_name": "test_project",
            "technologies": [],
            "complexity_score": 0.5,
        }

        # Measure generation time
        start_time = time.time()

        workflows = await generator.generate_workflows(decisions, project_analysis)

        end_time = time.time()
        generation_time = end_time - start_time

        # Verify performance
        assert generation_time < 10.0, (
            f"Workflow generation took {generation_time:.2f}s, should be < 10s"
        )
        assert len(workflows) == 50

        workflows_per_second = len(workflows) / generation_time

        print(f"Workflow Generation Performance:")
        print(f"  Workflows generated: {len(workflows)}")
        print(f"  Generation time: {generation_time:.2f}s")
        print(f"  Workflows per second: {workflows_per_second:.2f}")

    @pytest.mark.asyncio
    async def test_stress_testing(self, large_project_structure, test_config):
        """Stress test the system under high load"""
        from src.core.pipeline_coordinator import PipelineCoordinator

        # Create multiple coordinators for stress testing
        coordinators = []
        for i in range(20):  # 20 concurrent coordinators
            coordinator = PipelineCoordinator()
            coordinator.set_project_analyzer(AsyncMock())
            coordinator.set_knowledge_service(AsyncMock())
            coordinator.set_decision_engine(AsyncMock())
            coordinator.set_workflow_generator(AsyncMock())
            coordinator.set_validator(AsyncMock())

            # Mock services with realistic delays
            coordinator.project_analyzer.analyze_project = AsyncMock(
                return_value={
                    "project_name": f"stress_project_{i}",
                    "technologies": [],
                    "complexity_score": 0.7,
                }
            )
            coordinator.knowledge_service.query_relevant_knowledge = AsyncMock(
                return_value={"nodes": [], "patterns": [], "confidence": 0.8}
            )
            coordinator.decision_engine.make_decisions = AsyncMock(
                return_value={"workflows": [], "confidence": 0.8}
            )
            coordinator.workflow_generator.generate_workflows = AsyncMock(
                return_value=[]
            )
            coordinator.validator.validate_workflows = AsyncMock(
                return_value={"valid": True}
            )

            coordinators.append(coordinator)

        # Execute stress test
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        tasks = [
            coordinator.execute_pipeline(
                project_path=large_project_structure,
                request_id=f"stress-test-{i}",
                user_id="test-user",
            )
            for i, coordinator in enumerate(coordinators)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

        total_time = end_time - start_time
        memory_usage = end_memory - start_memory

        # Analyze results
        successful_results = [
            r for r in results if not isinstance(r, Exception) and r.success
        ]
        failed_results = [
            r for r in results if isinstance(r, Exception) or not r.success
        ]

        success_rate = len(successful_results) / len(results) * 100

        # Verify stress test results
        assert success_rate >= 80.0, (
            f"Success rate {success_rate:.1f}% too low, should be >= 80%"
        )
        assert total_time < 300.0, (
            f"Stress test took {total_time:.2f}s, should be < 300s"
        )
        assert memory_usage < 1000.0, f"Memory usage {memory_usage:.2f}MB too high"

        print(f"Stress Test Results:")
        print(f"  Total executions: {len(results)}")
        print(f"  Successful: {len(successful_results)}")
        print(f"  Failed: {len(failed_results)}")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Memory usage: {memory_usage:.2f}MB")
        print(f"  Executions per second: {len(results) / total_time:.2f}")
