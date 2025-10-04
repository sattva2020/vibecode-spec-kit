#!/usr/bin/env python3
"""
Полный запуск RAG системы с автоматическим созданием n8n workflow'ов
"""

import asyncio
import subprocess
import sys
import os
import time
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cli.services.n8n_workflow_manager import N8nWorkflowManager, create_rag_workflows
from cli.utils.output import OutputFormatter


class RAGSystemManager:
    """Менеджер для полного запуска RAG системы"""

    def __init__(self):
        self.output = OutputFormatter()
        self.project_path = Path.cwd()
        self.docker_compose_file = "docker-compose-rag.yml"

    async def start_docker_services(self):
        """Запуск Docker сервисов"""
        self.output.print_header("🐳 Запуск Docker сервисов")

        try:
            # Проверяем наличие docker-compose файла
            if not Path(self.docker_compose_file).exists():
                self.output.print_error(f"❌ Файл {self.docker_compose_file} не найден")
                return False

            # Запускаем сервисы
            self.output.print_info("Запуск Docker Compose...")
            result = subprocess.run(
                ["docker-compose", "-f", self.docker_compose_file, "up", "-d"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.output.print_success("✅ Docker сервисы запущены успешно")
                return True
            else:
                self.output.print_error(f"❌ Ошибка запуска Docker: {result.stderr}")
                return False

        except Exception as e:
            self.output.print_error(f"❌ Ошибка запуска Docker сервисов: {e}")
            return False

    async def wait_for_services(self, timeout=300):
        """Ожидание готовности сервисов"""
        self.output.print_header("⏳ Ожидание готовности сервисов")

        services_to_check = [
            ("RAG Proxy", "http://localhost:9000/health"),
            ("n8n", "http://localhost:5678/healthz"),
            ("LightRAG", "http://localhost:8000/health"),
        ]

        for service_name, health_url in services_to_check:
            self.output.print_info(f"Проверка {service_name}...")

            if await self._wait_for_service(health_url, timeout=60):
                self.output.print_success(f"✅ {service_name} готов")
            else:
                self.output.print_warning(f"⚠️ {service_name} не отвечает (продолжаем)")

    async def _wait_for_service(self, url, timeout=60):
        """Ожидание готовности конкретного сервиса"""
        import httpx

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=5.0)
                    if response.status_code == 200:
                        return True
            except:
                pass

            await asyncio.sleep(5)

        return False

    async def create_n8n_workflows(self):
        """Создание n8n workflow'ов"""
        self.output.print_header("🔄 Создание n8n workflow'ов")

        try:
            n8n_config = {
                "url": "http://localhost:5678",
                "username": "admin",
                "password": "admin123",
            }

            # Ждем готовности n8n
            self.output.print_info("Ожидание готовности n8n...")
            if not await self._wait_for_service(
                n8n_config["url"] + "/healthz", timeout=120
            ):
                self.output.print_error(
                    "❌ n8n не готов, пропускаем создание workflow'ов"
                )
                return False

            # Создаем workflow'ы
            success = await create_rag_workflows(str(self.project_path), n8n_config)

            if success:
                self.output.print_success("✅ n8n workflow'ы созданы успешно!")
                return True
            else:
                self.output.print_error("❌ Не удалось создать n8n workflow'ы")
                return False

        except Exception as e:
            self.output.print_error(f"❌ Ошибка создания workflow'ов: {e}")
            return False

    async def test_system_integration(self):
        """Тестирование интеграции системы"""
        self.output.print_header("🧪 Тестирование интеграции системы")

        try:
            # Тестируем RAG команды
            test_commands = [
                ["python", "memory-bank-cli.py", "rag", "status"],
                ["python", "memory-bank-cli.py", "rag", "list-workflows"],
            ]

            for cmd in test_commands:
                self.output.print_info(f"Выполнение: {' '.join(cmd)}")

                result = subprocess.run(
                    cmd, capture_output=True, text=True, cwd=self.project_path
                )

                if result.returncode == 0:
                    self.output.print_success(f"✅ {' '.join(cmd)} - успешно")
                else:
                    self.output.print_warning(
                        f"⚠️ {' '.join(cmd)} - ошибка: {result.stderr}"
                    )

            return True

        except Exception as e:
            self.output.print_error(f"❌ Ошибка тестирования: {e}")
            return False

    async def show_system_status(self):
        """Показ статуса системы"""
        self.output.print_header("📊 Статус RAG системы")

        self.output.print_info("🌐 Доступные сервисы:")
        self.output.print_info("  • RAG Proxy API: http://localhost:9000")
        self.output.print_info("  • n8n UI: http://localhost:5678")
        self.output.print_info("  • LightRAG API: http://localhost:8000")
        self.output.print_info("  • PostgreSQL: localhost:5432")

        self.output.print_info("\n🔧 Доступные команды:")
        self.output.print_info("  • python memory-bank-cli.py rag status")
        self.output.print_info("  • python memory-bank-cli.py rag setup-workflows")
        self.output.print_info("  • python memory-bank-cli.py rag list-workflows")
        self.output.print_info(
            "  • python memory-bank-cli.py rag suggest --code 'const user = '"
        )

        self.output.print_info("\n📖 Документация:")
        self.output.print_info("  • RAG_INTEGRATION.md - интеграция с Spec Kit")
        self.output.print_info("  • RAG_INTEGRATION_REPORT.md - отчет о реализации")

    async def run_full_setup(self):
        """Полная настройка и запуск RAG системы"""
        self.output.print_header("🚀 Полный запуск RAG системы")

        try:
            # 1. Запуск Docker сервисов
            if not await self.start_docker_services():
                return False

            # 2. Ожидание готовности сервисов
            await self.wait_for_services()

            # 3. Создание n8n workflow'ов
            await self.create_n8n_workflows()

            # 4. Тестирование интеграции
            await self.test_system_integration()

            # 5. Показ статуса
            await self.show_system_status()

            self.output.print_success("🎉 RAG система полностью запущена и настроена!")
            return True

        except Exception as e:
            self.output.print_error(f"❌ Ошибка запуска системы: {e}")
            return False


async def main():
    """Главная функция"""
    manager = RAGSystemManager()

    print("🤖 RAG-Powered Code Assistant: Vibecode Spec Kit Integration")
    print("=" * 70)

    success = await manager.run_full_setup()

    if success:
        print("\n✅ Система готова к использованию!")
        print("💡 Откройте VS Code в корневой директории проекта для полной интеграции")
    else:
        print("\n❌ Ошибка запуска системы")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
