"""
Cursor IDE API Client
Интеграция с Cursor IDE для использования платных подписок
"""

import httpx
import asyncio
import structlog
from typing import Dict, Any, Optional, List
import time
import os

from ..config import Settings
from ..models import AIRequest, AIResponse, ProviderType, TaskType

logger = structlog.get_logger()


class CursorAPIClient:
    """Клиент для работы с Cursor IDE API"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_key = settings.cursor_api_key
        self.base_url = settings.cursor_api_url or "https://api.cursor.sh/v1"
        self.session_id: Optional[str] = None
        self.session_name = settings.cursor_session_name or "n8n-ai-router"
        self.fallback_mode = False

        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "n8n-ai-router/1.0.0",
            },
        )

    async def initialize(self) -> bool:
        """Инициализация клиента и создание терминальной сессии"""
        try:
            if not self.api_key:
                logger.warning("Cursor API key not provided, using fallback mode")
                self.fallback_mode = True
                return False

            # Создаем терминальную сессию
            self.session_id = await self._create_terminal_session()
            if self.session_id:
                logger.info("Cursor API client initialized", session_id=self.session_id)
                return True
            else:
                logger.error("Failed to create Cursor terminal session")
                self.fallback_mode = True
                return False

        except Exception as e:
            logger.error("Failed to initialize Cursor API client", error=str(e))
            self.fallback_mode = True
            return False

    async def _create_terminal_session(self) -> Optional[str]:
        """Создает отдельную терминальную сессию для n8n"""
        try:
            response = await self.http_client.post(
                f"{self.base_url}/sessions/terminal",
                json={
                    "name": self.session_name,
                    "type": "automation",
                    "description": "AI Router для n8n workflow'ов",
                    "metadata": {
                        "purpose": "n8n_workflow_creation",
                        "version": "1.0.0",
                    },
                },
            )

            if response.status_code == 200:
                data = response.json()
                session_id = data.get("session_id")
                logger.info("Cursor terminal session created", session_id=session_id)
                return session_id
            else:
                logger.error(
                    "Failed to create Cursor session",
                    status_code=response.status_code,
                    response=response.text,
                )
                return None

        except Exception as e:
            logger.error("Error creating Cursor session", error=str(e))
            return None

    async def analyze_for_n8n(self, request: AIRequest) -> AIResponse:
        """Анализ проекта для n8n через Cursor"""
        if self.fallback_mode:
            raise Exception("Cursor API not available, fallback mode active")

        try:
            start_time = time.time()

            # Строим промпт для n8n анализа
            prompt = self._build_n8n_prompt(request)

            # Отправляем запрос в Cursor
            response = await self.http_client.post(
                f"{self.base_url}/sessions/{self.session_id}/chat",
                json={
                    "messages": [
                        {"role": "system", "content": self._get_n8n_system_prompt()},
                        {"role": "user", "content": prompt},
                    ],
                    "model": "claude-3.5-sonnet",  # Используем вашу подписку
                    "temperature": 0.1,
                    "max_tokens": 4096,
                    "stream": False,
                },
            )

            if response.status_code == 200:
                data = response.json()
                content = (
                    data.get("choices", [{}])[0].get("message", {}).get("content", "")
                )

                duration = time.time() - start_time

                # Парсим ответ для n8n
                parsed_response = self._parse_n8n_response(content, request)

                return AIResponse(
                    content=parsed_response["content"],
                    provider=ProviderType.CURSOR,
                    model="claude-3.5-sonnet",
                    task_type=request.task_type,
                    duration=duration,
                    tokens_used=data.get("usage", {}).get("total_tokens"),
                    confidence=parsed_response.get("confidence", 0.9),
                    metadata=parsed_response.get("metadata", {}),
                )
            else:
                logger.error(
                    "Cursor API request failed",
                    status_code=response.status_code,
                    response=response.text,
                )
                raise Exception(f"Cursor API error: {response.status_code}")

        except Exception as e:
            logger.error("Cursor n8n analysis failed", error=str(e))
            raise Exception(f"Cursor analysis failed: {str(e)}")

    async def generate_code(self, request: AIRequest) -> AIResponse:
        """Генерация кода через Cursor"""
        if self.fallback_mode:
            raise Exception("Cursor API not available, fallback mode active")

        try:
            start_time = time.time()

            response = await self.http_client.post(
                f"{self.base_url}/sessions/{self.session_id}/chat",
                json={
                    "messages": [
                        {
                            "role": "system",
                            "content": "Ты эксперт по программированию. Генерируй качественный код.",
                        },
                        {"role": "user", "content": request.prompt},
                    ],
                    "model": "gpt-4-turbo",  # Используем GPT-4 для кода
                    "temperature": 0.2,
                    "max_tokens": 2048,
                    "stream": False,
                },
            )

            if response.status_code == 200:
                data = response.json()
                content = (
                    data.get("choices", [{}])[0].get("message", {}).get("content", "")
                )
                duration = time.time() - start_time

                return AIResponse(
                    content=content,
                    provider=ProviderType.CURSOR,
                    model="gpt-4-turbo",
                    task_type=request.task_type,
                    duration=duration,
                    tokens_used=data.get("usage", {}).get("total_tokens"),
                    confidence=0.9,
                    metadata={"language": self._detect_language(content)},
                )
            else:
                raise Exception(
                    f"Cursor code generation failed: {response.status_code}"
                )

        except Exception as e:
            logger.error("Cursor code generation failed", error=str(e))
            raise Exception(f"Cursor code generation failed: {str(e)}")

    def _build_n8n_prompt(self, request: AIRequest) -> str:
        """Строит промпт для n8n анализа"""
        context = request.context

        prompt = f"""
