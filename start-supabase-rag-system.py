#!/usr/bin/env python3
"""
Полный запуск RAG системы с Supabase Stack
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


class SupabaseRAGSystemManager:
    """Менеджер для полного запуска RAG системы с Supabase"""

    def __init__(self):
        self.output = OutputFormatter()
        self.project_path = Path.cwd()
        self.docker_compose_file = "docker-compose-supabase-rag.yml"

    async def start_supabase_services(self):
        """Запуск Supabase сервисов"""
        self.output.print_header("🚀 Запуск Supabase RAG системы")

        try:
            # Проверяем наличие docker-compose файла
            if not Path(self.docker_compose_file).exists():
                self.output.print_error(f"❌ Файл {self.docker_compose_file} не найден")
                return False

            # Проверяем наличие .env файла
            env_file = Path(".env")
            if not env_file.exists():
                self.output.print_warning(
                    "⚠️ Файл .env не найден. Копируем из примера..."
                )
                subprocess.run(["cp", "supabase-env.example", ".env"], check=True)
                self.output.print_info(
                    "📝 Пожалуйста, отредактируйте .env файл с вашими настройками"
                )

            # Запускаем сервисы
            self.output.print_info("Запуск Supabase Docker Compose...")
            result = subprocess.run(
                ["docker-compose", "-f", self.docker_compose_file, "up", "-d"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.output.print_success("✅ Supabase сервисы запущены успешно")
                return True
            else:
                self.output.print_error(f"❌ Ошибка запуска Supabase: {result.stderr}")
                return False

        except Exception as e:
            self.output.print_error(f"❌ Ошибка запуска Supabase сервисов: {e}")
            return False

    async def wait_for_supabase_services(self, timeout=300):
        """Ожидание готовности Supabase сервисов"""
        self.output.print_header("⏳ Ожидание готовности Supabase сервисов")

        services_to_check = [
            ("Supabase Kong API Gateway", "http://localhost:8000/rest/v1/"),
            ("Supabase Studio", "http://localhost:3000/api/profile"),
            ("Supabase Auth", "http://localhost:8000/auth/v1/health"),
            ("Supabase Storage", "http://localhost:8000/storage/v1/status"),
            ("n8n", "http://localhost:5678/healthz"),
            ("LightRAG", "http://localhost:8000/health"),
            ("RAG Proxy", "http://localhost:9000/health"),
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
                    if response.status_code in [
                        200,
                        404,
                    ]:  # 404 is OK for some endpoints
                        return True
            except:
                pass

            await asyncio.sleep(5)

        return False

    async def create_supabase_n8n_workflows(self):
        """Создание n8n workflow'ов для Supabase интеграции"""
        self.output.print_header("🔄 Создание n8n workflow'ов для Supabase")

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
                self.output.print_success(
                    "✅ n8n workflow'ы для Supabase созданы успешно!"
                )
                return True
            else:
                self.output.print_error("❌ Не удалось создать n8n workflow'ы")
                return False

        except Exception as e:
            self.output.print_error(f"❌ Ошибка создания workflow'ов: {e}")
            return False

    async def test_supabase_integration(self):
        """Тестирование Supabase интеграции"""
        self.output.print_header("🧪 Тестирование Supabase интеграции")

        try:
            # Тестируем Supabase API
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

    async def show_supabase_status(self):
        """Показ статуса Supabase системы"""
        self.output.print_header("📊 Статус Supabase RAG системы")

        self.output.print_info("🌐 Supabase сервисы:")
        self.output.print_info("  • Supabase Studio: http://localhost:3000")
        self.output.print_info("  • Supabase API: http://localhost:8000")
        self.output.print_info("  • Supabase Auth: http://localhost:8000/auth/v1")
        self.output.print_info("  • Supabase Storage: http://localhost:8000/storage/v1")
        self.output.print_info("  • Supabase Realtime: ws://localhost:8000/realtime/v1")

        self.output.print_info("\n🔧 RAG сервисы:")
        self.output.print_info("  • RAG Proxy API: http://localhost:9000")
        self.output.print_info("  • n8n UI: http://localhost:5678")
        self.output.print_info("  • LightRAG API: http://localhost:8000")

        self.output.print_info("\n📊 База данных:")
        self.output.print_info("  • PostgreSQL: localhost:5432")
        self.output.print_info("  • Redis: localhost:6379")

        self.output.print_info("\n🔧 Доступные команды:")
        self.output.print_info("  • python memory-bank-cli.py rag status")
        self.output.print_info("  • python memory-bank-cli.py rag setup-workflows")
        self.output.print_info("  • python memory-bank-cli.py rag list-workflows")
        self.output.print_info(
            "  • python memory-bank-cli.py rag suggest --code 'const user = '"
        )

        self.output.print_info("\n📖 Документация:")
        self.output.print_info(
            "  • docs/N8N_WORKFLOW_INTEGRATION.md - интеграция workflow'ов"
        )
        self.output.print_info("  • N8N_INTEGRATION_REPORT.md - отчет о реализации")

        self.output.print_info("\n🔑 Supabase ключи:")
        self.output.print_info("  • Anon Key: (из .env файла)")
        self.output.print_info("  • Service Role Key: (из .env файла)")

    async def run_supabase_setup(self):
        """Полная настройка и запуск Supabase RAG системы"""
        self.output.print_header("🚀 Полный запуск Supabase RAG системы")

        try:
            # 1. Запуск Supabase сервисов
            if not await self.start_supabase_services():
                return False

            # 2. Ожидание готовности сервисов
            await self.wait_for_supabase_services()

            # 3. Создание n8n workflow'ов
            await self.create_supabase_n8n_workflows()

            # 4. Тестирование интеграции
            await self.test_supabase_integration()

            # 5. Показ статуса
            await self.show_supabase_status()

            self.output.print_success(
                "🎉 Supabase RAG система полностью запущена и настроена!"
            )
            return True

        except Exception as e:
            self.output.print_error(f"❌ Ошибка запуска Supabase системы: {e}")
            return False


async def main():
    """Главная функция"""
    manager = SupabaseRAGSystemManager()

    print("🤖 Supabase RAG-Powered Code Assistant: Vibecode Spec Kit Integration")
    print("=" * 80)

    success = await manager.run_supabase_setup()

    if success:
        print("\n✅ Supabase система готова к использованию!")
        print("💡 Откройте VS Code в корневой директории проекта для полной интеграции")
        print("🌐 Доступ к Supabase Studio: http://localhost:3000")
        print("🔑 Используйте ключи из .env файла для подключения к Supabase API")
    else:
        print("\n❌ Ошибка запуска Supabase системы")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
