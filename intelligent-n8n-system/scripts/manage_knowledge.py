#!/usr/bin/env python3
"""
Knowledge Management CLI
Управление граф-базой знаний для n8n системы
"""

import asyncio
import argparse
import sys
import json
from pathlib import Path
from typing import Dict, List, Any

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent.parent))

from src.core.config import Settings
from src.knowledge.lightrag_service import LightRAGService
from src.knowledge.knowledge_ingestion_pipeline import KnowledgeIngestionPipeline


class KnowledgeManagerCLI:
    """CLI для управления знаниями"""

    def __init__(self):
        self.settings = Settings()
        self.lightrag_service = None
        self.pipeline = None

    async def initialize(self):
        """Инициализация сервисов"""
        self.lightrag_service = LightRAGService(self.settings)
        self.pipeline = KnowledgeIngestionPipeline(self.settings, self.lightrag_service)

        await self.lightrag_service.initialize()
        await self.pipeline.initialize()

    async def close(self):
        """Закрытие сервисов"""
        if self.pipeline:
            await self.pipeline.close()
        if self.lightrag_service:
            await self.lightrag_service.close()

    async def init_knowledge_base(self):
        """Инициализация базы знаний"""
        print("🧠 Initializing knowledge base...")

        try:
            # Инициализируем LightRAG
            await self.lightrag_service.initialize_knowledge_base()
            print("✅ LightRAG knowledge base initialized")

            # Наполняем предопределенными технологиями
            success = await self.pipeline.ingest_initial_technologies()
            if success:
                print("✅ Initial technologies ingested successfully")
            else:
                print("❌ Failed to ingest initial technologies")
                return False

            print("🎉 Knowledge base initialization completed!")
            return True

        except Exception as e:
            print(f"❌ Failed to initialize knowledge base: {e}")
            return False

    async def search_technologies(self, query: str, limit: int = 10):
        """Поиск технологий"""
        print(f"🔍 Searching technologies: '{query}'")

        try:
            results = await self.lightrag_service.query_relevant_knowledge(query)

            print(f"\n📊 Found {len(results.nodes)} results:")
            print("-" * 50)

            for i, node in enumerate(results.nodes[:limit], 1):
                print(f"{i}. {node.name}")
                print(f"   Category: {node.metadata.get('category', 'Unknown')}")
                print(f"   Confidence: {node.confidence:.2f}")
                print(
                    f"   N8N Integrations: {', '.join(node.metadata.get('n8n_integrations', []))}"
                )
                print()

            return True

        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False

    async def get_recommendations(self, project_context: Dict[str, Any]):
        """Получение рекомендаций технологий"""
        print("🎯 Getting technology recommendations...")
        print(f"Project context: {project_context}")

        try:
            recommendations = await self.pipeline.get_technology_recommendations(
                project_context
            )

            print(f"\n🚀 Technology Recommendations:")
            print("-" * 50)

            for i, tech in enumerate(recommendations, 1):
                print(f"{i}. {tech.name}")
                print(f"   Category: {tech.category}")
                print(f"   Description: {tech.description}")
                print(f"   Use Cases: {', '.join(tech.use_cases)}")
                print(f"   N8N Integrations: {', '.join(tech.n8n_integrations)}")
                print(f"   Complexity: {tech.complexity_level}")
                print()

            return True

        except Exception as e:
            print(f"❌ Failed to get recommendations: {e}")
            return False

    async def get_workflow_suggestions(self, technologies: List[str]):
        """Получение предложений n8n workflow"""
        print(f"🔄 Getting n8n workflow suggestions for: {', '.join(technologies)}")

        try:
            suggestions = await self.pipeline.get_n8n_workflow_suggestions(technologies)

            print(f"\n⚡ N8N Workflow Suggestions:")
            print("-" * 50)

            for i, workflow in enumerate(suggestions, 1):
                print(f"{i}. {workflow['name']}")
                print(f"   Description: {workflow['description']}")
                print(f"   Technologies: {', '.join(workflow['technologies'])}")
                print(f"   N8N Nodes: {', '.join(workflow['n8n_nodes'])}")
                print(f"   Complexity: {workflow['complexity']}")
                print()

            return True

        except Exception as e:
            print(f"❌ Failed to get workflow suggestions: {e}")
            return False

    async def update_popularity(self):
        """Обновление популярности технологий"""
        print("📈 Updating technology popularity...")

        try:
            success = await self.pipeline.update_technology_popularity()
            if success:
                print("✅ Technology popularity updated successfully")
            else:
                print("❌ Failed to update technology popularity")
            return success

        except Exception as e:
            print(f"❌ Update failed: {e}")
            return False

    async def discover_new_technologies(self):
        """Обнаружение новых технологий"""
        print("🔍 Discovering new technologies...")

        try:
            new_technologies = await self.pipeline.discover_new_technologies()

            if new_technologies:
                print(f"🆕 Discovered {len(new_technologies)} new technologies:")
                for tech in new_technologies:
                    print(f"  - {tech.name} ({tech.category})")
            else:
                print("ℹ️ No new technologies discovered")

            return True

        except Exception as e:
            print(f"❌ Discovery failed: {e}")
            return False

    async def export_knowledge(self, output_file: str):
        """Экспорт базы знаний"""
        print(f"💾 Exporting knowledge base to {output_file}")

        try:
            # Получаем все технологии
            all_technologies = {}
            for tech_name, tech_entity in self.pipeline.predefined_technologies.items():
                all_technologies[tech_name] = {
                    "name": tech_entity.name,
                    "category": tech_entity.category,
                    "description": tech_entity.description,
                    "use_cases": tech_entity.use_cases,
                    "related_technologies": tech_entity.related_technologies,
                    "n8n_integrations": tech_entity.n8n_integrations,
                    "complexity_level": tech_entity.complexity_level,
                    "popularity_score": tech_entity.popularity_score,
                }

            # Сохраняем в файл
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_technologies, f, indent=2, ensure_ascii=False)

            print(f"✅ Knowledge base exported to {output_file}")
            return True

        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False

    async def stats(self):
        """Статистика базы знаний"""
        print("📊 Knowledge Base Statistics")
        print("-" * 30)

        try:
            total_technologies = len(self.pipeline.predefined_technologies)

            # Подсчитываем по категориям
            categories = {}
            for tech in self.pipeline.predefined_technologies.values():
                category = tech.category
                categories[category] = categories.get(category, 0) + 1

            print(f"Total Technologies: {total_technologies}")
            print("\nBy Category:")
            for category, count in sorted(categories.items()):
                print(f"  {category}: {count}")

            # Подсчитываем n8n интеграции
            all_integrations = set()
            for tech in self.pipeline.predefined_technologies.values():
                all_integrations.update(tech.n8n_integrations)

            print(f"\nN8N Integrations: {len(all_integrations)}")
            print("Available integrations:")
            for integration in sorted(all_integrations):
                print(f"  - {integration}")

            return True

        except Exception as e:
            print(f"❌ Stats failed: {e}")
            return False

    async def sync_with_context7(self):
        """Синхронизация с Context7"""
        print("🔄 Syncing with Context7...")

        try:
            results = await self.pipeline.sync_with_context7()

            print(f"\n📊 Context7 Sync Results:")
            print("-" * 50)
            print(f"Technologies Processed: {results['technologies_processed']}")
            print(f"Technologies Enriched: {results['technologies_enriched']}")
            print(
                f"New Technologies Discovered: {results['new_technologies_discovered']}"
            )
            print(f"Documents Added: {results['documents_added']}")

            if results["errors"]:
                print(f"\n❌ Errors ({len(results['errors'])}):")
                for error in results["errors"]:
                    print(
                        f"  - {error.get('technology', 'Unknown')}: {error.get('error', 'Unknown error')}"
                    )
            else:
                print("\n✅ No errors occurred during sync")

            print("\n🎉 Context7 sync completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Context7 sync failed: {e}")
            return False

    async def enrich_technology(self, technology_name: str):
        """Обогащение технологии данными из Context7"""
        print(f"🔍 Enriching {technology_name} with Context7 data...")

        try:
            success = await self.pipeline.enrich_technology_with_context7(
                technology_name
            )

            if success:
                print(f"✅ {technology_name} enriched successfully with Context7 data")

                # Показываем обновленную информацию
                if technology_name.lower() in self.pipeline.predefined_technologies:
                    tech = self.pipeline.predefined_technologies[
                        technology_name.lower()
                    ]
                    print(f"\n📋 Updated Technology Information:")
                    print(f"  Name: {tech.name}")
                    print(f"  Category: {tech.category}")
                    print(f"  Use Cases: {', '.join(tech.use_cases)}")
                    print(
                        f"  Related Technologies: {', '.join(tech.related_technologies)}"
                    )
                    print(f"  N8N Integrations: {', '.join(tech.n8n_integrations)}")
                    print(f"  Complexity: {tech.complexity_level}")
            else:
                print(f"❌ Failed to enrich {technology_name} with Context7 data")

            return success

        except Exception as e:
            print(f"❌ Technology enrichment failed: {e}")
            return False


