"""
Knowledge Service для AI Router
Интеграция с граф-базой знаний для умных рекомендаций
"""

import asyncio
import structlog
from typing import Dict, List, Any, Optional
import httpx

from ..config import Settings
from ..models import AIRequest, AIResponse, ProviderType, TaskType

logger = structlog.get_logger()


class KnowledgeService:
    """Сервис для работы с граф-базой знаний"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = "http://intelligent-n8n-api:8000"  # URL к intelligent n8n API
        self.session = httpx.AsyncClient(timeout=30.0)

    async def initialize(self):
        """Инициализация сервиса"""
        logger.info("Knowledge service initialized")

    async def close(self):
        """Закрытие сервиса"""
        await self.session.aclose()

    async def get_technology_recommendations(
        self, project_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Получение рекомендаций технологий на основе контекста проекта"""
        try:
            logger.info("Getting technology recommendations", context=project_context)

            response = await self.session.post(
                f"{self.base_url}/knowledge/recommendations", json=project_context
            )

            if response.status_code == 200:
                recommendations = response.json()
                logger.info(
                    "Technology recommendations received", count=len(recommendations)
                )
                return recommendations
            else:
                logger.error(
                    "Failed to get recommendations", status_code=response.status_code
                )
                return []

        except Exception as e:
            logger.error("Failed to get technology recommendations", error=str(e))
            return []

    async def get_n8n_workflow_suggestions(
        self, technologies: List[str]
    ) -> List[Dict[str, Any]]:
        """Получение предложений n8n workflow на основе технологий"""
        try:
            logger.info("Getting n8n workflow suggestions", technologies=technologies)

            response = await self.session.post(
                f"{self.base_url}/knowledge/workflow-suggestions",
                json={"technologies": technologies},
            )

            if response.status_code == 200:
                suggestions = response.json()
                logger.info("Workflow suggestions received", count=len(suggestions))
                return suggestions
            else:
                logger.error(
                    "Failed to get workflow suggestions",
                    status_code=response.status_code,
                )
                return []

        except Exception as e:
            logger.error("Failed to get workflow suggestions", error=str(e))
            return []

    async def search_technologies(
        self, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Поиск технологий в граф-базе знаний"""
        try:
            logger.info("Searching technologies", query=query, limit=limit)

            response = await self.session.get(
                f"{self.base_url}/knowledge/search",
                params={"query": query, "limit": limit},
            )

            if response.status_code == 200:
                results = response.json()
                logger.info("Technology search completed", results_count=len(results))
                return results
            else:
                logger.error(
                    "Failed to search technologies", status_code=response.status_code
                )
                return []

        except Exception as e:
            logger.error("Failed to search technologies", error=str(e))
            return []

    async def get_technology_details(
        self, technology_name: str
    ) -> Optional[Dict[str, Any]]:
        """Получение детальной информации о технологии"""
        try:
            logger.info("Getting technology details", technology=technology_name)

            response = await self.session.get(
                f"{self.base_url}/knowledge/technology/{technology_name}"
            )

            if response.status_code == 200:
                details = response.json()
                logger.info("Technology details received", technology=technology_name)
                return details
            else:
                logger.error(
                    "Failed to get technology details",
                    technology=technology_name,
                    status_code=response.status_code,
                )
                return None

        except Exception as e:
            logger.error(
                "Failed to get technology details",
                technology=technology_name,
                error=str(e),
            )
            return None

    async def enrich_ai_response(
        self, ai_response: AIResponse, context: Dict[str, Any]
    ) -> AIResponse:
        """Обогащение AI ответа знаниями из граф-базы"""
        try:
            logger.info("Enriching AI response with knowledge")

            # Извлекаем технологии из контекста
            technologies = context.get("technologies", [])

            if technologies:
                # Получаем рекомендации технологий
                recommendations = await self.get_technology_recommendations(context)

                # Получаем предложения n8n workflow
                workflow_suggestions = await self.get_n8n_workflow_suggestions(
                    technologies
                )

                # Обогащаем метаданные ответа
                enriched_metadata = ai_response.metadata.copy()
                enriched_metadata.update(
                    {
                        "technology_recommendations": recommendations,
                        "n8n_workflow_suggestions": workflow_suggestions,
                        "knowledge_enriched": True,
                    }
                )

                # Создаем обогащенный ответ
                enriched_response = AIResponse(
                    content=ai_response.content,
                    provider=ai_response.provider,
                    model=ai_response.model,
                    task_type=ai_response.task_type,
                    duration=ai_response.duration,
                    tokens_used=ai_response.tokens_used,
                    confidence=ai_response.confidence,
                    metadata=enriched_metadata,
                    error=ai_response.error,
                )

                logger.info("AI response enriched with knowledge")
                return enriched_response

            return ai_response

        except Exception as e:
            logger.error("Failed to enrich AI response", error=str(e))
            return ai_response

    async def generate_technology_insights(
        self, project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Генерация инсайтов о технологиях для проекта"""
        try:
            logger.info("Generating technology insights", context=project_context)

            insights = {
                "recommended_technologies": [],
                "workflow_patterns": [],
                "integration_opportunities": [],
                "complexity_assessment": {},
                "best_practices": [],
            }

            # Получаем рекомендации технологий
            recommendations = await self.get_technology_recommendations(project_context)
            insights["recommended_technologies"] = recommendations

            # Получаем предложения workflow
            technologies = project_context.get("technologies", [])
            if technologies:
                workflow_suggestions = await self.get_n8n_workflow_suggestions(
                    technologies
                )
                insights["workflow_patterns"] = workflow_suggestions

            # Анализируем возможности интеграции
            integration_opportunities = []
            for tech in technologies:
                details = await self.get_technology_details(tech)
                if details and details.get("n8n_integrations"):
                    integration_opportunities.append(
                        {
                            "technology": tech,
                            "n8n_integrations": details["n8n_integrations"],
                            "integration_complexity": details.get(
                                "complexity_level", "unknown"
                            ),
                        }
                    )

            insights["integration_opportunities"] = integration_opportunities

            # Оцениваем сложность
            complexity_scores = []
            for tech in technologies:
                details = await self.get_technology_details(tech)
                if details:
                    complexity_scores.append(
                        {
                            "technology": tech,
                            "complexity": details.get("complexity_level", "unknown"),
                            "popularity": details.get("popularity_score", 0.0),
                        }
                    )

            insights["complexity_assessment"] = {
                "technologies": complexity_scores,
                "overall_complexity": self._calculate_overall_complexity(
                    complexity_scores
                ),
            }

            logger.info("Technology insights generated successfully")
            return insights

        except Exception as e:
            logger.error("Failed to generate technology insights", error=str(e))
            return {}

    def _calculate_overall_complexity(
        self, complexity_scores: List[Dict[str, Any]]
    ) -> str:
        """Вычисление общей сложности проекта"""
        if not complexity_scores:
            return "unknown"

        complexity_mapping = {"low": 1, "medium": 2, "high": 3}
        scores = []

        for item in complexity_scores:
            complexity = item.get("complexity", "unknown")
            if complexity in complexity_mapping:
                scores.append(complexity_mapping[complexity])

        if not scores:
            return "unknown"

        avg_score = sum(scores) / len(scores)

        if avg_score <= 1.5:
            return "low"
        elif avg_score <= 2.5:
            return "medium"
        else:
            return "high"

    async def check_health(self) -> bool:
        """Проверка здоровья сервиса"""
        try:
            response = await self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error("Knowledge service health check failed", error=str(e))
            return False
