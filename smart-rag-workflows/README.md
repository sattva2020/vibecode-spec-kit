# 🧠 Smart RAG System

**Интеллектуальная RAG система на базе n8n + Ollama + Supabase**

## 🎯 Описание

Smart RAG - это революционная система для работы с знаниями, которая заменяет сложные зависимости LightRAG на простые и надежные n8n workflows. Система использует Ollama для анализа текста и Supabase для хранения структурированных знаний.

## 🏗️ Архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │   Python API    │    │   n8n Webhooks  │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      Smart RAG Core       │
                    │      (n8n Workflows)      │
                    └─────────────┬─────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
┌─────────▼───────┐    ┌─────────▼───────┐    ┌─────────▼───────┐
│   Ollama AI     │    │   Supabase DB   │    │   Text Analysis │
│   (Analysis)    │    │   (Storage)     │    │   (Processing)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Компоненты

### 1. **RAG Insert Workflow** (`rag-insert.json`)
- **Функция:** Вставка новых знаний в базу
- **Процесс:**
  1. Получение текста и метаданных
  2. Анализ текста через Ollama (qwen2.5-coder:7b)
  3. Извлечение ключевых концепций, сущностей и связей
  4. Сохранение в Supabase с структурированным анализом
- **Webhook:** `POST /webhook/rag-insert`

### 2. **RAG Query Workflow** (`rag-query.json`)
- **Функция:** Интеллектуальный поиск знаний
- **Процесс:**
  1. Анализ поискового запроса через Ollama
  2. Построение оптимизированного SQL запроса
  3. Поиск в Supabase с фильтрами
  4. Ранжирование результатов по релевантности
- **Webhook:** `POST /webhook/rag-query`

### 3. **RAG Analyze Workflow** (`rag-analyze.json`)
- **Функция:** Анализ и улучшение существующих знаний
- **Процесс:**
  1. Получение существующего знания
  2. Глубокий анализ через Ollama
  3. Поиск связанных знаний
  4. Генерация рекомендаций по улучшению
- **Webhook:** `POST /webhook/rag-analyze`

## 📊 База данных

### Таблица `knowledge_base`
```sql
CREATE TABLE knowledge_base (
    id TEXT PRIMARY KEY,
    original_text TEXT NOT NULL,
    processed_text TEXT,
    analysis JSONB,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Структура анализа
```json
{
  "summary": "Краткое описание знания",
  "category": "категория",
  "key_concepts": ["концепция1", "концепция2"],
  "entities": ["сущность1", "сущность2"],
  "relationships": [
    {"from": "A", "to": "B", "type": "связь"}
  ],
  "tags": ["тег1", "тег2"],
  "quality_score": 8
}
```

## 🔧 Установка и настройка

### 1. Предварительные требования
- Docker и Docker Compose
- n8n (запущен на порту 8080)
- Supabase (запущен на порту 5432)
- Ollama (запущен на порту 11434)

### 2. Развертывание
```bash
# Клонирование и переход в директорию
cd smart-rag-workflows

# Создание таблицы в Supabase
Get-Content create-knowledge-table.sql | docker exec -i rag-supabase-db psql -U postgres -d postgres

# Создание workflows в n8n
.\deploy-smart-rag.ps1
```

### 3. Активация workflows
Следуйте инструкциям в [ACTIVATION_GUIDE.md](ACTIVATION_GUIDE.md)

## 🧪 Использование

### Python API
```python
from smart_rag_coordinator import SmartRAGCoordinator
import asyncio

async def main():
    async with SmartRAGCoordinator() as rag:
        # Вставка знания
        result = await rag.insert_knowledge(
            text="Python - мощный язык программирования",
            metadata={"category": "programming", "source": "manual"}
        )
        
        # Поиск знаний
        results = await rag.query_knowledge("Python программирование")
        
        # Анализ знания
        analysis = await rag.analyze_knowledge(result['knowledge_id'])

asyncio.run(main())
```

### HTTP API
```bash
# Вставка
curl -X POST http://localhost:8080/webhook/rag-insert \
  -H "Content-Type: application/json" \
  -d '{"text": "Текст для анализа", "metadata": {"category": "test"}}'

# Поиск
curl -X POST http://localhost:8080/webhook/rag-query \
  -H "Content-Type: application/json" \
  -d '{"query": "поисковый запрос", "options": {"limit": 10}}'

# Анализ
curl -X POST http://localhost:8080/webhook/rag-analyze \
  -H "Content-Type: application/json" \
  -d '{"knowledge_id": "ID_ЗНАНИЯ", "analysis_type": "comprehensive"}'
```

## 🎯 Преимущества

### ✅ Простота
- Нет сложных зависимостей Python
- Все через n8n workflows
- Легко отлаживать и модифицировать

### ✅ Надежность
- Автоматическое восстановление
- Fallback механизмы
- Стабильная работа с Docker

### ✅ Гибкость
- Легко добавлять новые функции
- Простое масштабирование
- Адаптация к новым требованиям

### ✅ Интеллект
- Анализ через Ollama
- Структурированное хранение
- Умный поиск и ранжирование

## 📈 Производительность

### Модели Ollama
- **qwen2.5-coder:1.5b** - Быстрый анализ простых задач
- **qwen2.5-coder:7b** - Качественный анализ сложных задач

### Оптимизации
- Индексирование в Supabase
- Кэширование результатов
- Параллельная обработка

## 🔍 Мониторинг

### Логи n8n
```bash
docker logs rag-n8n
```

### Логи Supabase
```bash
docker logs rag-supabase-db
```

### Логи Ollama
```bash
docker logs rag-ollama
```

## 🚨 Устранение проблем

### Webhook не найден (404)
**Решение:** Убедитесь, что workflow активирован в n8n UI

### Ошибка подключения к Supabase
**Решение:** Проверьте статус контейнера `rag-supabase-db`

### Ошибка подключения к Ollama
**Решение:** Проверьте статус контейнера `rag-ollama`

### Медленная работа
**Решение:** Проверьте загрузку CPU и память контейнеров

## 🔮 Планы развития

### Ближайшие улучшения
- [ ] Векторный поиск через pgvector
- [ ] Автоматическая категоризация
- [ ] Система рекомендаций
- [ ] Экспорт/импорт знаний

### Долгосрочные планы
- [ ] Интеграция с внешними API
- [ ] Машинное обучение для улучшения качества
- [ ] Многоязычная поддержка
- [ ] Веб-интерфейс для управления

## 📚 Дополнительные ресурсы

- [ACTIVATION_GUIDE.md](ACTIVATION_GUIDE.md) - Руководство по активации
- [deploy-smart-rag.ps1](deploy-smart-rag.ps1) - Скрипт развертывания
- [smart-rag-coordinator.py](smart-rag-coordinator.py) - Python API
- [create-knowledge-table.sql](create-knowledge-table.sql) - SQL для создания таблицы

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте логи контейнеров
2. Убедитесь в правильности активации workflows
3. Проверьте подключение между сервисами
4. Обратитесь к [ACTIVATION_GUIDE.md](ACTIVATION_GUIDE.md)

---

**Smart RAG System v1.0.0** - Революционный подход к работе с знаниями! 🚀