async def main():
    """Главная функция CLI"""
    parser = argparse.ArgumentParser(description="Knowledge Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Команда инициализации
    subparsers.add_parser("init", help="Initialize knowledge base")

    # Команда поиска
    search_parser = subparsers.add_parser("search", help="Search technologies")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=10, help="Limit results")

    # Команда рекомендаций
    recommend_parser = subparsers.add_parser(
        "recommend", help="Get technology recommendations"
    )
    recommend_parser.add_argument("--technologies", nargs="+", help="Technologies list")
    recommend_parser.add_argument("--architecture", help="Architecture type")
    recommend_parser.add_argument("--use-cases", nargs="+", help="Use cases list")

    # Команда workflow предложений
    workflow_parser = subparsers.add_parser(
        "workflows", help="Get n8n workflow suggestions"
    )
    workflow_parser.add_argument("technologies", nargs="+", help="Technologies list")

    # Команда обновления
    subparsers.add_parser("update", help="Update technology popularity")

    # Команда обнаружения
    subparsers.add_parser("discover", help="Discover new technologies")

    # Команда экспорта
    export_parser = subparsers.add_parser("export", help="Export knowledge base")
    export_parser.add_argument("output", help="Output file path")

    # Команда статистики
    subparsers.add_parser("stats", help="Show knowledge base statistics")

    # Команда синхронизации с Context7
    subparsers.add_parser(
        "sync-context7", help="Sync with Context7 for latest technology data"
    )

    # Команда обогащения технологии
    enrich_parser = subparsers.add_parser(
        "enrich", help="Enrich technology with Context7 data"
    )
    enrich_parser.add_argument("technology", help="Technology name to enrich")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Инициализируем CLI
    cli = KnowledgeManagerCLI()

    try:
        await cli.initialize()

        # Выполняем команду
        if args.command == "init":
            await cli.init_knowledge_base()

        elif args.command == "search":
            await cli.search_technologies(args.query, args.limit)

        elif args.command == "recommend":
            project_context = {
                "technologies": args.technologies or [],
                "architecture": args.architecture or "not specified",
                "use_cases": args.use_cases or [],
            }
            await cli.get_recommendations(project_context)

        elif args.command == "workflows":
            await cli.get_workflow_suggestions(args.technologies)

        elif args.command == "update":
            await cli.update_popularity()

        elif args.command == "discover":
            await cli.discover_new_technologies()

        elif args.command == "export":
            await cli.export_knowledge(args.output)

        elif args.command == "stats":
            await cli.stats()

        elif args.command == "sync-context7":
            await cli.sync_with_context7()

        elif args.command == "enrich":
            await cli.enrich_technology(args.technology)

    finally:
        await cli.close()


if __name__ == "__main__":
    asyncio.run(main())
