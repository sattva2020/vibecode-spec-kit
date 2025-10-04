# 🤖 Ollama Models Configuration

## 📋 Используемые модели

### **Основные модели (RAG System)**

| Модель | Размер | Назначение | Статус |
|--------|--------|------------|--------|
| **qwen2.5-coder:1.5b** | 1.5B | Быстрая генерация кода | ✅ Активная |
| **qwen2.5-coder:7b** | 7B | Балансированная генерация | ✅ Активная |
| **nomic-embed-text** | 274M | Эмбеддинги для RAG | ✅ Активная |

### **Intelligent n8n System модели**

| Модель | Размер | Назначение | Конфигурация |
|--------|--------|------------|--------------|
| **llama3.2:3b** | 3B | Генерация кода | `OLLAMA_MODEL_CODE` |
| **llama3.2:7b** | 7B | Анализ проектов | `OLLAMA_MODEL_ANALYSIS` |
| **nomic-embed-text:latest** | 274M | Эмбеддинги | `OLLAMA_MODEL_EMBEDDING` |

## 🚀 Установка моделей

### Автоматическая установка
```bash
# Запуск скрипта установки (Windows)
.\scripts\start-rag-system.ps1

# Или вручную через Docker
docker exec rag-ollama ollama pull qwen2.5-coder:1.5b
docker exec rag-ollama ollama pull qwen2.5-coder:7b
docker exec rag-ollama ollama pull nomic-embed-text
```

### Ручная установка
```bash
# Подключение к Ollama контейнеру
docker exec -it rag-ollama bash

# Установка моделей
ollama pull qwen2.5-coder:1.5b
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text
ollama pull llama3.2:3b
ollama pull llama3.2:7b
```

## 📊 Характеристики моделей

### **qwen2.5-coder:1.5b**
- **Размер**: 1.5B параметров
- **Память**: ~1GB RAM
- **Скорость**: Очень быстрая (1-2 сек)
- **Качество**: Хорошее для простого кода
- **Использование**: Inline completions, быстрые предложения

### **qwen2.5-coder:7b**
- **Размер**: 7B параметров
- **Память**: ~4GB RAM
- **Скорость**: Быстрая (2-4 сек)
- **Качество**: Отличное для сложного кода
- **Использование**: Основная генерация кода, рефакторинг

### **llama3.2:3b**
- **Размер**: 3B параметров
- **Память**: ~2GB RAM
- **Скорость**: Быстрая (2-3 сек)
- **Качество**: Хорошее для анализа
- **Использование**: Анализ кода, генерация в n8n system

### **llama3.2:7b**
- **Размер**: 7B параметров
- **Память**: ~4GB RAM
- **Скорость**: Средняя (3-5 сек)
- **Качество**: Отличное для анализа
- **Использование**: Глубокий анализ проектов

### **nomic-embed-text**
- **Размер**: 274M параметров
- **Память**: ~500MB RAM
- **Скорость**: Очень быстрая (<1 сек)
- **Качество**: Высокое для эмбеддингов
- **Использование**: RAG поиск, семантический анализ

## ⚙️ Конфигурация

### Переменные окружения

```bash
# Основная RAG система
OLLAMA_MODEL=qwen2.5-coder:7b

# Intelligent n8n System
OLLAMA_MODEL_CODE=llama3.2:3b
OLLAMA_MODEL_EMBEDDING=nomic-embed-text:latest
OLLAMA_MODEL_ANALYSIS=llama3.2:7b
OLLAMA_BASE_URL=http://localhost:11434
```

### Выбор модели по задаче

```python
def select_model(task_type: str) -> str:
    """Выбор модели в зависимости от типа задачи"""
    if task_type == "quick_completion":
        return "qwen2.5-coder:1.5b"  # Быстрая генерация
    elif task_type == "code_generation":
        return "qwen2.5-coder:7b"    # Качественная генерация
    elif task_type == "analysis":
        return "llama3.2:7b"         # Глубокий анализ
    elif task_type == "embedding":
        return "nomic-embed-text"    # Эмбеддинги
    else:
        return "qwen2.5-coder:7b"    # По умолчанию
```

## 🔍 Проверка моделей

### Список установленных моделей
```bash
# Через API
curl http://localhost:11434/api/tags

# Через Docker
docker exec rag-ollama ollama list
```

### Тест модели
```bash
# Простой тест
curl http://localhost:11434/api/generate \
  -d '{
    "model": "qwen2.5-coder:7b",
    "prompt": "Write a Python function to calculate factorial:",
    "stream": false
  }'
```

## 📈 Мониторинг

### Использование ресурсов
```bash
# Статистика Docker контейнеров
docker stats rag-ollama

# Логи Ollama
docker logs rag-ollama -f
```

### Метрики производительности
- **Время ответа**: <500ms для быстрых моделей
- **Использование памяти**: Мониторинг через Grafana
- **Загрузка GPU**: Если доступна

## 🎯 Рекомендации

### Для разработки
1. **qwen2.5-coder:1.5b** - для быстрых inline completions
2. **qwen2.5-coder:7b** - для основной генерации кода
3. **nomic-embed-text** - для RAG поиска

### Для production
1. **llama3.2:7b** - для качественного анализа
2. **qwen2.5-coder:7b** - для генерации кода
3. **nomic-embed-text** - для эмбеддингов

### Оптимизация
- Используйте более быстрые модели для real-time функций
- Кешируйте результаты для повторяющихся запросов
- Мониторьте использование памяти и GPU
