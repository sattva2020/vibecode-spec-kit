# 🎯 Cursor IDE Integration Architecture

## 💡 Концепция

**Использовать ваши платные подписки Cursor IDE для n8n взаимодействия!**

### **Как это работает:**
1. **Cursor IDE** - у вас уже есть платная подписка с современными моделями
2. **AI Router** - подключается к Cursor API как отдельная терминальная сессия
3. **n8n взаимодействие** - использует те же модели, что и ваш IDE
4. **Экономия** - не нужно платить отдельно за AI API

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    Cursor IDE                               │
│  • Ваша платная подписка                                    │
│  • Современные модели (Claude, GPT-4, etc.)                │
│  • Cursor API для терминальных сессий                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  AI Router Service                         │
│  • Подключается к Cursor API                               │
│  • Использует ваши подписки                                │
│  • Маршрутизирует n8n задачи                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  n8n System                                │
│  • Получает AI анализ через Cursor                         │
│  • Создает workflow'ы                                       │
│  • Использует ваши платные модели                           │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Реализация

### **1. Cursor API Client**

```python
class CursorAPIClient:
    def __init__(self, cursor_api_key: str):
        self.api_key = cursor_api_key
        self.base_url = "https://api.cursor.sh/v1"
        self.session_id = self._create_terminal_session()
    
    async def _create_terminal_session(self) -> str:
        """Создает отдельную терминальную сессию для n8n"""
        response = await self._post("/sessions/terminal", {
            "name": "n8n-ai-router",
            "type": "automation",
            "description": "AI Router для n8n workflow'ов"
        })
        return response["session_id"]
    
    async def analyze_for_n8n(self, project_context: dict) -> dict:
        """Анализ проекта для n8n через Cursor"""
        prompt = self._build_n8n_prompt(project_context)
        
        response = await self._post(f"/sessions/{self.session_id}/chat", {
            "messages": [
                {"role": "system", "content": "Ты эксперт по n8n workflow'ам"},
                {"role": "user", "content": prompt}
            ],
            "model": "claude-3.5-sonnet",  # Использует вашу подписку
            "temperature": 0.1
        })
        
        return self._parse_n8n_response(response)
```

### **2. Обновленный AI Router**

```python
class AIRouter:
    def __init__(self):
        self.cursor_client = CursorAPIClient(os.getenv("CURSOR_API_KEY"))
        self.fallback_providers = {
            "claude": ClaudeClient(),
            "openai": OpenAIClient()
        }
    
    async def route_n8n_request(self, request: N8nRequest) -> N8nResponse:
        """Маршрутизация n8n запросов через Cursor"""
        try:
            # Пытаемся использовать Cursor API
            response = await self.cursor_client.analyze_for_n8n(request.context)
            response.provider = "cursor"
            return response
            
        except Exception as e:
            # Fallback на платные API
            return await self._fallback_to_paid_api(request)
```

### **3. Конфигурация**

```bash
# Cursor IDE Integration
CURSOR_API_KEY=your-cursor-api-key
CURSOR_API_URL=https://api.cursor.sh/v1
CURSOR_SESSION_NAME=n8n-ai-router

# Fallback providers (если Cursor недоступен)
ANTHROPIC_API_KEY=your-claude-key
OPENAI_API_KEY=your-openai-key

# Режим работы
AI_PROVIDER_MODE=cursor_first  # cursor_first, paid_only, cursor_only
```

## 🚀 Преимущества

### **Экономия средств**
- ✅ Используете уже купленные подписки
- ✅ Не нужно платить за отдельные AI API
- ✅ Один аккаунт для всех задач

### **Единообразие**
- ✅ Те же модели, что и в IDE
- ✅ Одинаковое качество анализа
- ✅ Консистентные результаты

### **Простота**
- ✅ Один API ключ для всего
- ✅ Не нужно управлять множественными подписками
- ✅ Автоматический fallback

## 🔄 Workflow

### **1. Инициализация**
```bash
# Создание терминальной сессии в Cursor
curl -X POST https://api.cursor.sh/v1/sessions/terminal \
  -H "Authorization: Bearer $CURSOR_API_KEY" \
  -d '{"name": "n8n-ai-router"}'
```

### **2. Анализ проекта**
```python
# AI Router отправляет запрос в Cursor
response = await cursor_client.analyze_project({
    "project_path": "/path/to/project",
    "technologies": ["python", "fastapi", "postgresql"],
    "task_type": "workflow_creation"
})
```

### **3. Создание n8n workflow**
```python
# Cursor возвращает анализ, AI Router создает workflow
workflow = await n8n_client.create_workflow(
    analysis=response.workflow_suggestions,
    project_context=request.context
)
```

## 📊 Мониторинг

### **Метрики использования Cursor**
```python
class CursorMetrics:
    def __init__(self):
        self.sessions_created = 0
        self.requests_processed = 0
        self.fallback_usage = 0
        self.cursor_api_errors = 0
```

### **Health Check**
```python
@app.get("/cursor/health")
async def cursor_health():
    """Проверка доступности Cursor API"""
    try:
        status = await cursor_client.check_health()
        return {
            "cursor_api": "healthy" if status else "unavailable",
            "session_id": cursor_client.session_id,
            "fallback_mode": cursor_client.fallback_mode
        }
    except Exception as e:
        return {"cursor_api": "error", "error": str(e)}
```

## 🎯 Итоговая архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    Cursor IDE (Ваша подписка)               │
│  • Claude 3.5 Sonnet                                        │
│  • GPT-4 Turbo                                              │
│  • Cursor API                                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  AI Router Service                         │
│  • Cursor API Client                                       │
│  • Терминальная сессия "n8n-ai-router"                     │
│  • Fallback на платные API                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  n8n System                                │
│  • Получает анализ через Cursor                            │
│  • Создает workflow'ы                                       │
│  • Использует ваши модели                                   │
└─────────────────────────────────────────────────────────────┘
```

## ✅ Заключение

**Эта архитектура позволяет:**
- 💰 **Экономить деньги** - используете уже купленные подписки
- 🎯 **Получать качество** - те же современные модели
- 🔄 **Автоматизировать** - n8n работает через ваш Cursor
- 🛡️ **Иметь fallback** - если Cursor недоступен

**Идеальное решение для экономии и качества!** 🚀
