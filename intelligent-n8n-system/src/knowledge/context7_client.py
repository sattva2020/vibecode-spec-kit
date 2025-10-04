"""
Context7 Client
Интеграция с Context7 для получения современной документации технологий
"""

import asyncio
import aiohttp
import structlog
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import re

from ..core.config import Settings

logger = structlog.get_logger()


@dataclass
class Context7Document:
    """Документ из Context7"""

    title: str
    url: str
    content: str
    category: str
    technology: str
    tags: List[str]
    last_updated: Optional[datetime] = None


@dataclass
class Context7SearchResult:
    """Результат поиска в Context7"""

    documents: List[Context7Document]
    total_count: int
    query: str
    search_time: float


class Context7Client:
    """Клиент для работы с Context7 API"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = "https://context7.com"
        self.api_url = f"{self.base_url}/api/v1"
        self.session: Optional[aiohttp.ClientSession] = None

        # Популярные технологии для Context7
        self.popular_technologies = [
            "react",
            "nextjs",
            "vue",
            "angular",
            "svelte",
            "nodejs",
            "express",
            "fastapi",
            "django",
            "flask",
            "typescript",
            "javascript",
            "python",
            "rust",
            "go",
            "postgresql",
            "mongodb",
            "redis",
            "mysql",
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "gcp",
            "graphql",
            "rest",
            "websocket",
            "grpc",
            "tailwind",
            "bootstrap",
            "material-ui",
            "chakra-ui",
            "jest",
            "cypress",
            "playwright",
            "vitest",
            "webpack",
            "vite",
            "rollup",
            "esbuild",
            "git",
            "github",
            "gitlab",
            "bitbucket",
            "ci-cd",
            "github-actions",
            "gitlab-ci",
            "jenkins",
        ]

        # Маппинг технологий для n8n интеграций
        self.technology_n8n_mapping = {
            "react": ["HTTP Request", "Webhook", "Code"],
            "nextjs": ["HTTP Request", "Webhook", "Code"],
            "vue": ["HTTP Request", "Webhook", "Code"],
            "angular": ["HTTP Request", "Webhook", "Code"],
            "nodejs": ["HTTP Request", "Webhook", "Code", "Function"],
            "express": ["HTTP Request", "Webhook", "Code"],
            "fastapi": ["HTTP Request", "Webhook", "REST API"],
            "django": ["HTTP Request", "Webhook", "REST API"],
            "flask": ["HTTP Request", "Webhook", "REST API"],
            "typescript": ["Code", "HTTP Request", "Webhook"],
            "javascript": ["Code", "HTTP Request", "Webhook"],
            "python": ["Python Code", "HTTP Request", "Webhook"],
            "rust": ["HTTP Request", "Webhook"],
            "go": ["HTTP Request", "Webhook"],
            "postgresql": ["PostgreSQL", "Database"],
            "mongodb": ["MongoDB", "Database"],
            "redis": ["Redis", "Memory Cache"],
            "mysql": ["MySQL", "Database"],
            "docker": ["Docker", "HTTP Request"],
            "kubernetes": ["HTTP Request", "Webhook"],
            "aws": ["AWS", "HTTP Request", "Webhook"],
            "azure": ["Azure", "HTTP Request", "Webhook"],
            "gcp": ["Google Cloud", "HTTP Request", "Webhook"],
            "graphql": ["GraphQL", "HTTP Request"],
            "rest": ["REST API", "HTTP Request"],
            "websocket": ["WebSocket", "HTTP Request"],
            "grpc": ["HTTP Request", "Webhook"],
            "tailwind": ["HTTP Request", "Webhook"],
            "bootstrap": ["HTTP Request", "Webhook"],
            "material-ui": ["HTTP Request", "Webhook"],
            "chakra-ui": ["HTTP Request", "Webhook"],
            "jest": ["HTTP Request", "Webhook"],
            "cypress": ["HTTP Request", "Webhook"],
            "playwright": ["HTTP Request", "Webhook"],
            "vitest": ["HTTP Request", "Webhook"],
            "webpack": ["HTTP Request", "Webhook"],
            "vite": ["HTTP Request", "Webhook"],
            "rollup": ["HTTP Request", "Webhook"],
            "esbuild": ["HTTP Request", "Webhook"],
            "git": ["Git", "HTTP Request"],
            "github": ["GitHub", "HTTP Request", "Webhook"],
            "gitlab": ["GitLab", "HTTP Request", "Webhook"],
            "bitbucket": ["Bitbucket", "HTTP Request", "Webhook"],
            "ci-cd": ["Git", "HTTP Request", "Webhook"],
            "github-actions": ["GitHub", "HTTP Request", "Webhook"],
            "gitlab-ci": ["GitLab", "HTTP Request", "Webhook"],
            "jenkins": ["HTTP Request", "Webhook"],
        }

    async def initialize(self):
        """Инициализация клиента"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "User-Agent": "n8n-knowledge-system/1.0.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        logger.info("Context7 client initialized")

    async def close(self):
        """Закрытие клиента"""
        if self.session:
            await self.session.close()

    async def search_technology(
        self, technology: str, limit: int = 10
    ) -> Context7SearchResult:
        """Поиск документации по технологии в Context7"""
        try:
            logger.info("Searching Context7 for technology", technology=technology)

            start_time = datetime.now()

            # Формируем поисковый запрос
            search_query = self._build_search_query(technology)

            # Выполняем поиск (симуляция, так как Context7 API может требовать аутентификации)
            documents = await self._simulate_context7_search(
                technology, search_query, limit
            )

            search_time = (datetime.now() - start_time).total_seconds()

            result = Context7SearchResult(
                documents=documents,
                total_count=len(documents),
                query=search_query,
                search_time=search_time,
            )

            logger.info(
                "Context7 search completed",
                technology=technology,
                documents_found=len(documents),
                search_time=search_time,
            )

            return result

        except Exception as e:
            logger.error("Context7 search failed", technology=technology, error=str(e))
            return Context7SearchResult(
                documents=[], total_count=0, query=technology, search_time=0.0
            )

    def _build_search_query(self, technology: str) -> str:
        """Построение поискового запроса для технологии"""
        # Маппинг технологий для более точного поиска
        tech_mapping = {
            "react": "React.js ReactJS frontend library",
            "nextjs": "Next.js NextJS React framework",
            "vue": "Vue.js VueJS frontend framework",
            "angular": "Angular.js AngularJS frontend framework",
            "nodejs": "Node.js NodeJS backend runtime",
            "express": "Express.js ExpressJS Node.js framework",
            "fastapi": "FastAPI Python web framework",
            "django": "Django Python web framework",
            "flask": "Flask Python web framework",
            "typescript": "TypeScript TS JavaScript",
            "javascript": "JavaScript JS programming language",
            "python": "Python programming language",
            "rust": "Rust programming language",
            "go": "Go Golang programming language",
            "postgresql": "PostgreSQL Postgres database",
            "mongodb": "MongoDB NoSQL database",
            "redis": "Redis cache database",
            "mysql": "MySQL database",
            "docker": "Docker containerization",
            "kubernetes": "Kubernetes K8s orchestration",
            "aws": "AWS Amazon Web Services",
            "azure": "Azure Microsoft cloud",
            "gcp": "Google Cloud Platform GCP",
            "graphql": "GraphQL API query language",
            "rest": "REST API RESTful",
            "websocket": "WebSocket real-time communication",
            "grpc": "gRPC RPC framework",
            "tailwind": "Tailwind CSS utility framework",
            "bootstrap": "Bootstrap CSS framework",
            "material-ui": "Material-UI MUI React components",
            "chakra-ui": "Chakra UI React components",
            "jest": "Jest testing framework",
            "cypress": "Cypress testing framework",
            "playwright": "Playwright testing framework",
            "vitest": "Vitest testing framework",
            "webpack": "Webpack bundler",
            "vite": "Vite build tool",
            "rollup": "Rollup bundler",
            "esbuild": "esbuild bundler",
            "git": "Git version control",
            "github": "GitHub Git repository",
            "gitlab": "GitLab Git repository",
            "bitbucket": "Bitbucket Git repository",
            "ci-cd": "CI/CD continuous integration",
            "github-actions": "GitHub Actions CI/CD",
            "gitlab-ci": "GitLab CI/CD",
            "jenkins": "Jenkins CI/CD",
        }

        return tech_mapping.get(technology.lower(), technology)

    async def _simulate_context7_search(
        self, technology: str, query: str, limit: int
    ) -> List[Context7Document]:
        """Симуляция поиска в Context7 (заглушка для демонстрации)"""
        # В реальной реализации здесь был бы вызов к Context7 API
        # Пока создаем демонстрационные документы

        documents = []

        # Генерируем демонстрационные документы для технологии
        if technology.lower() in self.popular_technologies:
            # Основная документация
            main_doc = Context7Document(
                title=f"{technology.title()} - Getting Started",
                url=f"https://context7.com/docs/{technology}/getting-started",
                content=f"""
                {technology.title()} is a modern technology that provides excellent capabilities for development.
                
                Key Features:
                - Modern syntax and features
                - Excellent performance
                - Great community support
                - Extensive documentation
                
                Getting Started:
                1. Installation
                2. Basic setup
                3. First project
                4. Best practices
                
                This technology is widely used in modern web development and provides
                excellent integration capabilities with various tools and frameworks.
                """,
                category="getting-started",
                technology=technology,
                tags=["tutorial", "beginner", "setup"],
                last_updated=datetime.now(),
            )
            documents.append(main_doc)

            # API документация
            api_doc = Context7Document(
                title=f"{technology.title()} API Reference",
                url=f"https://context7.com/docs/{technology}/api",
                content=f"""
                {technology.title()} API Reference
                
                Core API Methods:
                - create() - Create new instances
                - update() - Update existing instances
                - delete() - Remove instances
                - query() - Search and filter data
                
                Configuration Options:
                - timeout: Request timeout in milliseconds
                - retries: Number of retry attempts
                - cache: Enable/disable caching
                
                Error Handling:
                - Validation errors
                - Network errors
                - Authentication errors
                
                Best Practices:
                - Always handle errors gracefully
                - Use appropriate timeouts
                - Implement proper logging
                """,
                category="api",
                technology=technology,
                tags=["api", "reference", "methods"],
                last_updated=datetime.now(),
            )
            documents.append(api_doc)

            # Интеграция с n8n
            n8n_doc = Context7Document(
                title=f"{technology.title()} n8n Integration",
                url=f"https://context7.com/docs/{technology}/n8n-integration",
                content=f"""
                {technology.title()} n8n Integration Guide
                
                Available n8n Nodes:
                {", ".join(self.technology_n8n_mapping.get(technology.lower(), ["HTTP Request", "Webhook"]))}
                
                Integration Patterns:
                1. Webhook Integration
                   - Set up webhook endpoint
                   - Configure n8n webhook node
                   - Process incoming data
                
                2. API Integration
                   - Use HTTP Request node
                   - Configure authentication
                   - Handle responses
                
                3. Database Integration
                   - Connect to database
                   - Use appropriate n8n database node
                   - Implement CRUD operations
                
                Example Workflow:
                1. Trigger: Manual or scheduled
                2. Action: {technology} API call
                3. Process: Data transformation
                4. Output: Store or send results
                
                Best Practices:
                - Use environment variables for configuration
                - Implement proper error handling
                - Add logging and monitoring
                - Test thoroughly before deployment
                """,
                category="integration",
                technology=technology,
                tags=["n8n", "integration", "workflow", "automation"],
                last_updated=datetime.now(),
            )
            documents.append(n8n_doc)

            # Примеры использования
            examples_doc = Context7Document(
                title=f"{technology.title()} Examples and Use Cases",
                url=f"https://context7.com/docs/{technology}/examples",
                content=f"""
                {technology.title()} Examples and Use Cases
                
                Common Use Cases:
                1. Web Application Development
                   - Frontend frameworks
                   - Backend APIs
                   - Full-stack applications
                
                2. Data Processing
                   - ETL pipelines
                   - Data analysis
                   - Report generation
                
                3. Automation
                   - CI/CD pipelines
                   - Task scheduling
                   - Workflow automation
                
                4. Integration
                   - Third-party APIs
                   - Database connections
                   - Message queues
                
                Code Examples:
                ```javascript
                // Example implementation
                const {technology} = require('{technology}');
                
                const instance = new {technology}({{
                    config: {{
                        timeout: 5000,
                        retries: 3
                    }}
                }});
                
                instance.process()
                    .then(result => {{
                        console.log('Success:', result);
                    }})
                    .catch(error => {{
                        console.error('Error:', error);
                    }});
                ```
                
                Performance Tips:
                - Use appropriate caching strategies
                - Optimize database queries
                - Implement connection pooling
                - Monitor resource usage
                """,
                category="examples",
                technology=technology,
                tags=["examples", "use-cases", "code", "performance"],
                last_updated=datetime.now(),
            )
            documents.append(examples_doc)

        # Ограничиваем количество документов
        return documents[:limit]

    async def get_technology_trends(self) -> List[Dict[str, Any]]:
        """Получение трендов технологий из Context7"""
        try:
            logger.info("Getting technology trends from Context7")

            # Симуляция получения трендов
            trends = [
                {
                    "technology": "react",
                    "trend_score": 0.95,
                    "growth_rate": 0.15,
                    "popularity": "very_high",
                    "category": "frontend",
                },
                {
                    "technology": "nextjs",
                    "trend_score": 0.88,
                    "growth_rate": 0.25,
                    "popularity": "high",
                    "category": "frontend",
                },
                {
                    "technology": "fastapi",
                    "trend_score": 0.82,
                    "growth_rate": 0.30,
                    "popularity": "high",
                    "category": "backend",
                },
                {
                    "technology": "typescript",
                    "trend_score": 0.92,
                    "growth_rate": 0.18,
                    "popularity": "very_high",
                    "category": "language",
                },
                {
                    "technology": "docker",
                    "trend_score": 0.85,
                    "growth_rate": 0.12,
                    "popularity": "high",
                    "category": "devops",
                },
            ]

            logger.info("Technology trends retrieved", count=len(trends))
            return trends

        except Exception as e:
            logger.error("Failed to get technology trends", error=str(e))
            return []

    async def get_technology_ecosystem(self, technology: str) -> Dict[str, Any]:
        """Получение экосистемы технологии из Context7"""
        try:
            logger.info("Getting technology ecosystem", technology=technology)

            # Симуляция получения экосистемы
            ecosystem = {
                "core_technology": technology,
                "related_technologies": self.technology_n8n_mapping.get(
                    technology.lower(), []
                ),
                "n8n_integrations": self.technology_n8n_mapping.get(
                    technology.lower(), ["HTTP Request", "Webhook"]
                ),
                "popular_combinations": self._get_popular_combinations(technology),
                "use_cases": self._get_use_cases(technology),
                "complexity_level": self._get_complexity_level(technology),
                "learning_resources": [
                    f"https://context7.com/docs/{technology}/getting-started",
                    f"https://context7.com/docs/{technology}/api",
                    f"https://context7.com/docs/{technology}/examples",
                ],
            }

            logger.info("Technology ecosystem retrieved", technology=technology)
            return ecosystem

        except Exception as e:
            logger.error(
                "Failed to get technology ecosystem",
                technology=technology,
                error=str(e),
            )
            return {}

    def _get_popular_combinations(self, technology: str) -> List[str]:
        """Получение популярных комбинаций технологий"""
        combinations = {
            "react": ["TypeScript", "Next.js", "Tailwind CSS", "Material-UI"],
            "nextjs": ["React", "TypeScript", "Tailwind CSS", "Vercel"],
            "vue": ["TypeScript", "Nuxt.js", "Vuetify", "Pinia"],
            "angular": ["TypeScript", "RxJS", "Angular Material", "NgRx"],
            "nodejs": ["Express", "TypeScript", "MongoDB", "Jest"],
            "express": ["Node.js", "TypeScript", "MongoDB", "JWT"],
            "fastapi": ["Python", "SQLAlchemy", "PostgreSQL", "Pydantic"],
            "django": ["Python", "PostgreSQL", "Redis", "Celery"],
            "flask": ["Python", "SQLAlchemy", "PostgreSQL", "JWT"],
            "typescript": ["React", "Node.js", "Express", "Jest"],
            "python": ["FastAPI", "Django", "PostgreSQL", "Redis"],
            "postgresql": ["SQLAlchemy", "Django", "FastAPI", "Redis"],
            "mongodb": ["Mongoose", "Node.js", "Express", "TypeScript"],
            "redis": ["Node.js", "Python", "Django", "FastAPI"],
            "docker": ["Kubernetes", "Docker Compose", "CI/CD", "GitHub Actions"],
            "kubernetes": ["Docker", "Helm", "Prometheus", "Istio"],
        }

        return combinations.get(technology.lower(), [])

    def _get_use_cases(self, technology: str) -> List[str]:
        """Получение use cases для технологии"""
        use_cases = {
            "react": ["web_applications", "mobile_apps", "admin_panels", "dashboards"],
            "nextjs": ["full_stack_apps", "static_sites", "e_commerce", "blogs"],
            "vue": ["progressive_apps", "spa", "mobile_apps", "admin_interfaces"],
            "angular": [
                "enterprise_apps",
                "large_applications",
                "admin_panels",
                "dashboards",
            ],
            "nodejs": ["apis", "microservices", "real_time_apps", "cli_tools"],
            "express": ["rest_apis", "web_servers", "microservices", "middleware"],
            "fastapi": ["apis", "microservices", "data_processing", "ai_ml"],
            "django": [
                "web_applications",
                "content_management",
                "apis",
                "admin_interfaces",
            ],
            "flask": ["apis", "web_applications", "microservices", "prototypes"],
            "typescript": ["frontend", "backend", "full_stack", "mobile"],
            "python": ["web_development", "data_science", "automation", "ai_ml"],
            "postgresql": [
                "web_applications",
                "analytics",
                "transaction_processing",
                "reporting",
            ],
            "mongodb": [
                "content_management",
                "real_time_apps",
                "mobile_backends",
                "analytics",
            ],
            "redis": [
                "caching",
                "session_storage",
                "message_queues",
                "real_time_features",
            ],
            "docker": ["containerization", "microservices", "ci_cd", "development"],
            "kubernetes": ["orchestration", "scaling", "deployment", "microservices"],
        }

        return use_cases.get(technology.lower(), ["general_purpose"])

    def _get_complexity_level(self, technology: str) -> str:
        """Получение уровня сложности технологии"""
        complexity = {
            "react": "medium",
            "nextjs": "medium",
            "vue": "low",
            "angular": "high",
            "nodejs": "medium",
            "express": "low",
            "fastapi": "low",
            "django": "medium",
            "flask": "low",
            "typescript": "medium",
            "python": "low",
            "postgresql": "medium",
            "mongodb": "low",
            "redis": "low",
            "docker": "medium",
            "kubernetes": "high",
        }

        return complexity.get(technology.lower(), "medium")

    async def check_health(self) -> bool:
        """Проверка доступности Context7"""
        try:
            if not self.session:
                return False

            # Простая проверка доступности
            async with self.session.get(self.base_url, timeout=5) as response:
                return response.status == 200

        except Exception as e:
            logger.error("Context7 health check failed", error=str(e))
            return False