Анализируй проект для создания n8n workflow'ов:

**Контекст проекта:**
- Путь: {context.get("project_path", "не указан")}
- Технологии: {", ".join(context.get("technologies", []))}
- Архитектура: {context.get("architecture", "не указана")}
- Задача: {request.task_type}

**Требования:**
1. Проанализируй структуру проекта
2. Определи возможности для автоматизации
3. Предложи n8n workflow'ы
4. Укажи необходимые API интеграции
5. Оцени сложность реализации

**Ответ должен содержать:**
- Анализ архитектуры
- Рекомендуемые workflow'ы
- Список необходимых n8n узлов
- План интеграции
- Оценку сложности (1-10)
"""

        if request.prompt:
            prompt += f"\n\n**Дополнительные требования:**\n{request.prompt}"

        return prompt

    def _get_n8n_system_prompt(self) -> str:
        """Системный промпт для n8n анализа"""
        return """
Ты эксперт по n8n workflow automation и архитектуре программных систем.

Твоя задача:
1. Анализировать проекты и предлагать автоматизацию через n8n
2. Создавать детальные планы workflow'ов
3. Рекомендовать подходящие n8n узлы и интеграции
4. Оценивать сложность и приоритеты задач

Всегда отвечай в структурированном формате с четкими рекомендациями.
"""

    def _parse_n8n_response(self, content: str, request: AIRequest) -> Dict[str, Any]:
        """Парсит ответ от Cursor для n8n"""
        try:
            # Простой парсинг - в реальности можно использовать более сложную логику
            lines = content.split("\n")

            workflow_suggestions = []
            api_recommendations = []
            complexity_score = 5  # По умолчанию

            current_section = None

            for line in lines:
                line = line.strip()

                if "workflow" in line.lower() or "автоматизация" in line.lower():
                    workflow_suggestions.append(line)
                elif "api" in line.lower() or "интеграция" in line.lower():
                    api_recommendations.append(line)
                elif "сложность" in line.lower():
                    # Пытаемся извлечь оценку сложности
                    import re

                    numbers = re.findall(r"\d+", line)
                    if numbers:
                        complexity_score = min(10, max(1, int(numbers[0])))

            return {
                "content": content,
                "confidence": 0.9,
                "metadata": {
                    "workflow_suggestions": workflow_suggestions[:5],
                    "api_recommendations": api_recommendations[:5],
                    "complexity_score": complexity_score,
                    "analysis_type": "n8n_workflow_creation",
                },
            }

        except Exception as e:
            logger.error("Failed to parse n8n response", error=str(e))
            return {
                "content": content,
                "confidence": 0.7,
                "metadata": {"error": "parsing_failed"},
            }

    def _detect_language(self, content: str) -> str:
        """Определяет язык программирования в коде"""
        if "```python" in content or "def " in content:
            return "python"
        elif "```javascript" in content or "function " in content:
            return "javascript"
        elif "```typescript" in content or "interface " in content:
            return "typescript"
        elif "```rust" in content or "fn " in content:
            return "rust"
        elif "```go" in content or "func " in content:
            return "go"
        else:
            return "unknown"

    async def check_health(self) -> bool:
        """Проверка доступности Cursor API"""
        try:
            if self.fallback_mode:
                return False

            response = await self.http_client.get(f"{self.base_url}/health")
            return response.status_code == 200

        except Exception as e:
            logger.error("Cursor health check failed", error=str(e))
            return False

    async def close(self):
        """Закрытие клиента"""
        if self.session_id:
            try:
                await self.http_client.delete(
                    f"{self.base_url}/sessions/{self.session_id}"
                )
                logger.info("Cursor session closed", session_id=self.session_id)
            except Exception as e:
                logger.error("Failed to close Cursor session", error=str(e))

        await self.http_client.aclose()
