"""
RAG Integration Commands for Vibecode Spec Kit
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
import httpx
from ..core.memory_bank import MemoryBank
from ..utils.output import OutputFormatter
from ..services.n8n_workflow_manager import N8nWorkflowManager, create_rag_workflows


class RAGCommand:
    """RAG integration commands for Spec Kit"""

    def __init__(self, memory_bank: MemoryBank):
        self.memory_bank = memory_bank
        self.output = OutputFormatter()
        self.rag_proxy_url = "http://localhost:9000"
        self.lightrag_url = "http://localhost:8000"

    async def execute(self, args) -> None:
        """Execute RAG command"""
        action = args.rag_action

        if action == "status":
            await self._show_status()
        elif action == "suggest":
            await self._suggest_code(args)
        elif action == "learn":
            await self._learn_from_code(args)
        elif action == "search":
            await self._search_context(args)
        elif action == "integrate":
            await self._integrate_spec_kit(args)
        elif action == "health":
            await self._health_check()
        elif action == "setup-workflows":
            await self._setup_n8n_workflows(args)
        elif action == "list-workflows":
            await self._list_n8n_workflows()
        else:
            self.output.print_error(f"Unknown RAG action: {action}")

    async def _show_status(self) -> None:
        """Show RAG system status"""
        self.output.print_header("RAG System Status")

        try:
            # Check Memory Bank
            mb_status = await self.memory_bank.health_check()
            self.output.print_success(f"Memory Bank: {mb_status['status']}")

            # Check RAG Proxy
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(f"{self.rag_proxy_url}/health")
                    rag_status = response.json()
                    self.output.print_success(
                        f"RAG Proxy: {rag_status.get('status', 'unknown')}"
                    )

                    # Show service details
                    for service, health in rag_status.get("services", {}).items():
                        status_icon = "✅" if health == "healthy" else "❌"
                        self.output.print_text(f"  {status_icon} {service}: {health}")

                except httpx.ConnectError:
                    self.output.print_error("RAG Proxy: Not available")

            # Check LightRAG
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(f"{self.lightrag_url}/health")
                    lightrag_status = response.json()
                    self.output.print_success(
                        f"LightRAG: {lightrag_status.get('status', 'unknown')}"
                    )
                except httpx.ConnectError:
                    self.output.print_error("LightRAG: Not available")

        except Exception as e:
            self.output.print_error(f"Failed to get status: {e}")

    async def _suggest_code(self, args) -> None:
        """Get AI code suggestions"""
        file_path = getattr(args, "file_path", "unknown")
        code = getattr(args, "code", "")
        language = getattr(args, "language", "text")

        self.output.print_header("AI Code Suggestions")

        try:
            # Get Spec Kit context
            spec_context = self.memory_bank.get_rag_context("code suggestion")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.rag_proxy_url}/api/suggest",
                    json={
                        "file_path": file_path,
                        "code": code,
                        "language": language,
                        "project_context": spec_context,
                    },
                )

                if response.status_code == 200:
                    result = response.json()
                    suggestions = result.get("suggestions", [])

                    if suggestions:
                        self.output.print_success(
                            f"Found {len(suggestions)} suggestions:"
                        )
                        for i, suggestion in enumerate(suggestions, 1):
                            self.output.print_text(f"\n{i}. {suggestion['text']}")
                            self.output.print_text(
                                f"   Confidence: {suggestion['confidence']:.2f}"
                            )
                            self.output.print_text(f"   Type: {suggestion['type']}")
                            if suggestion.get("spec_kit_integration"):
                                self.output.print_text(
                                    f"   Spec Kit: {suggestion['spec_kit_integration']}"
                                )
                    else:
                        self.output.print_warning("No suggestions available")
                else:
                    self.output.print_error(
                        f"Failed to get suggestions: {response.status_code}"
                    )

        except Exception as e:
            self.output.print_error(f"Failed to get suggestions: {e}")

    async def _learn_from_code(self, args) -> None:
        """Learn from code and integrate with Spec Kit"""
        file_path = getattr(args, "file_path", "unknown")
        code = getattr(args, "code", "")
        language = getattr(args, "language", "text")

        self.output.print_header("Learning from Code")

        try:
            # Integrate with Memory Bank first
            spec_type = getattr(args, "spec_type", "general")
            integration_result = await self.memory_bank.integrate_rag_context(
                spec_type, code
            )
            self.output.print_success(f"Memory Bank: {integration_result}")

            # Send to RAG system
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.rag_proxy_url}/api/learn",
                    json={
                        "file_path": file_path,
                        "code": code,
                        "language": language,
                        "context": {
                            "spec_kit_integration": True,
                            "spec_type": spec_type,
                            "memory_bank_context": integration_result,
                        },
                    },
                )

                if response.status_code == 200:
                    result = response.json()
                    self.output.print_success(
                        f"Code learned: {result.get('message', 'Success')}"
                    )
                else:
                    self.output.print_error(
                        f"Failed to learn code: {response.status_code}"
                    )

        except Exception as e:
            self.output.print_error(f"Failed to learn from code: {e}")

    async def _search_context(self, args) -> None:
        """Search code context"""
        query = getattr(args, "query", "")

        if not query:
            self.output.print_error("Query is required for search")
            return

        self.output.print_header(f"Searching Context: {query}")

        try:
            # Get Spec Kit context for search
            spec_context = self.memory_bank.get_rag_context(query)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.rag_proxy_url}/api/context/search",
                    json={"query": query, "spec_kit_context": spec_context},
                )

                if response.status_code == 200:
                    result = response.json()
                    self.output.print_success("Search Results:")
                    self.output.print_text(json.dumps(result, indent=2))
                else:
                    self.output.print_error(f"Search failed: {response.status_code}")

        except Exception as e:
            self.output.print_error(f"Failed to search context: {e}")

    async def _integrate_spec_kit(self, args) -> None:
        """Integrate RAG with Spec Kit methodologies"""
        spec_type = getattr(args, "spec_type", "general")
        code = getattr(args, "code", "")

        self.output.print_header("Spec Kit Integration")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.rag_proxy_url}/api/spec-kit/integrate",
                    json={"spec_type": spec_type, "code": code},
                )

                if response.status_code == 200:
                    result = response.json()
                    self.output.print_success(
                        f"Integration: {result.get('integration', 'Success')}"
                    )
                    self.output.print_text(
                        f"Spec Type: {result.get('spec_type', 'unknown')}"
                    )
                    self.output.print_text(f"Status: {result.get('status', 'unknown')}")
                else:
                    self.output.print_error(
                        f"Integration failed: {response.status_code}"
                    )

        except Exception as e:
            self.output.print_error(f"Failed to integrate with Spec Kit: {e}")

    async def _health_check(self) -> None:
        """Comprehensive health check"""
        self.output.print_header("RAG Health Check")

        # Check all components
        await self._show_status()

        # Test integration
        try:
            test_result = await self.memory_bank.integrate_rag_context(
                "test", "// Test integration"
            )
            self.output.print_success(f"Integration test: {test_result}")
        except Exception as e:
            self.output.print_error(f"Integration test failed: {e}")

    async def _setup_n8n_workflows(self, args) -> None:
        """Setup n8n workflows for RAG system"""
        self.output.print_header("Setting up n8n Workflows for RAG System")

        try:
            import os

            project_path = getattr(args, "project_path", os.getcwd())

            n8n_config = {
                "url": self.rag_proxy_url.replace("9000", "5678"),  # n8n runs on 5678
                "username": "admin",  # From .env
                "password": "admin123",  # From .env
            }

            self.output.print_info(f"Project path: {project_path}")
            self.output.print_info(f"n8n URL: {n8n_config['url']}")

            # Создаем workflow'ы через API
            success = await create_rag_workflows(project_path, n8n_config)

            if success:
                self.output.print_success("✅ n8n workflows созданы успешно!")
                self.output.print_info("Доступные workflow'ы:")
                self.output.print_info(
                    "  • RAG Code Indexing - автоматическая индексация кода"
                )
                self.output.print_info(
                    "  • Spec Kit Validation - валидация по методологиям"
                )
                self.output.print_info(f"  • n8n UI: {n8n_config['url']}")
            else:
                self.output.print_error("❌ Не удалось создать n8n workflows")

        except Exception as e:
            self.output.print_error(f"Failed to setup n8n workflows: {e}")

    async def _list_n8n_workflows(self) -> None:
        """List existing n8n workflows"""
        self.output.print_header("n8n Workflows")

        try:
            manager = N8nWorkflowManager(
                n8n_url="http://localhost:5678", username="admin", password="admin123"
            )

            if await manager.authenticate():
                workflows = await manager.list_workflows()

                if workflows:
                    self.output.print_success(
                        f"✅ Найдено {len(workflows)} workflow'ов"
                    )

                    # Создаем таблицу с workflow'ами
                    headers = ["ID", "Name", "Active", "Created"]
                    rows = []

                    for workflow in workflows:
                        rows.append(
                            [
                                str(workflow.get("id", "N/A")),
                                workflow.get("name", "Unnamed"),
                                "✅" if workflow.get("active") else "❌",
                                workflow.get("createdAt", "N/A")[:10]
                                if workflow.get("createdAt")
                                else "N/A",
                            ]
                        )

                    self.output.table(headers, rows)
                else:
                    self.output.print_info("ℹ️ Workflow'ы не найдены")
            else:
                self.output.print_error("❌ Не удалось подключиться к n8n")

            await manager.close()

        except Exception as e:
            self.output.print_error(f"Failed to list n8n workflows: {e}")


# Create command instance
rag_command = RAGCommand(MemoryBank())
