#!/usr/bin/env python3
"""
Smart RAG Coordinator
Координатор для управления Smart RAG системой через n8n workflows
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartRAGCoordinator:
    """Координатор Smart RAG системы"""
    
    def __init__(self, n8n_base_url: str = "http://localhost:8080"):
        self.n8n_base_url = n8n_base_url
        self.session = None
        
        # URLs для Smart RAG workflows
        self.urls = {
            'insert': f"{n8n_base_url}/webhook/rag-insert",
            'query': f"{n8n_base_url}/webhook/rag-query", 
            'analyze': f"{n8n_base_url}/webhook/rag-analyze"
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def insert_knowledge(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Вставка нового знания в базу
        
        Args:
            text: Текст для вставки
            metadata: Дополнительные метаданные
            
        Returns:
            Результат операции вставки
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        payload = {
            "text": text,
            "metadata": metadata or {}
        }
        
        try:
            logger.info(f"Inserting knowledge: {text[:100]}...")
            async with self.session.post(self.urls['insert'], json=payload) as response:
                result = await response.json()
                
                if response.status == 200:
                    logger.info(f"Knowledge inserted successfully: {result.get('knowledge_id', 'unknown')}")
                    return result
                else:
                    logger.error(f"Failed to insert knowledge: {result}")
                    raise Exception(f"Insert failed: {result}")
                    
        except Exception as e:
            logger.error(f"Error inserting knowledge: {e}")
            raise
    
    async def query_knowledge(self, query: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Поиск знаний в базе
        
        Args:
            query: Поисковый запрос
            options: Дополнительные опции поиска
            
        Returns:
            Результаты поиска
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        payload = {
            "query": query,
            "options": options or {}
        }
        
        try:
            logger.info(f"Querying knowledge: {query}")
            async with self.session.post(self.urls['query'], json=payload) as response:
                result = await response.json()
                
                if response.status == 200:
                    logger.info(f"Query completed: {result.get('total_found', 0)} results found")
                    return result
                else:
                    logger.error(f"Failed to query knowledge: {result}")
                    raise Exception(f"Query failed: {result}")
                    
        except Exception as e:
            logger.error(f"Error querying knowledge: {e}")
            raise
    
    async def analyze_knowledge(self, knowledge_id: str, analysis_type: str = "comprehensive", 
                               options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Анализ существующего знания
        
        Args:
            knowledge_id: ID знания для анализа
            analysis_type: Тип анализа
            options: Дополнительные опции
            
        Returns:
            Результаты анализа
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        payload = {
            "knowledge_id": knowledge_id,
            "analysis_type": analysis_type,
            "options": options or {}
        }
        
        try:
            logger.info(f"Analyzing knowledge: {knowledge_id}")
            async with self.session.post(self.urls['analyze'], json=payload) as response:
                result = await response.json()
                
                if response.status == 200:
                    logger.info(f"Analysis completed for: {knowledge_id}")
                    return result
                else:
                    logger.error(f"Failed to analyze knowledge: {result}")
                    raise Exception(f"Analysis failed: {result}")
                    
        except Exception as e:
            logger.error(f"Error analyzing knowledge: {e}")
            raise
    
    async def batch_insert(self, knowledge_items: List[Dict[str, Any]], 
                          batch_size: int = 5) -> List[Dict[str, Any]]:
        """
        Пакетная вставка знаний
        
        Args:
            knowledge_items: Список элементов для вставки
            batch_size: Размер пакета
            
        Returns:
            Результаты вставки
        """
        results = []
        
        for i in range(0, len(knowledge_items), batch_size):
            batch = knowledge_items[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} items")
            
            # Параллельная обработка пакета
            tasks = []
            for item in batch:
                task = self.insert_knowledge(
                    text=item['text'],
                    metadata=item.get('metadata', {})
                )
                tasks.append(task)
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(batch_results)
            
            # Небольшая пауза между пакетами
            if i + batch_size < len(knowledge_items):
                await asyncio.sleep(1)
        
        return results
    
    async def smart_search(self, query: str, search_strategies: List[str] = None) -> Dict[str, Any]:
        """
        Умный поиск с использованием нескольких стратегий
        
        Args:
            query: Поисковый запрос
            search_strategies: Список стратегий поиска
            
        Returns:
            Агрегированные результаты поиска
        """
        if search_strategies is None:
            search_strategies = ['text_search', 'concept_search', 'tag_search']
        
        results = {}
        
        # Параллельный поиск с разными стратегиями
        tasks = []
        for strategy in search_strategies:
            options = {'strategy': strategy}
            task = self.query_knowledge(query, options)
            tasks.append(task)
        
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Агрегация результатов
        for i, strategy in enumerate(search_strategies):
            if isinstance(search_results[i], Exception):
                logger.error(f"Search strategy {strategy} failed: {search_results[i]}")
                results[strategy] = {'error': str(search_results[i])}
            else:
                results[strategy] = search_results[i]
        
        # Объединение и ранжирование результатов
        all_results = []
        for strategy_result in results.values():
            if 'results' in strategy_result:
                all_results.extend(strategy_result['results'])
        
        # Удаление дубликатов и ранжирование
        unique_results = {}
        for result in all_results:
            result_id = result.get('id')
            if result_id not in unique_results:
                unique_results[result_id] = result
            else:
                # Объединение результатов с максимальным relevance_score
                if result.get('relevance_score', 0) > unique_results[result_id].get('relevance_score', 0):
                    unique_results[result_id] = result
        
        final_results = list(unique_results.values())
        final_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return {
            'query': query,
            'strategies_used': search_strategies,
            'strategy_results': results,
            'aggregated_results': final_results,
            'total_found': len(final_results),
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Получение статистики системы
        
        Returns:
            Статистика системы
        """
        try:
            # Тестовый запрос для получения статистики
            test_query = await self.query_knowledge("system stats", {"limit": 1})
            
            return {
                'status': 'healthy',
                'workflows_accessible': True,
                'last_check': datetime.now().isoformat(),
                'test_query_results': test_query.get('total_found', 0)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }


# Пример использования
async def main():
    """Пример использования Smart RAG Coordinator"""
    
    async with SmartRAGCoordinator() as coordinator:
        try:
            # Проверка состояния системы
            stats = await coordinator.get_system_stats()
            print(f"System stats: {json.dumps(stats, indent=2)}")
            
            # Вставка тестового знания
            test_knowledge = {
                "text": "Python is a high-level programming language known for its simplicity and readability. It's widely used in web development, data science, and automation.",
                "metadata": {
                    "source": "test",
                    "category": "programming",
                    "author": "system"
                }
            }
            
            insert_result = await coordinator.insert_knowledge(
                text=test_knowledge["text"],
                metadata=test_knowledge["metadata"]
            )
            print(f"Insert result: {json.dumps(insert_result, indent=2)}")
            
            # Поиск знаний
            search_results = await coordinator.query_knowledge("Python programming")
            print(f"Search results: {json.dumps(search_results, indent=2)}")
            
            # Умный поиск
            smart_results = await coordinator.smart_search("programming languages")
            print(f"Smart search results: {json.dumps(smart_results, indent=2)}")
            
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
