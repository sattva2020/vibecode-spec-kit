# 🧠 AI Architecture Redesign

## 🎯 Новая концепция

### **Ollama - только для графа базы данных**
- **Назначение**: Обслуживание knowledge graph, embeddings
- **Модели**: nomic-embed-text, легкие модели для графа
- **Функции**: Семантический поиск, индексация документов

### **Платные API - для основной работы**
- **Anthropic Claude**: Анализ кода, архитектурные решения
- **OpenAI GPT-4/Codex**: Генерация кода, рефакторинг
- **Другие API**: Специализированные задачи

## 🏗️ Архитектура системы

```
┌─────────────────────────────────────────────────────────────┐
│                    VS Code Extension                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  AI Router Service                          │
│  • Определяет тип задачи                                    │
│  • Выбирает подходящий API                                  │
│  • Маршрутизирует запросы                                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──┐ ┌───────▼──┐ ┌────────▼────────┐
│  Claude  │ │   GPT-4  │ │   Ollama Graph   │
│  API     │ │   API    │ │   Service        │
└──────────┘ └──────────┘ └──────────────────┘
```

## 🔄 Маршрутизация задач

### **К Ollama (граф БД)**
- Семантический поиск по коду
- Индексация новых документов
- Обновление knowledge graph
- Embeddings для RAG

### **К Claude API**
- Анализ архитектуры
- Код-ревью и рефакторинг
- Сложные архитектурные решения
- Документация высокого уровня

### **К GPT-4/Codex API**
- Генерация кода
- Inline completions
- Быстрые исправления
- Техническая документация

## ⚙️ Конфигурация

### Переменные окружения
```bash
# Ollama (только для графа)
OLLAMA_URL=http://localhost:11434
OLLAMA_GRAPH_MODEL=nomic-embed-text
OLLAMA_INDEX_MODEL=qwen2.5-coder:1.5b

# Anthropic Claude
ANTHROPIC_API_KEY=your-claude-key
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_MAX_TOKENS=4096

# OpenAI
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_CODE_MODEL=gpt-4-code-interpreter

# Другие API
GOOGLE_API_KEY=your-google-key
GOOGLE_MODEL=gemini-pro
```

### Роутинг правил
```python
def route_task(task_type: str, complexity: str) -> str:
    """Маршрутизация задач по API"""
    
    if task_type == "semantic_search":
        return "ollama"  # Только для графа
    
    elif task_type == "code_analysis" and complexity == "high":
        return "claude"  # Сложный анализ
    
    elif task_type == "code_generation":
        return "openai"  # Генерация кода
    
    elif task_type == "inline_completion":
        return "openai"  # Быстрые предложения
    
    else:
        return "claude"  # По умолчанию
```

## 💰 Экономия ресурсов

### **Ollama (локально)**
- ✅ Бесплатно
- ✅ Приватность данных
- ✅ Быстрые embeddings
- ❌ Ограниченные возможности

### **Платные API**
- ✅ Современные модели
- ✅ Высокое качество
- ✅ Специализированные возможности
- ❌ Стоимость за токен

## 🚀 Преимущества новой архитектуры

1. **Экономия**: Ollama только для графа (бесплатно)
2. **Качество**: Платные API для основной работы
3. **Гибкость**: Легко переключаться между API
4. **Масштабируемость**: Каждый API для своих задач
5. **Приватность**: Локальный граф БД
