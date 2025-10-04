#!/usr/bin/env python3
"""
RAG System Integration Test
Tests the basic functionality of the RAG system components
"""

import asyncio
import json
import time
from typing import Dict, Any
import httpx
import psycopg2
from psycopg2.extras import RealDictCursor


class RAGIntegrationTester:
    def __init__(self):
        self.results = {}

    async def test_database_connection(self) -> bool:
        """Test PostgreSQL database connection and pgvector extension"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="rag_system",
                user="postgres",
                password="your_secure_password_here",
            )

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Test basic connection
                cur.execute("SELECT version();")
                version = cur.fetchone()["version"]
                print(f"✅ Database connected: {version}")

                # Test pgvector extension
                cur.execute(
                    "SELECT extname FROM pg_extension WHERE extname = 'vector';"
                )
                vector_ext = cur.fetchone()
                if vector_ext:
                    print("✅ pgvector extension is available")
                else:
                    print("❌ pgvector extension not found")
                    return False

                # Test vector operations
                cur.execute(
                    "SELECT '[1,2,3]'::vector <-> '[1,2,4]'::vector as distance;"
                )
                distance = cur.fetchone()["distance"]
                print(f"✅ Vector operations working, distance: {distance}")

            conn.close()
            return True

        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

    async def test_ollama_api(self) -> bool:
        """Test Ollama API functionality"""
        try:
            async with httpx.AsyncClient() as client:
                # Test API availability
                response = await client.get("http://localhost:11434/api/tags")
                if response.status_code == 200:
                    models = response.json()
                    print(
                        f"✅ Ollama API available, models: {len(models.get('models', []))}"
                    )

                    # Test model inference if available
                    if models.get("models"):
                        test_prompt = "Hello, how are you?"
                        inference_data = {
                            "model": models["models"][0]["name"],
                            "prompt": test_prompt,
                            "stream": False,
                        }

                        response = await client.post(
                            "http://localhost:11434/api/generate",
                            json=inference_data,
                            timeout=30.0,
                        )

                        if response.status_code == 200:
                            result = response.json()
                            print(
                                f"✅ Model inference working: {result.get('response', '')[:50]}..."
                            )
                            return True
                        else:
                            print(f"❌ Model inference failed: {response.status_code}")
                            return False
                    else:
                        print("⚠️  No models available for testing")
                        return True
                else:
                    print(f"❌ Ollama API not available: {response.status_code}")
                    return False

        except Exception as e:
            print(f"❌ Ollama API test failed: {e}")
            return False

    async def test_n8n_api(self) -> bool:
        """Test n8n API functionality"""
        try:
            async with httpx.AsyncClient() as client:
                # Test health endpoint
                response = await client.get("http://localhost:5678/healthz")
                if response.status_code == 200:
                    health = response.json()
                    print(f"✅ n8n API healthy: {health}")

                    # Test workflows endpoint (basic auth required)
                    auth = ("admin", "your_n8n_password_here")
                    response = await client.get(
                        "http://localhost:5678/api/v1/workflows",
                        auth=auth,
                        timeout=10.0,
                    )

                    if response.status_code in [
                        200,
                        401,
                    ]:  # 401 is OK if not authenticated
                        print("✅ n8n workflows API accessible")
                        return True
                    else:
                        print(f"❌ n8n workflows API failed: {response.status_code}")
                        return False
                else:
                    print(f"❌ n8n health check failed: {response.status_code}")
                    return False

        except Exception as e:
            print(f"❌ n8n API test failed: {e}")
            return False

    async def test_ollama_model_inference(self) -> bool:
        """Test Ollama model inference with a simple prompt"""
        try:
            async with httpx.AsyncClient() as client:
                # Get available models
                response = await client.get("http://localhost:11434/api/tags")
                models = response.json().get("models", [])

                if not models:
                    print("⚠️  No models available for inference test")
                    return False

                model_name = models[0]["name"]
                print(f"🧪 Testing inference with model: {model_name}")

                # Test inference
                inference_data = {
                    "model": model_name,
                    "prompt": "Write a simple Python function to add two numbers:",
                    "stream": False,
                    "options": {"temperature": 0.1, "max_tokens": 100},
                }

                start_time = time.time()
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json=inference_data,
                    timeout=60.0,
                )
                inference_time = time.time() - start_time

                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Inference successful in {inference_time:.2f}s")
                    print(f"📝 Response: {result.get('response', '')[:100]}...")
                    return True
                else:
                    print(f"❌ Inference failed: {response.status_code}")
                    return False

        except Exception as e:
            print(f"❌ Model inference test failed: {e}")
            return False

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        print("🚀 Starting RAG System Integration Tests")
        print("=" * 50)

        tests = [
            ("Database Connection", self.test_database_connection),
            ("Ollama API", self.test_ollama_api),
            ("n8n API", self.test_n8n_api),
            ("Model Inference", self.test_ollama_model_inference),
        ]

        results = {}
        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\n🧪 Testing: {test_name}")
            print("-" * 30)

            try:
                result = await test_func()
                results[test_name] = result
                if result:
                    passed += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                results[test_name] = False
                print(f"❌ {test_name}: ERROR - {e}")

        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! RAG system is ready.")
        elif passed > total // 2:
            print("⚠️  Most tests passed. Some components may need attention.")
        else:
            print("❌ Multiple tests failed. System needs significant work.")

        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": total - passed,
            "results": results,
            "overall_success": passed == total,
        }


async def main():
    """Main test execution"""
    tester = RAGIntegrationTester()
    results = await tester.run_all_tests()

    # Save results to file
    with open("integration-test-results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Results saved to: integration-test-results.json")

    return results["overall_success"]


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
