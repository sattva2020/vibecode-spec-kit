#!/usr/bin/env python3
"""
Integration test runner for Intelligent n8n Workflow Creation System
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
import argparse
import json
from typing import List, Dict, Any


class IntegrationTestRunner:
    """Runner for integration tests"""

    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()

    async def check_docker_services(self) -> Dict[str, bool]:
        """Check if Docker services are running"""
        services = {
            "lightrag": "http://localhost:8000",
            "supabase": "http://localhost:54321",
            "n8n": "http://localhost:5678",
            "ollama": "http://localhost:11434",
        }

        service_status = {}

        for service_name, url in services.items():
            try:
                import httpx

                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{url}/health")
                    service_status[service_name] = response.status_code == 200
            except Exception:
                service_status[service_name] = False

        return service_status

    async def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests"""
        print("🧪 Running unit tests...")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/",
                    "-m",
                    "unit",
                    "-v",
                    "--tb=short",
                    "--json-report",
                    "--json-report-file=unit_test_results.json",
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent,
            )

            success = result.returncode == 0

            # Try to read JSON report
            json_file = Path("unit_test_results.json")
            if json_file.exists():
                with open(json_file, "r") as f:
                    report = json.load(f)
            else:
                report = {"summary": {"total": 0, "passed": 0, "failed": 0}}

            return {
                "success": success,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "report": report,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "returncode": -1}

    async def run_integration_tests(
        self, docker_required: bool = False
    ) -> Dict[str, Any]:
        """Run integration tests"""
        print("🔗 Running integration tests...")

        test_args = [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-m",
            "integration",
            "-v",
            "--tb=short",
            "--json-report",
            "--json-report-file=integration_test_results.json",
        ]

        if docker_required:
            test_args.extend(["-m", "docker"])

        try:
            result = subprocess.run(
                test_args, capture_output=True, text=True, cwd=Path(__file__).parent
            )

            success = result.returncode == 0

            # Try to read JSON report
            json_file = Path("integration_test_results.json")
            if json_file.exists():
                with open(json_file, "r") as f:
                    report = json.load(f)
            else:
                report = {"summary": {"total": 0, "passed": 0, "failed": 0}}

            return {
                "success": success,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "report": report,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "returncode": -1}

    async def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        print("⚡ Running performance tests...")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/",
                    "-m",
                    "performance",
                    "-v",
                    "--tb=short",
                    "--json-report",
                    "--json-report-file=performance_test_results.json",
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent,
            )

            success = result.returncode == 0

            # Try to read JSON report
            json_file = Path("performance_test_results.json")
            if json_file.exists():
                with open(json_file, "r") as f:
                    report = json.load(f)
            else:
                report = {"summary": {"total": 0, "passed": 0, "failed": 0}}

            return {
                "success": success,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "report": report,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "returncode": -1}

    async def run_n8n_integration_tests(self) -> Dict[str, Any]:
        """Run n8n integration tests"""
        print("🔌 Running n8n integration tests...")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/test_n8n_integration.py",
                    "-v",
                    "--tb=short",
                    "--json-report",
                    "--json-report-file=n8n_test_results.json",
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent,
            )

            success = result.returncode == 0

            # Try to read JSON report
            json_file = Path("n8n_test_results.json")
            if json_file.exists():
                with open(json_file, "r") as f:
                    report = json.load(f)
            else:
                report = {"summary": {"total": 0, "passed": 0, "failed": 0}}

            return {
                "success": success,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "report": report,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "returncode": -1}

    async def run_model_training_tests(self) -> Dict[str, Any]:
        """Run model training tests"""
        print("🤖 Running model training tests...")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/test_model_training.py",
                    "-v",
                    "--tb=short",
                    "--json-report",
                    "--json-report-file=model_training_results.json",
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent,
            )

            success = result.returncode == 0

            # Try to read JSON report
            json_file = Path("model_training_results.json")
            if json_file.exists():
                with open(json_file, "r") as f:
                    report = json.load(f)
            else:
                report = {"summary": {"total": 0, "passed": 0, "failed": 0}}

            return {
                "success": success,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "report": report,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "returncode": -1}

    def print_summary(self):
        """Print test summary"""
        total_time = time.time() - self.start_time

        print("\n" + "=" * 80)
        print("🎯 INTEGRATION TEST SUMMARY")
        print("=" * 80)

        total_tests = 0
        total_passed = 0
        total_failed = 0

        for test_type, result in self.test_results.items():
            if "report" in result and "summary" in result["report"]:
                summary = result["report"]["summary"]
                total_tests += summary.get("total", 0)
                total_passed += summary.get("passed", 0)
                total_failed += summary.get("failed", 0)

                status = "✅ PASSED" if result["success"] else "❌ FAILED"
                print(f"{test_type.upper()}: {status}")
                print(
                    f"  Tests: {summary.get('total', 0)} | Passed: {summary.get('passed', 0)} | Failed: {summary.get('failed', 0)}"
                )
            else:
                status = "✅ PASSED" if result["success"] else "❌ FAILED"
                print(f"{test_type.upper()}: {status}")
                if "error" in result:
                    print(f"  Error: {result['error']}")

        print(
            f"\nOVERALL: {total_passed}/{total_tests} tests passed ({total_passed / total_tests * 100:.1f}%)"
        )
        print(f"Total execution time: {total_time:.2f} seconds")

        if total_failed > 0:
            print(f"\n❌ {total_failed} tests failed - check logs for details")
            return False
        else:
            print(f"\n✅ All tests passed!")
            return True

    async def run_all_tests(
        self, include_docker: bool = True, include_performance: bool = False
    ):
        """Run all integration tests"""
        print("🚀 Starting Integration Test Suite")
        print("=" * 50)

        # Check Docker services
        if include_docker:
            print("🐳 Checking Docker services...")
            service_status = await self.check_docker_services()

            for service, is_running in service_status.items():
                status = "🟢 Running" if is_running else "🔴 Not running"
                print(f"  {service}: {status}")

            docker_available = any(service_status.values())
            if not docker_available:
                print("⚠️  No Docker services detected. Some tests may be skipped.")
        else:
            docker_available = False

        # Run unit tests
        self.test_results["unit_tests"] = await self.run_unit_tests()

        # Run integration tests
        self.test_results["integration_tests"] = await self.run_integration_tests(
            docker_required=False
        )

        # Run n8n integration tests if Docker is available
        if docker_available:
            self.test_results[
                "n8n_integration"
            ] = await self.run_n8n_integration_tests()
        else:
            self.test_results["n8n_integration"] = {
                "success": True,
                "skipped": True,
                "reason": "Docker services not available",
            }

        # Run model training tests
        self.test_results["model_training"] = await self.run_model_training_tests()

        # Run performance tests if requested
        if include_performance:
            self.test_results["performance_tests"] = await self.run_performance_tests()

        # Print summary
        return self.print_summary()


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Run integration tests for Intelligent n8n System"
    )
    parser.add_argument(
        "--no-docker", action="store_true", help="Skip Docker-dependent tests"
    )
    parser.add_argument(
        "--performance", action="store_true", help="Include performance tests"
    )
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration-only", action="store_true", help="Run only integration tests"
    )
    parser.add_argument(
        "--n8n-only", action="store_true", help="Run only n8n integration tests"
    )
    parser.add_argument(
        "--model-only", action="store_true", help="Run only model training tests"
    )

    args = parser.parse_args()

    runner = IntegrationTestRunner()

    if args.unit_only:
        result = await runner.run_unit_tests()
        print(
            "✅ Unit tests completed" if result["success"] else "❌ Unit tests failed"
        )
        return result["success"]

    elif args.integration_only:
        result = await runner.run_integration_tests(docker_required=not args.no_docker)
        print(
            "✅ Integration tests completed"
            if result["success"]
            else "❌ Integration tests failed"
        )
        return result["success"]

    elif args.n8n_only:
        result = await runner.run_n8n_integration_tests()
        print(
            "✅ n8n integration tests completed"
            if result["success"]
            else "❌ n8n integration tests failed"
        )
        return result["success"]

    elif args.model_only:
        result = await runner.run_model_training_tests()
        print(
            "✅ Model training tests completed"
            if result["success"]
            else "❌ Model training tests failed"
        )
        return result["success"]

    else:
        # Run all tests
        success = await runner.run_all_tests(
            include_docker=not args.no_docker, include_performance=args.performance
        )
        return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
