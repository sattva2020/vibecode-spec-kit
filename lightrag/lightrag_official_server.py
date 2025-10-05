#!/usr/bin/env python3
"""
Official LightRAG Server Integration
Интеграция с официальным LightRAG API
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

class LightRAGOfficialClient:
    """Клиент для официального LightRAG API"""
    
    def __init__(self, base_url: str = "http://rag-lightrag:8000"):
        self.base_url = base_url
        self.session = None
        
        # Endpoints официального LightRAG API
        self.endpoints = {
            'insert': f"{base_url}/insert",
            'query': f"{base_url}/query",
            'initialize': f"{base_url}/initialize",
            'finalize': f"{base_url}/finalize"
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def insert_text(self, text: str) -> Dict[str, Any]:
        """
        Вставка текста в LightRAG
        
        Args:
            text: Текст для вставки
            
        Returns:
            Результат операции вставки
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        payload = {"text": text}
        
        try:
            logger.info(f"Inserting text into LightRAG: {text[:100]}...")
            async with self.session.post(self.endpoints['insert'], json=payload) as response:
                result = await response.json()
                
                if response.status == 200:
                    logger.info("Text inserted successfully into LightRAG")
                    return {
                        "status": "success",
                        "message": "Text inserted into LightRAG",
                        "lightrag_response": result
                    }
                else:
                    logger.error(f"Failed to insert text into LightRAG: {result}")
                    return {
                        "status": "error",
                        "message": f"LightRAG insert failed: {result}",
                        "error": result
                    }
                    
        except Exception as e:
            logger.error(f"Error inserting text into LightRAG: {e}")
            return {
                "status": "error",
                "message": f"LightRAG insert error: {str(e)}",
                "error": str(e)
            }
    
    async def query_text(self, query: str, mode: str = "hybrid") -> Dict[str, Any]:
        """
        Запрос к LightRAG
        
        Args:
            query: Поисковый запрос
            mode: Режим запроса (naive, local, global, hybrid)
            
        Returns:
            Результаты поиска
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        payload = {
            "query": query,
            "mode": mode
        }
        
        try:
            logger.info(f"Querying LightRAG: {query}")
            async with self.session.post(self.endpoints['query'], json=payload) as response:
                result = await response.json()
                
                if response.status == 200:
                    logger.info("LightRAG query completed successfully")
                    return {
                        "status": "success",
                        "message": "LightRAG query completed",
                        "query": query,
                        "mode": mode,
                        "answer": result.get("answer", ""),
                        "lightrag_response": result
                    }
                else:
                    logger.error(f"Failed to query LightRAG: {result}")
                    return {
                        "status": "error",
                        "message": f"LightRAG query failed: {result}",
                        "error": result
                    }
                    
        except Exception as e:
            logger.error(f"Error querying LightRAG: {e}")
            return {
                "status": "error",
                "message": f"LightRAG query error: {str(e)}",
                "error": str(e)
            }
    
    async def initialize_storages(self) -> Dict[str, Any]:
        """
        Инициализация хранилищ LightRAG
        
        Returns:
            Результат инициализации
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        try:
            logger.info("Initializing LightRAG storages...")
            async with self.session.post(self.endpoints['initialize']) as response:
                result = await response.json()
                
                if response.status == 200:
                    logger.info("LightRAG storages initialized successfully")
                    return {
                        "status": "success",
                        "message": "LightRAG storages initialized",
                        "lightrag_response": result
                    }
                else:
                    logger.error(f"Failed to initialize LightRAG storages: {result}")
                    return {
                        "status": "error",
                        "message": f"LightRAG initialization failed: {result}",
                        "error": result
                    }
                    
        except Exception as e:
            logger.error(f"Error initializing LightRAG storages: {e}")
            return {
                "status": "error",
                "message": f"LightRAG initialization error: {str(e)}",
                "error": str(e)
            }
    
    async def finalize_storages(self) -> Dict[str, Any]:
        """
        Финализация хранилищ LightRAG
        
        Returns:
            Результат финализации
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        try:
            logger.info("Finalizing LightRAG storages...")
            async with self.session.post(self.endpoints['finalize']) as response:
                result = await response.json()
                
                if response.status == 200:
                    logger.info("LightRAG storages finalized successfully")
                    return {
                        "status": "success",
                        "message": "LightRAG storages finalized",
                        "lightrag_response": result
                    }
                else:
                    logger.error(f"Failed to finalize LightRAG storages: {result}")
                    return {
                        "status": "error",
                        "message": f"LightRAG finalization failed: {result}",
                        "error": result
                    }
                    
        except Exception as e:
            logger.error(f"Error finalizing LightRAG storages: {e}")
            return {
                "status": "error",
                "message": f"LightRAG finalization error: {str(e)}",
                "error": str(e)
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Получение статуса системы LightRAG
        
        Returns:
            Статус системы
        """
        try:
            # Попытка выполнить простой запрос для проверки доступности
            test_result = await self.query_text("test", "naive")
            
            return {
                'status': 'healthy' if test_result['status'] == 'success' else 'error',
                'lightrag_available': test_result['status'] == 'success',
                'endpoints': self.endpoints,
                'last_check': datetime.now().isoformat(),
                'test_result': test_result
            }
        except Exception as e:
            return {
                'status': 'error',
                'lightrag_available': False,
                'error': str(e),
                'endpoints': self.endpoints,
                'last_check': datetime.now().isoformat()
            }


# Пример использования
async def main():
    """Пример использования LightRAG Official Client"""
    
    async with LightRAGOfficialClient() as client:
        try:
            # Проверка состояния системы
            status = await client.get_system_status()
            print(f"LightRAG Status: {json.dumps(status, indent=2)}")
            
            # Инициализация хранилищ
            init_result = await client.initialize_storages()
            print(f"Initialization: {json.dumps(init_result, indent=2)}")
            
            # Вставка тестового текста
            insert_result = await client.insert_text(
                "LightRAG is a powerful RAG system that provides structured knowledge management."
            )
            print(f"Insert Result: {json.dumps(insert_result, indent=2)}")
            
            # Запрос к системе
            query_result = await client.query_text(
                "What is LightRAG?",
                mode="hybrid"
            )
            print(f"Query Result: {json.dumps(query_result, indent=2)}")
            
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
