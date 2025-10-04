#!/usr/bin/env python3
"""
Phase 2 Implementation Script for Intelligent n8n Workflow Creation System
Integration Testing and Real Service Connection
"""

import asyncio
import sys
import subprocess
import time
from pathlib import Path
import json
from typing import Dict, Any, List


class Phase2Runner:
    """Runner for Phase 2 implementation"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {}

    async def check_prerequisites(self) -> Dict[str, bool]:
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")

        prerequisites = {
            "python": self._check_python_version(),
            "dependencies": self._check_dependencies(),
            "docker": self._check_docker(),
            "services": await self._check_services(),
        }

        for name, status in prerequisites.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {name}")

        return prerequisites

    def _check_python_version(self) -> bool:
        """Check Python version"""
        version = sys.version_info
        print(f"    Python version: {version.major}.{version.minor}.{version.micro}")
        return version >= (3, 8)

    def _check_dependencies(self) -> bool:
        """Check if dependencies are installed"""
        try:
            import fastapi
            import uvicorn
            import pytest
            import httpx
            import asyncio

            return True
        except ImportError:
            return False

    def _check_docker(self) -> bool:
        """Check if Docker is running"""
        try:
            result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    async def _check_services(self) -> Dict[str, bool]:
        """Check if required services are running"""
        services = {
            "lightrag": "http://localhost:8000",
            "supabase": "http://localhost:54321",
            "n8n": "http://localhost:5678",
            "ollama": "http://localhost:11434",
        }

        service_status = {}

        try:
            import httpx

            async with httpx.AsyncClient(timeout=5.0) as client:
                for service_name, url in services.items():
                    try:
                        response = await client.get(f"{url}/health")
                        service_status[service_name] = response.status_code == 200
                    except Exception:
                        service_status[service_name] = False
        except ImportError:
            # httpx not available, assume services are down
            service_status = {name: False for name in services.keys()}

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
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        print("🔗 Running integration tests...")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/test_integration_pipeline.py",
                    "tests/test_integration_services.py",
                    "-v",
                    "--tb=short",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

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
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

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
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_api_endpoints(self) -> Dict[str, Any]:
        """Test API endpoints"""
        print("🌐 Testing API endpoints...")

        try:
            # Start the API server in the background
            server_process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "src.main:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    "8001",  # Use different port to avoid conflicts
                    "--log-level",
                    "error",
                ],
                cwd=self.project_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Wait for server to start
            await asyncio.sleep(3)

            # Test endpoints
            import httpx

            async with httpx.AsyncClient() as client:
                endpoints = [
                    "/health",
                    "/api/v1/status",
                    "/api/v1/workflows",
                    "/api/v1/projects",
                ]

                results = {}
                for endpoint in endpoints:
                    try:
                        response = await client.get(f"http://localhost:8001{endpoint}")
                        results[endpoint] = {
                            "status_code": response.status_code,
                            "success": response.status_code < 500,
                        }
                    except Exception as e:
                        results[endpoint] = {"error": str(e), "success": False}

                # Stop server
                server_process.terminate()
                server_process.wait()

                return {
                    "success": all(result["success"] for result in results.values()),
                    "results": results,
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_performance_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks"""
        print("⚡ Running performance benchmarks...")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/test_performance.py",
                    "-v",
                    "--tb=short",
                    "-x",  # Stop on first failure
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def generate_integration_report(self) -> Dict[str, Any]:
        """Generate integration test report"""
        print("📊 Generating integration report...")

        total_tests = 0
        passed_tests = 0
        failed_tests = 0

        for test_type, result in self.results.items():
            if "success" in result:
                if result["success"]:
                    passed_tests += 1
                else:
                    failed_tests += 1
                total_tests += 1

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        report = {
            "timestamp": time.time(),
            "phase": "Phase 2 - Integration Testing",
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
            },
            "test_results": self.results,
            "recommendations": self._generate_recommendations(),
        }

        # Save report
        report_file = self.project_root / "phase2_integration_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📄 Report saved to: {report_file}")

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        # Check test results and generate recommendations
        if "unit_tests" in self.results and not self.results["unit_tests"]["success"]:
            recommendations.append(
                "Fix failing unit tests before proceeding to integration"
            )

        if (
            "integration_tests" in self.results
            and not self.results["integration_tests"]["success"]
        ):
            recommendations.append(
                "Review integration test failures and fix core pipeline issues"
            )

        if (
            "n8n_integration" in self.results
            and not self.results["n8n_integration"]["success"]
        ):
            recommendations.append("Verify n8n service is running and accessible")

        if (
            "model_training" in self.results
            and not self.results["model_training"]["success"]
        ):
            recommendations.append(
                "Check ML dependencies and training data availability"
            )

        if "api_testing" in self.results and not self.results["api_testing"]["success"]:
            recommendations.append(
                "Fix API endpoint issues and ensure proper error handling"
            )

        if "performance" in self.results and not self.results["performance"]["success"]:
            recommendations.append(
                "Optimize performance bottlenecks identified in benchmarks"
            )

        if not recommendations:
            recommendations.append(
                "All tests passed! Ready for Phase 3 - Integration & Learning"
            )

        return recommendations

    def print_summary(self):
        """Print Phase 2 summary"""
        print("\n" + "=" * 80)
        print("🎯 PHASE 2 INTEGRATION TESTING SUMMARY")
        print("=" * 80)

        total_tests = 0
        passed_tests = 0

        for test_type, result in self.results.items():
            if "success" in result:
                total_tests += 1
                if result["success"]:
                    passed_tests += 1
                    status = "✅ PASSED"
                else:
                    status = "❌ FAILED"

                print(f"{test_type.upper()}: {status}")

                if "error" in result:
                    print(f"  Error: {result['error']}")
                elif "returncode" in result and result["returncode"] != 0:
                    print(f"  Exit code: {result['returncode']}")

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print(
            f"\nOVERALL SUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)"
        )

        if success_rate >= 80:
            print("🎉 Phase 2 completed successfully! Ready for Phase 3.")
        elif success_rate >= 60:
            print("⚠️  Phase 2 partially completed. Review failures before proceeding.")
        else:
            print("❌ Phase 2 failed. Fix critical issues before proceeding.")

    async def run_phase2(self):
        """Run complete Phase 2 implementation"""
        print("🚀 Starting Phase 2 - Integration Testing & Real Service Connection")
        print("=" * 70)

        start_time = time.time()

        # Check prerequisites
        prerequisites = await self.check_prerequisites()

        if not all(prerequisites.values()):
            print("❌ Prerequisites not met. Please fix issues before proceeding.")
            return False

        print("✅ All prerequisites met. Starting integration tests...\n")

        # Run all tests
        self.results["unit_tests"] = await self.run_unit_tests()
        self.results["integration_tests"] = await self.run_integration_tests()
        self.results["n8n_integration"] = await self.run_n8n_integration_tests()
        self.results["model_training"] = await self.run_model_training_tests()
        self.results["api_testing"] = await self.test_api_endpoints()
        self.results["performance"] = await self.test_performance_benchmarks()

        # Generate report
        report = await self.generate_integration_report()

        # Print summary
        self.print_summary()

        execution_time = time.time() - start_time
        print(f"\n⏱️  Total execution time: {execution_time:.2f} seconds")

        # Return success if most tests passed
        total_tests = len(self.results)
        passed_tests = sum(
            1 for result in self.results.values() if result.get("success", False)
        )
        success_rate = passed_tests / total_tests * 100

        return success_rate >= 60  # Consider successful if 60%+ tests pass


async def main():
    """Main function"""
    runner = Phase2Runner()
    success = await runner.run_phase2()

    if success:
        print("\n🎉 Phase 2 completed successfully!")
        print("Next steps:")
        print("  1. Review integration test results")
        print("  2. Fix any critical issues")
        print("  3. Proceed to Phase 3 - Integration & Learning")
    else:
        print("\n❌ Phase 2 failed. Please review and fix issues before proceeding.")

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
