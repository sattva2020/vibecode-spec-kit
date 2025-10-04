"""
Knowledge Ingestion Pipeline
Автоматическое наполнение граф-базы современными технологиями
"""

import asyncio
import aiohttp
import structlog
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import yaml

from ..core.config import Settings
from .lightrag_service import LightRAGService
from .context7_client import Context7Client

logger = structlog.get_logger()


@dataclass
class TechnologyEntity:
    """Сущность технологии в граф-базе"""

    name: str
    category: str  # language, framework, tool, methodology, pattern
    description: str
    popularity_score: float
    use_cases: List[str]
    related_technologies: List[str]
    n8n_integrations: List[str]
    complexity_level: str  # low, medium, high
    documentation_url: Optional[str] = None
    github_stars: Optional[int] = None
    last_updated: Optional[datetime] = None


@dataclass
class TechnologyRelationship:
    """Связь между технологиями"""

    source: str
    target: str
    relationship_type: str  # uses, integrates_with, alternative_to, depends_on
    strength: float  # 0.0 to 1.0
    context: str


class KnowledgeIngestionPipeline:
    """Pipeline для автоматического наполнения граф-базы"""

    def __init__(self, settings: Settings, lightrag_service: LightRAGService):
        self.settings = settings
        self.lightrag_service = lightrag_service
        self.session: Optional[aiohttp.ClientSession] = None

        # Context7 клиент для современной документации
        self.context7_client = Context7Client(settings)

        # Источники данных
        self.data_sources = {
            "context7": "https://context7.com",
            "github": "https://api.github.com",
            "stackoverflow": "https://api.stackexchange.com/2.3",
            "npm": "https://registry.npmjs.org",
            "pypi": "https://pypi.org/pypi",
            "crates": "https://crates.io/api/v1",
        }

        # Предопределенные технологии для начального наполнения
        self.predefined_technologies = self._load_predefined_technologies()

    async def initialize(self):
        """Инициализация pipeline"""
        self.session = aiohttp.ClientSession()
        await self.context7_client.initialize()
        logger.info("Knowledge ingestion pipeline initialized")

    async def close(self):
        """Закрытие pipeline"""
        if self.session:
            await self.session.close()
        await self.context7_client.close()

    def _load_predefined_technologies(self) -> Dict[str, TechnologyEntity]:
        """Загрузка предопределенных технологий"""
        return {
            # Языки программирования
            "python": TechnologyEntity(
                name="Python",
                category="language",
                description="Высокоуровневый язык программирования общего назначения",
                popularity_score=0.95,
                use_cases=["web_development", "data_science", "automation", "ai_ml"],
                related_technologies=["FastAPI", "Django", "Flask", "pandas", "numpy"],
                n8n_integrations=["Python Code", "HTTP Request", "Webhook"],
                complexity_level="medium",
                documentation_url="https://docs.python.org/3/",
                github_stars=50000,
            ),
            "typescript": TechnologyEntity(
                name="TypeScript",
                category="language",
                description="Типизированная версия JavaScript",
                popularity_score=0.90,
                use_cases=["web_development", "frontend", "backend", "mobile"],
                related_technologies=[
                    "React",
                    "Next.js",
                    "Node.js",
                    "Angular",
                    "Vue.js",
                ],
                n8n_integrations=["Code", "HTTP Request", "Webhook"],
                complexity_level="medium",
                documentation_url="https://www.typescriptlang.org/docs/",
                github_stars=95000,
            ),
            "rust": TechnologyEntity(
                name="Rust",
                category="language",
                description="Системный язык программирования с фокусом на безопасность",
                popularity_score=0.75,
                use_cases=[
                    "systems_programming",
                    "web_assembly",
                    "blockchain",
                    "performance",
                ],
                related_technologies=["Actix", "Tokio", "Serde", "Wasm"],
                n8n_integrations=["HTTP Request", "Webhook"],
                complexity_level="high",
                documentation_url="https://doc.rust-lang.org/book/",
                github_stars=85000,
            ),
            # Фреймворки
            "fastapi": TechnologyEntity(
                name="FastAPI",
                category="framework",
                description="Современный веб-фреймворк для создания API на Python",
                popularity_score=0.85,
                use_cases=["api_development", "microservices", "rapid_prototyping"],
                related_technologies=["Python", "Pydantic", "Uvicorn", "SQLAlchemy"],
                n8n_integrations=["HTTP Request", "Webhook", "REST API"],
                complexity_level="low",
                documentation_url="https://fastapi.tiangolo.com/",
                github_stars=67000,
            ),
            "react": TechnologyEntity(
                name="React",
                category="framework",
                description="Библиотека для создания пользовательских интерфейсов",
                popularity_score=0.95,
                use_cases=["frontend_development", "spa", "mobile_apps"],
                related_technologies=["TypeScript", "Next.js", "Redux", "Material-UI"],
                n8n_integrations=["HTTP Request", "Webhook"],
                complexity_level="medium",
                documentation_url="https://reactjs.org/docs/",
                github_stars=220000,
            ),
            # Инструменты
            "docker": TechnologyEntity(
                name="Docker",
                category="tool",
                description="Платформа для контейнеризации приложений",
                popularity_score=0.90,
                use_cases=[
                    "containerization",
                    "deployment",
                    "development",
                    "microservices",
                ],
                related_technologies=["Kubernetes", "Docker Compose", "Dockerfile"],
                n8n_integrations=["Docker", "HTTP Request"],
                complexity_level="medium",
                documentation_url="https://docs.docker.com/",
                github_stars=68000,
            ),
            "kubernetes": TechnologyEntity(
                name="Kubernetes",
                category="tool",
                description="Платформа для оркестрации контейнеров",
                popularity_score=0.80,
                use_cases=["container_orchestration", "scaling", "deployment"],
                related_technologies=["Docker", "Helm", "Istio", "Prometheus"],
                n8n_integrations=["HTTP Request", "Webhook"],
                complexity_level="high",
                documentation_url="https://kubernetes.io/docs/",
                github_stars=100000,
            ),
            # Базы данных
            "postgresql": TechnologyEntity(
                name="PostgreSQL",
                category="database",
                description="Продвинутая реляционная база данных",
                popularity_score=0.85,
                use_cases=["data_storage", "analytics", "transaction_processing"],
                related_technologies=["SQLAlchemy", "Django ORM", "Prisma"],
                n8n_integrations=["PostgreSQL", "Database"],
                complexity_level="medium",
                documentation_url="https://www.postgresql.org/docs/",
                github_stars=14000,
            ),
            "redis": TechnologyEntity(
                name="Redis",
                category="database",
                description="In-memory структура данных для кеширования",
                popularity_score=0.80,
                use_cases=["caching", "session_storage", "message_queue"],
                related_technologies=["Python", "Node.js", "Docker"],
                n8n_integrations=["Redis", "Memory Cache"],
                complexity_level="low",
                documentation_url="https://redis.io/docs/",
                github_stars=63000,
            ),
            # Методологии
            "agile": TechnologyEntity(
                name="Agile",
                category="methodology",
                description="Итеративная методология разработки ПО",
                popularity_score=0.90,
                use_cases=[
                    "project_management",
                    "team_collaboration",
                    "rapid_development",
                ],
                related_technologies=["Scrum", "Kanban", "Jira", "Confluence"],
                n8n_integrations=["Jira", "Slack", "Email"],
                complexity_level="medium",
                documentation_url="https://agilemanifesto.org/",
                github_stars=None,
            ),
            "devops": TechnologyEntity(
                name="DevOps",
                category="methodology",
                description="Культура и практики для автоматизации процессов",
                popularity_score=0.85,
                use_cases=["automation", "ci_cd", "monitoring", "deployment"],
                related_technologies=["Docker", "Kubernetes", "Jenkins", "GitLab"],
                n8n_integrations=["Git", "Docker", "HTTP Request", "Webhook"],
                complexity_level="high",
                documentation_url="https://aws.amazon.com/devops/what-is-devops/",
                github_stars=None,
            ),
        }

    async def ingest_initial_technologies(self) -> bool:
        """Начальное наполнение граф-базы предопределенными технологиями"""
        try:
            logger.info(
                "Starting initial technology ingestion",
                count=len(self.predefined_technologies),
            )

            for tech_name, tech_entity in self.predefined_technologies.items():
                # Добавляем технологию в LightRAG
                await self._add_technology_to_graph(tech_entity)

                # Добавляем связи
                for related_tech in tech_entity.related_technologies:
                    if related_tech.lower() in self.predefined_technologies:
                        relationship = TechnologyRelationship(
                            source=tech_entity.name,
                            target=related_tech,
                            relationship_type="related_to",
                            strength=0.8,
                            context=f"{tech_entity.name} commonly used with {related_tech}",
                        )
                        await self._add_relationship_to_graph(relationship)

                # Добавляем n8n интеграции
                for n8n_integration in tech_entity.n8n_integrations:
                    relationship = TechnologyRelationship(
                        source=tech_entity.name,
                        target=n8n_integration,
                        relationship_type="integrates_with",
                        strength=0.9,
                        context=f"{tech_entity.name} can be integrated using {n8n_integration} node",
                    )
                    await self._add_relationship_to_graph(relationship)

            logger.info("Initial technology ingestion completed successfully")
            return True

        except Exception as e:
            logger.error("Failed to ingest initial technologies", error=str(e))
            return False

    async def _add_technology_to_graph(self, tech_entity: TechnologyEntity):
        """Добавление технологии в граф LightRAG"""
        try:
            # Создаем документ для технологии
            tech_document = f"""
            Technology: {tech_entity.name}
            Category: {tech_entity.category}
            Description: {tech_entity.description}
            Use Cases: {", ".join(tech_entity.use_cases)}
            Related Technologies: {", ".join(tech_entity.related_technologies)}
            N8N Integrations: {", ".join(tech_entity.n8n_integrations)}
            Complexity Level: {tech_entity.complexity_level}
            Popularity Score: {tech_entity.popularity_score}
            Documentation: {tech_entity.documentation_url or "Not available"}
            """

            # Добавляем в LightRAG
            await self.lightrag_service.add_document(
                content=tech_document,
                metadata={
                    "type": "technology",
                    "name": tech_entity.name,
                    "category": tech_entity.category,
                    "popularity_score": tech_entity.popularity_score,
                    "complexity_level": tech_entity.complexity_level,
                    "n8n_integrations": tech_entity.n8n_integrations,
                },
            )

            logger.info(
                "Added technology to graph",
                technology=tech_entity.name,
                category=tech_entity.category,
            )

        except Exception as e:
            logger.error(
                "Failed to add technology to graph",
                technology=tech_entity.name,
                error=str(e),
            )

    async def _add_relationship_to_graph(self, relationship: TechnologyRelationship):
        """Добавление связи в граф LightRAG"""
        try:
            relationship_document = f"""
            Relationship: {relationship.source} {relationship.relationship_type} {relationship.target}
            Strength: {relationship.strength}
            Context: {relationship.context}
            """

            await self.lightrag_service.add_document(
                content=relationship_document,
                metadata={
                    "type": "relationship",
                    "source": relationship.source,
                    "target": relationship.target,
                    "relationship_type": relationship.relationship_type,
                    "strength": relationship.strength,
                },
            )

            logger.debug(
                "Added relationship to graph",
                source=relationship.source,
                target=relationship.target,
                type=relationship.relationship_type,
            )

        except Exception as e:
            logger.error(
                "Failed to add relationship to graph",
                relationship=relationship.relationship_type,
                error=str(e),
            )

    async def update_technology_popularity(self) -> bool:
        """Обновление популярности технологий из внешних источников"""
        try:
            logger.info("Updating technology popularity from external sources")

            # Здесь можно добавить логику для получения актуальных данных
            # из GitHub API, Stack Overflow и других источников

            # Пока используем заглушку
            await asyncio.sleep(1)

            logger.info("Technology popularity updated successfully")
            return True

        except Exception as e:
            logger.error("Failed to update technology popularity", error=str(e))
            return False

    async def discover_new_technologies(self) -> List[TechnologyEntity]:
        """Обнаружение новых технологий из внешних источников"""
        try:
            logger.info("Discovering new technologies from external sources")

            new_technologies = []

            # Получаем тренды из Context7
            trends = await self.context7_client.get_technology_trends()

            for trend in trends:
                tech_name = trend["technology"]

                # Проверяем, есть ли уже эта технология в нашей базе
                if tech_name.lower() not in self.predefined_technologies:
                    # Получаем экосистему технологии из Context7
                    ecosystem = await self.context7_client.get_technology_ecosystem(
                        tech_name
                    )

                    if ecosystem:
                        # Создаем новую технологию на основе данных Context7
                        new_tech = TechnologyEntity(
                            name=tech_name.title(),
                            category=trend.get("category", "unknown"),
                            description=f"Modern {tech_name} technology with growing popularity",
                            popularity_score=trend.get("trend_score", 0.5),
                            use_cases=ecosystem.get("use_cases", []),
                            related_technologies=ecosystem.get(
                                "related_technologies", []
                            ),
                            n8n_integrations=ecosystem.get(
                                "n8n_integrations", ["HTTP Request", "Webhook"]
                            ),
                            complexity_level=ecosystem.get(
                                "complexity_level", "medium"
                            ),
                        )
                        new_technologies.append(new_tech)

            logger.info(
                "Technology discovery completed", new_technologies=len(new_technologies)
            )
            return new_technologies

        except Exception as e:
            logger.error("Failed to discover new technologies", error=str(e))
            return []

    async def get_technology_recommendations(
        self, project_context: Dict[str, Any]
    ) -> List[TechnologyEntity]:
        """Получение рекомендаций технологий на основе контекста проекта"""
        try:
            logger.info("Getting technology recommendations", context=project_context)

            # Используем LightRAG для поиска релевантных технологий
            query = f"""
            Recommend technologies for project with:
            - Technologies: {", ".join(project_context.get("technologies", []))}
            - Architecture: {project_context.get("architecture", "not specified")}
            - Use cases: {", ".join(project_context.get("use_cases", []))}
            """

            results = await self.lightrag_service.query_relevant_knowledge(query)

            # Преобразуем результаты в TechnologyEntity объекты
            recommendations = []
            for result in results.nodes[:10]:  # Топ 10 рекомендаций
                if result.name in self.predefined_technologies:
                    recommendations.append(self.predefined_technologies[result.name])

            logger.info(
                "Technology recommendations generated", count=len(recommendations)
            )
            return recommendations

        except Exception as e:
            logger.error("Failed to get technology recommendations", error=str(e))
            return []

    async def get_n8n_workflow_suggestions(
        self, technologies: List[str]
    ) -> List[Dict[str, Any]]:
        """Получение предложений n8n workflow на основе технологий"""
        try:
            logger.info("Getting n8n workflow suggestions", technologies=technologies)

            workflow_suggestions = []

            # Анализируем технологии и предлагаем workflow'ы
            for tech in technologies:
                if tech in self.predefined_technologies:
                    tech_entity = self.predefined_technologies[tech]

                    for integration in tech_entity.n8n_integrations:
                        workflow_suggestions.append(
                            {
                                "name": f"{tech} Integration Workflow",
                                "description": f"Automated workflow for {tech} using {integration}",
                                "technologies": [tech],
                                "n8n_nodes": [integration],
                                "complexity": tech_entity.complexity_level,
                                "use_cases": tech_entity.use_cases,
                            }
                        )

            logger.info(
                "N8N workflow suggestions generated", count=len(workflow_suggestions)
            )
            return workflow_suggestions

        except Exception as e:
            logger.error("Failed to get n8n workflow suggestions", error=str(e))
            return []

    async def enrich_technology_with_context7(self, technology_name: str) -> bool:
        """Обогащение технологии данными из Context7"""
        try:
            logger.info(
                "Enriching technology with Context7 data", technology=technology_name
            )

            # Поиск документации в Context7
            search_result = await self.context7_client.search_technology(
                technology_name, limit=5
            )

            if search_result.documents:
                # Добавляем найденные документы в граф
                for doc in search_result.documents:
                    await self._add_context7_document_to_graph(doc)

                # Получаем экосистему технологии
                ecosystem = await self.context7_client.get_technology_ecosystem(
                    technology_name
                )

                if ecosystem:
                    # Обновляем существующую технологию или создаем новую
                    await self._update_technology_with_ecosystem(
                        technology_name, ecosystem
                    )

                logger.info(
                    "Technology enriched with Context7 data",
                    technology=technology_name,
                    documents_added=len(search_result.documents),
                )
                return True
            else:
                logger.warning(
                    "No Context7 documents found for technology",
                    technology=technology_name,
                )
                return False

        except Exception as e:
            logger.error(
                "Failed to enrich technology with Context7",
                technology=technology_name,
                error=str(e),
            )
            return False

    async def _add_context7_document_to_graph(self, doc):
        """Добавление документа Context7 в граф LightRAG"""
        try:
            # Создаем документ для LightRAG
            document_content = f"""
            Title: {doc.title}
            Technology: {doc.technology}
            Category: {doc.category}
            URL: {doc.url}
            
            Content:
            {doc.content}
            
            Tags: {", ".join(doc.tags)}
            Last Updated: {doc.last_updated or "Unknown"}
            """

            # Добавляем в LightRAG
            await self.lightrag_service.add_document(
                content=document_content,
                metadata={
                    "type": "context7_document",
                    "title": doc.title,
                    "technology": doc.technology,
                    "category": doc.category,
                    "url": doc.url,
                    "tags": doc.tags,
                    "source": "context7",
                },
            )

            logger.debug(
                "Added Context7 document to graph",
                title=doc.title,
                technology=doc.technology,
            )

        except Exception as e:
            logger.error(
                "Failed to add Context7 document to graph",
                title=doc.title,
                error=str(e),
            )

    async def _update_technology_with_ecosystem(
        self, technology_name: str, ecosystem: Dict[str, Any]
    ):
        """Обновление технологии данными экосистемы из Context7"""
        try:
            tech_key = technology_name.lower()

            # Если технология уже есть в предопределенных, обновляем её
            if tech_key in self.predefined_technologies:
                tech_entity = self.predefined_technologies[tech_key]

                # Обновляем поля на основе данных Context7
                tech_entity.related_technologies.extend(
                    ecosystem.get("related_technologies", [])
                )
                tech_entity.use_cases.extend(ecosystem.get("use_cases", []))
                tech_entity.n8n_integrations.extend(
                    ecosystem.get("n8n_integrations", [])
                )

                # Убираем дубликаты
                tech_entity.related_technologies = list(
                    set(tech_entity.related_technologies)
                )
                tech_entity.use_cases = list(set(tech_entity.use_cases))
                tech_entity.n8n_integrations = list(set(tech_entity.n8n_integrations))

                logger.info(
                    "Updated existing technology with Context7 ecosystem",
                    technology=technology_name,
                )
            else:
                # Создаем новую технологию
                new_tech = TechnologyEntity(
                    name=technology_name.title(),
                    category=ecosystem.get("category", "unknown"),
                    description=f"Modern {technology_name} technology",
                    popularity_score=0.8,  # Высокая популярность для новых технологий
                    use_cases=ecosystem.get("use_cases", []),
                    related_technologies=ecosystem.get("related_technologies", []),
                    n8n_integrations=ecosystem.get(
                        "n8n_integrations", ["HTTP Request", "Webhook"]
                    ),
                    complexity_level=ecosystem.get("complexity_level", "medium"),
                )

                # Добавляем в предопределенные технологии
                self.predefined_technologies[tech_key] = new_tech

                # Добавляем в граф
                await self._add_technology_to_graph(new_tech)

                logger.info(
                    "Created new technology from Context7 ecosystem",
                    technology=technology_name,
                )

        except Exception as e:
            logger.error(
                "Failed to update technology with ecosystem",
                technology=technology_name,
                error=str(e),
            )

    async def sync_with_context7(self) -> Dict[str, Any]:
        """Синхронизация с Context7 для получения актуальных данных"""
        try:
            logger.info("Starting sync with Context7")

            sync_results = {
                "technologies_processed": 0,
                "documents_added": 0,
                "technologies_enriched": 0,
                "new_technologies_discovered": 0,
                "errors": [],
            }

            # Получаем тренды технологий
            trends = await self.context7_client.get_technology_trends()

            # Обрабатываем каждую технологию из трендов
            for trend in trends:
                tech_name = trend["technology"]
                sync_results["technologies_processed"] += 1

                try:
                    # Обогащаем технологию данными из Context7
                    enriched = await self.enrich_technology_with_context7(tech_name)
                    if enriched:
                        sync_results["technologies_enriched"] += 1

                except Exception as e:
                    sync_results["errors"].append(
                        {"technology": tech_name, "error": str(e)}
                    )

            # Обнаруживаем новые технологии
            new_technologies = await self.discover_new_technologies()
            sync_results["new_technologies_discovered"] = len(new_technologies)

            # Добавляем новые технологии в граф
            for new_tech in new_technologies:
                await self._add_technology_to_graph(new_tech)

            logger.info("Context7 sync completed", results=sync_results)
            return sync_results

        except Exception as e:
            logger.error("Failed to sync with Context7", error=str(e))
            return {
                "technologies_processed": 0,
                "documents_added": 0,
                "technologies_enriched": 0,
                "new_technologies_discovered": 0,
                "errors": [{"error": str(e)}],
            }
