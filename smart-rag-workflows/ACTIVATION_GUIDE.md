# 🚀 Smart RAG Workflows - Руководство по активации

## 📋 Статус развертывания

✅ **Выполнено:**
- Создана таблица `knowledge_base` в Supabase
- Созданы 3 Smart RAG workflows в n8n:
  - **RAG Insert Workflow** (ID: `GFZjxqPiv5DJT7KK`)
  - **RAG Query Workflow** (ID: `4JDiT1wAMiO5MN34`) 
  - **RAG Analyze Workflow** (ID: `mDgyQhrizc15KuBK`)

⚠️ **Требуется активация:**
- Workflows созданы, но не активированы (API активация не работает)

## 🔧 Инструкция по активации

### Шаг 1: Откройте n8n веб-интерфейс
```
http://localhost:8080
```

### Шаг 2: Найдите и активируйте workflows

#### 2.1 RAG Insert Workflow
1. Найдите workflow с ID: `GFZjxqPiv5DJT7KK`
2. Откройте его
3. Нажмите кнопку **"Activate"** (активировать)
4. Убедитесь, что статус изменился на **"Active"**

#### 2.2 RAG Query Workflow  
1. Найдите workflow с ID: `4JDiT1wAMiO5MN34`
2. Откройте его
3. Нажмите кнопку **"Activate"** (активировать)
4. Убедитесь, что статус изменился на **"Active"**

#### 2.3 RAG Analyze Workflow
1. Найдите workflow с ID: `mDgyQhrizc15KuBK`
2. Откройте его
3. Нажмите кнопку **"Activate"** (активировать)
4. Убедитесь, что статус изменился на **"Active"**

## 🧪 Тестирование после активации

### Тест 1: Вставка знания
```bash
curl -X POST http://localhost:8080/webhook/rag-insert \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Smart RAG система успешно развернута и готова к работе.",
    "metadata": {
      "source": "test",
      "category": "system",
      "author": "test_user"
    }
  }'
```

### Тест 2: Поиск знаний
```bash
curl -X POST http://localhost:8080/webhook/rag-query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Smart RAG система",
    "options": {
      "limit": 5
    }
  }'
```

### Тест 3: Анализ знания
```bash
curl -X POST http://localhost:8080/webhook/rag-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_id": "ЗАМЕНИТЕ_НА_ID_ИЗ_ТЕСТА_1",
    "analysis_type": "comprehensive"
  }'
```

## 🐍 Тестирование через Python

```python
import asyncio
import aiohttp
import json

async def test_smart_rag():
    async with aiohttp.ClientSession() as session:
        # Тест вставки
        insert_payload = {
            "text": "Python is a powerful programming language for data science and web development.",
            "metadata": {
                "source": "python_test",
                "category": "programming",
                "author": "python_user"
            }
        }
        
        async with session.post(
            "http://localhost:8080/webhook/rag-insert",
            json=insert_payload
        ) as response:
            result = await response.json()
            print(f"Insert result: {json.dumps(result, indent=2)}")
            
            if 'knowledge_id' in result:
                knowledge_id = result['knowledge_id']
                
                # Тест поиска
                query_payload = {
                    "query": "Python programming",
                    "options": {"limit": 3}
                }
                
                async with session.post(
                    "http://localhost:8080/webhook/rag-query",
                    json=query_payload
                ) as response:
                    result = await response.json()
                    print(f"Query result: {json.dumps(result, indent=2)}")
                
                # Тест анализа
                analyze_payload = {
                    "knowledge_id": knowledge_id,
                    "analysis_type": "comprehensive"
                }
                
                async with session.post(
                    "http://localhost:8080/webhook/rag-analyze",
                    json=analyze_payload
                ) as response:
                    result = await response.json()
                    print(f"Analyze result: {json.dumps(result, indent=2)}")

# Запуск тестов
asyncio.run(test_smart_rag())
```

## 🔍 Проверка статуса workflows

### Через API:
```bash
curl -X GET http://localhost:8080/api/v1/workflows \
  -H "X-N8N-API-KEY: $N8N_API_KEY"
```

### Через веб-интерфейс:
1. Откройте http://localhost:8080
2. Перейдите в раздел "Workflows"
3. Проверьте статус каждого workflow (должен быть "Active")

## 🚨 Устранение проблем

### Проблема: Webhook не найден (404)
**Решение:** Убедитесь, что workflow активирован в веб-интерфейсе

### Проблема: Ошибка подключения к Supabase
**Решение:** Проверьте, что Supabase запущен:
```bash
docker ps | grep supabase
```

### Проблема: Ошибка подключения к Ollama
**Решение:** Проверьте, что Ollama запущен:
```bash
docker ps | grep ollama
```

## 📊 Ожидаемые результаты

### Успешная вставка:
```json
{
  "status": "success",
  "message": "Knowledge inserted successfully",
  "knowledge_id": "knowledge_1234567890_abcdef123",
  "analysis": {
    "summary": "Python is a powerful programming language...",
    "category": "programming",
    "key_concepts": ["Python", "programming", "data science"],
    "tags": ["python", "programming", "data-science"]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Успешный поиск:
```json
{
  "status": "success",
  "query": "Python programming",
  "results": [
    {
      "id": "knowledge_1234567890_abcdef123",
      "summary": "Python is a powerful programming language...",
      "category": "programming",
      "relevance_score": 0.95
    }
  ],
  "total_found": 1,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🎉 После успешной активации

Smart RAG система будет готова к использованию:
- ✅ Автоматический анализ текста через Ollama
- ✅ Сохранение в Supabase с метаданными
- ✅ Интеллектуальный поиск с ранжированием
- ✅ Анализ и улучшение существующих знаний

**Следующий этап:** Реализация Adaptive AI Router
