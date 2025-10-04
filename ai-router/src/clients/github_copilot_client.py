"""
GitHub Copilot API Client
Интеграция с GitHub Copilot для использования платных подписок
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


class GitHubCopilotAPIClient:
    """Клиент для работы с GitHub Copilot API"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_key = settings.github_copilot_api_key
        self.base_url = (
            settings.github_copilot_api_url or "https://api.githubcopilot.com/v1"
        )
        self.session_id: Optional[str] = None
        self.session_name = settings.github_copilot_session_name or "n8n-ai-router"
        self.fallback_mode = False

        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "n8n-ai-router/1.0.0",
                "X-GitHub-Api-Version": "2023-07-07",
            },
        )

    async def initialize(self) -> bool:
        """Инициализация клиента"""
        try:
            if not self.api_key:
                logger.warning(
                    "GitHub Copilot API key not provided, using fallback mode"
                )
                self.fallback_mode = True
                return False

            # Проверяем доступность Copilot API
            health_check = await self.check_health()
            if health_check:
                logger.info("GitHub Copilot API client initialized successfully")
                return True
            else:
                logger.error("GitHub Copilot API not available")
                self.fallback_mode = True
                return False

        except Exception as e:
            logger.error("Failed to initialize GitHub Copilot API client", error=str(e))
            self.fallback_mode = True
            return False

    async def analyze_for_n8n(self, request: AIRequest) -> AIResponse:
        """Анализ проекта для n8n через GitHub Copilot"""
        if self.fallback_mode:
            raise Exception("GitHub Copilot API not available, fallback mode active")

        try:
            start_time = time.time()

            # Строим промпт для n8n анализа
            prompt = self._build_n8n_prompt(request)

            # Отправляем запрос в Copilot
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": "copilot-chat",  # GitHub Copilot Chat модель
                    "messages": [
                        {"role": "system", "content": self._get_n8n_system_prompt()},
                        {"role": "user", "content": prompt},
                    ],
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
                    provider=ProviderType.GITHUB_COPILOT,
                    model="copilot-chat",
                    task_type=request.task_type,
                    duration=duration,
                    tokens_used=data.get("usage", {}).get("total_tokens"),
                    confidence=parsed_response.get("confidence", 0.9),
                    metadata=parsed_response.get("metadata", {}),
                )
            else:
                logger.error(
                    "GitHub Copilot API request failed",
                    status_code=response.status_code,
                    response=response.text,
                )
                raise Exception(f"GitHub Copilot API error: {response.status_code}")

        except Exception as e:
            logger.error("GitHub Copilot n8n analysis failed", error=str(e))
            raise Exception(f"GitHub Copilot analysis failed: {str(e)}")

    async def generate_code(self, request: AIRequest) -> AIResponse:
        """Генерация кода через GitHub Copilot"""
        if self.fallback_mode:
            raise Exception("GitHub Copilot API not available, fallback mode active")

        try:
            start_time = time.time()

            # Строим контекст для генерации кода
            context = request.context

            response = await self.http_client.post(
                f"{self.base_url}/completions",
                json={
                    "model": "copilot-codex",  # GitHub Copilot Codex модель
                    "prompt": request.prompt,
                    "context": {
                        "language": context.get("language", "python"),
                        "framework": context.get("framework", ""),
                        "project_type": context.get("project_type", "general"),
                    },
                    "temperature": 0.2,
                    "max_tokens": 2048,
                    "stream": False,
                },
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("text", "")
                duration = time.time() - start_time

                return AIResponse(
                    content=content,
                    provider=ProviderType.GITHUB_COPILOT,
                    model="copilot-codex",
                    task_type=request.task_type,
                    duration=duration,
                    tokens_used=data.get("usage", {}).get("total_tokens"),
                    confidence=0.9,
                    metadata={
                        "language": context.get("language", "unknown"),
                        "framework": context.get("framework", ""),
                        "generation_type": "code_completion",
                    },
                )
            else:
                raise Exception(
                    f"GitHub Copilot code generation failed: {response.status_code}"
                )

        except Exception as e:
            logger.error("GitHub Copilot code generation failed", error=str(e))
            raise Exception(f"GitHub Copilot code generation failed: {str(e)}")

    async def suggest_n8n_nodes(self, project_context: Dict[str, Any]) -> AIResponse:
        """Предложения n8n узлов на основе контекста проекта"""
        if self.fallback_mode:
            raise Exception("GitHub Copilot API not available, fallback mode active")

        try:
            start_time = time.time()

            prompt = self._build_n8n_nodes_prompt(project_context)

            response = await self.http_client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": "copilot-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Ты эксперт по n8n workflow automation. Предлагай подходящие n8n узлы для автоматизации.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.1,
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
                    provider=ProviderType.GITHUB_COPILOT,
                    model="copilot-chat",
                    task_type=TaskType.WORKFLOW_CREATION,
                    duration=duration,
                    tokens_used=data.get("usage", {}).get("total_tokens"),
                    confidence=0.9,
                    metadata={
                        "suggestions_type": "n8n_nodes",
                        "project_technologies": project_context.get("technologies", []),
                        "analysis_type": "node_recommendation",
                    },
                )
            else:
                raise Exception(
                    f"GitHub Copilot n8n suggestions failed: {response.status_code}"
                )

        except Exception as e:
            logger.error("GitHub Copilot n8n suggestions failed", error=str(e))
            raise Exception(f"GitHub Copilot n8n suggestions failed: {str(e)}")

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
2. Определи возможности для автоматизации через n8n
3. Предложи конкретные workflow'ы
4. Укажи необходимые n8n узлы
5. Оцени сложность реализации

