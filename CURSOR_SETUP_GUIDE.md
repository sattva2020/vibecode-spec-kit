# 🎯 Cursor IDE Integration - Полное руководство

## 💡 Концепция

**Используйте ваши платные подписки Cursor IDE для n8n автоматизации!**

Вместо покупки отдельных AI API, система будет использовать те же модели, что и ваш Cursor IDE.

## 🚀 Быстрая настройка

### **1. Получите Cursor API ключ**

1. Откройте Cursor IDE
2. Перейдите в **Settings** > **Account** > **API Keys**
3. Создайте новый API ключ для "n8n-ai-router"
4. Скопируйте ключ

### **2. Запустите скрипт настройки**

```powershell
# Автоматическая настройка
.\scripts\setup-cursor-integration.ps1 -CursorApiKey "your-api-key"

# Или интерактивно
.\scripts\setup-cursor-integration.ps1
```

### **3. Проверьте интеграцию**

```bash
# Проверка здоровья AI Router
curl http://localhost:8081/health

# Проверка Cursor интеграции
curl http://localhost:8081/cursor/health
```

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    Cursor IDE                               │
│  • Ваша платная подписка (Claude, GPT-4, etc.)            │
│  • API для терминальных сессий                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  AI Router Service                         │
│  • Подключается к Cursor API                               │
│  • Создает терминальную сессию "n8n-ai-router"            │
│  • Маршрутизирует n8n задачи                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  n8n System                                │
│  • Получает анализ через Cursor                            │
│  • Создает workflow'ы                                       │
│  • Использует ваши модели                                   │
└─────────────────────────────────────────────────────────────┘
```

## ⚙️ Конфигурация

### **Переменные окружения**

```bash
# Cursor IDE Integration
CURSOR_API_KEY=your-cursor-api-key
CURSOR_API_URL=https://api.cursor.sh/v1
CURSOR_SESSION_NAME=n8n-ai-router

# Режим работы
AI_PROVIDER_MODE=cursor_first  # cursor_first, paid_only, cursor_only
AI_DEFAULT_PROVIDER=cursor
AI_FALLBACK_PROVIDER=claude
```

### **Режимы работы**

1. **cursor_first** - Сначала Cursor, потом fallback API
2. **cursor_only** - Только Cursor API
3. **paid_only** - Только платные API (Claude, OpenAI)

## 🔄 Как это работает

### **1. Инициализация**

```python
# AI Router создает терминальную сессию в Cursor
session = await cursor_client.create_terminal_session({
    "name": "n8n-ai-router",
    "type": "automation",
    "description": "AI Router для n8n workflow'ов"
})
```

### **2. Анализ проекта для n8n**

```python
# Отправка запроса в Cursor
response = await cursor_client.analyze_for_n8n({
    "project_path": "/path/to/project",
    "technologies": ["python", "fastapi", "postgresql"],
    "task_type": "workflow_creation"
})
```

### **3. Создание workflow**

```python
# Cursor возвращает анализ, система создает n8n workflow
workflow = await n8n_client.create_workflow(
    analysis=response.workflow_suggestions,
    project_context=request.context
)
```

## 📊 Преимущества

### **💰 Экономия средств**
- ✅ Используете уже купленные подписки
- ✅ Не нужно платить за отдельные AI API
- ✅ Один аккаунт для всех задач

### **🎯 Качество**
- ✅ Те же модели, что и в IDE
- ✅ Одинаковое качество анализа
- ✅ Консистентные результаты

### **🔧 Простота**
- ✅ Один API ключ для всего
- ✅ Не нужно управлять множественными подписками
- ✅ Автоматический fallback

## 🛠️ API Endpoints

### **Основные эндпоинты**

```bash
# Маршрутизация AI запросов
POST /route
{
  "task_type": "project_analysis",
  "prompt": "Analyze this project for n8n automation",
  "context": {"technologies": ["python", "fastapi"]}
}

# Специализированный анализ для n8n
POST /n8n/analyze
{
  "prompt": "Create n8n workflow for API integration",
  "context": {"project_path": "/path/to/project"}
}

# Генерация кода
POST /code/generate
{
  "prompt": "Generate Python function for data processing",
  "context": {"language": "python"}
}
```

### **Мониторинг**

```bash
# Проверка здоровья
GET /health

# Проверка Cursor интеграции
GET /cursor/health

# Метрики использования
GET /metrics

# Список провайдеров
GET /providers
```

## 🔍 Мониторинг и отладка

### **Логи AI Router**

```bash
# Просмотр логов AI Router
docker logs rag-ai-router -f

# Проверка статуса Cursor сессии
curl http://localhost:8081/cursor/health
```

### **Метрики использования**

```json
{
  "total_requests": 150,
  "requests_by_provider": {
    "cursor": 120,
    "claude": 25,
    "openai": 5
  },
  "average_response_time": 2.3,
  "error_rate": 0.02,
  "uptime": 86400
}
```

## 🚨 Troubleshooting

### **Проблема: Cursor API недоступен**

```bash
# Проверка API ключа
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.cursor.sh/v1/health

# Решение: Система автоматически переключится на fallback провайдеры
```

### **Проблема: Терминальная сессия не создается**

```bash
# Проверка лимитов Cursor API
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.cursor.sh/v1/sessions

# Решение: Проверьте план подписки Cursor
```

### **Проблема: Медленные ответы**

```bash
# Проверка метрик
curl http://localhost:8081/metrics

# Решение: Настройте таймауты в конфигурации
```

## 🎯 Использование в n8n

### **Автоматическое создание workflow'ов**

```python
# n8n система автоматически использует Cursor для анализа
async def create_n8n_workflow(project_context):
    # Отправка в AI Router
    response = await ai_router.analyze_for_n8n(project_context)
    
    # Создание workflow на основе анализа Cursor
    workflow = await n8n_client.create_workflow(
        suggestions=response.workflow_suggestions,
        api_recommendations=response.api_recommendations
    )
    
    return workflow
```

### **Интеграция с VS Code расширением**

```typescript
// VS Code расширение использует тот же AI Router
class RAGService {
    async analyzeProject(context: ProjectContext) {
        const response = await this.httpClient.post('/n8n/analyze', {
            context: context,
            prompt: "Analyze for n8n automation opportunities"
        });
        
        return response.data;
    }
}
```

## ✅ Заключение

**Cursor интеграция позволяет:**
- 💰 **Экономить деньги** - используете уже купленные подписки
- 🎯 **Получать качество** - те же современные модели
- 🔄 **Автоматизировать** - n8n работает через ваш Cursor
- 🛡️ **Иметь fallback** - если Cursor недоступен

**Идеальное решение для экономии и качества!** 🚀

## 📞 Поддержка

Если у вас возникли проблемы:
1. Проверьте логи: `docker logs rag-ai-router`
2. Проверьте здоровье: `curl http://localhost:8081/health`
3. Проверьте Cursor API: `curl http://localhost:8081/cursor/health`

**Готово к использованию!** 🎉