**Ответ должен содержать:**
- Анализ архитектуры проекта
- Рекомендуемые n8n workflow'ы
- Список необходимых n8n узлов
- План интеграции
- Оценку сложности (1-10)
"""

        if request.prompt:
            prompt += f"\n\n**Дополнительные требования:**\n{request.prompt}"

        return prompt

    def _build_n8n_nodes_prompt(self, project_context: Dict[str, Any]) -> str:
        """Строит промпт для предложения n8n узлов"""
        technologies = project_context.get("technologies", [])
        architecture = project_context.get("architecture", "не указана")

        prompt = f"""
Предложи подходящие n8n узлы для автоматизации проекта:

**Технологии проекта:**
{", ".join(technologies)}

**Архитектура:**
{architecture}

**Задача:**
Предложи конкретные n8n узлы, которые помогут автоматизировать этот проект.

**Ответ должен содержать:**
1. Список рекомендуемых n8n узлов
2. Объяснение зачем нужен каждый узел
3. Порядок подключения узлов
4. Примеры конфигурации
"""

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
Используй знание популярных технологий и их интеграций с n8n.
"""

    def _parse_n8n_response(self, content: str, request: AIRequest) -> Dict[str, Any]:
        """Парсит ответ от GitHub Copilot для n8n"""
        try:
            lines = content.split("\n")

            workflow_suggestions = []
            api_recommendations = []
            node_recommendations = []
            complexity_score = 5

            for line in lines:
                line = line.strip()

                if "workflow" in line.lower() or "автоматизация" in line.lower():
                    workflow_suggestions.append(line)
                elif "api" in line.lower() or "интеграция" in line.lower():
                    api_recommendations.append(line)
                elif "node" in line.lower() or "узел" in line.lower():
                    node_recommendations.append(line)
                elif "сложность" in line.lower():
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
                    "node_recommendations": node_recommendations[:5],
                    "complexity_score": complexity_score,
                    "analysis_type": "n8n_workflow_creation",
                    "provider": "github_copilot",
                },
            }

        except Exception as e:
            logger.error("Failed to parse GitHub Copilot response", error=str(e))
            return {
                "content": content,
                "confidence": 0.7,
                "metadata": {"error": "parsing_failed", "provider": "github_copilot"},
            }

    async def check_health(self) -> bool:
        """Проверка доступности GitHub Copilot API"""
        try:
            if self.fallback_mode:
                return False

            # Проверяем доступность через простой запрос
            response = await self.http_client.get(f"{self.base_url}/models")
            return response.status_code == 200

        except Exception as e:
            logger.error("GitHub Copilot health check failed", error=str(e))
            return False

    async def get_available_models(self) -> List[str]:
        """Получение доступных моделей GitHub Copilot"""
        try:
            response = await self.http_client.get(f"{self.base_url}/models")
            if response.status_code == 200:
                data = response.json()
                return [model.get("id") for model in data.get("data", [])]
            return []
        except Exception as e:
            logger.error("Failed to get GitHub Copilot models", error=str(e))
            return []

    async def close(self):
        """Закрытие клиента"""
        await self.http_client.aclose()
