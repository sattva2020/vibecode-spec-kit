# 🎯 Subscription Integration Guide - VS Code + GitHub Copilot

## 💡 Концепция

**Используйте ваши платные подписки VS Code + GitHub Copilot для n8n автоматизации!**

Теперь система поддерживает:
- ✅ **Cursor IDE** - ваша платная подписка
- ✅ **GitHub Copilot** - ваша платная подписка VS Code
- ✅ **Fallback на платные API** - Claude, OpenAI (если подписки недоступны)

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    VS Code Ecosystem                       │
│  • Cursor IDE (платная подписка)                           │
│  • GitHub Copilot (платная подписка)                       │
│  • Современные AI модели                                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  AI Router Service                         │
│  • Подключается к вашим подпискам                          │
│  • Маршрутизирует задачи по типу                           │
│  • Автоматический fallback                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  n8n System                                │
│  • Получает анализ через ваши подписки                     │
│  • Создает workflow'ы                                       │
│  • Экономит ваши деньги                                     │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Маршрутизация задач

### **Режимы работы:**

1. **subscription_first** (по умолчанию) - сначала ваши подписки, потом платные API
2. **cursor_only** - только Cursor IDE
3. **copilot_only** - только GitHub Copilot
4. **paid_only** - только платные API (Claude, OpenAI)

### **Правила маршрутизации:**

```python
# n8n и архитектурные задачи
PROJECT_ANALYSIS → Cursor → GitHub Copilot → Claude
WORKFLOW_CREATION → Cursor → GitHub Copilot → Claude
API_INTEGRATION → GitHub Copilot → Cursor → Claude

# Генерация кода
CODE_GENERATION → GitHub Copilot → OpenAI → Claude
REFACTORING → GitHub Copilot → OpenAI → Claude
DEBUGGING → GitHub Copilot → OpenAI → Claude

# Документация
DOCUMENTATION → Cursor → Claude → OpenAI
CODE_REVIEW → Cursor → Claude → OpenAI
```

## ⚙️ Конфигурация

### **Переменные окружения:**

```bash
# AI Router Configuration
AI_PROVIDER_MODE=subscription_first  # subscription_first, paid_only, cursor_only, copilot_only

# Cursor IDE Integration (ВАШИ ПЛАТНЫЕ ПОДПИСКИ!)
CURSOR_API_KEY=your-cursor-api-key
CURSOR_API_URL=https://api.cursor.sh/v1
CURSOR_SESSION_NAME=n8n-ai-router

# GitHub Copilot Integration (ВАША ПЛАТНАЯ ПОДПИСКА!)
GITHUB_COPILOT_API_KEY=your-github-copilot-api-key
GITHUB_COPILOT_API_URL=https://api.githubcopilot.com/v1
GITHUB_COPILOT_SESSION_NAME=n8n-ai-router

# Fallback провайдеры (если подписки недоступны)
ANTHROPIC_API_KEY=your-claude-api-key
OPENAI_API_KEY=your-openai-api-key
```

## 🚀 Быстрая настройка

### **1. Получите API ключи**

#### **Cursor IDE:**
1. Откройте Cursor IDE
2. Settings > Account > API Keys
3. Создайте ключ для "n8n-ai-router"

#### **GitHub Copilot:**
1. Откройте VS Code с GitHub Copilot
2. Settings > Extensions > GitHub Copilot
3. Account > Manage Subscription > API Keys
4. Создайте ключ для "n8n-ai-router"

### **2. Запустите скрипт настройки**

```powershell
# Автоматическая настройка
.\scripts\setup-subscription-integration.ps1

# Или с параметрами
.\scripts\setup-subscription-integration.ps1 -CursorApiKey "key1" -GitHubCopilotApiKey "key2"
```

### **3. Проверьте интеграцию**

```bash
# Проверка здоровья AI Router
curl http://localhost:8081/health

# Проверка провайдеров
curl http://localhost:8081/providers

# Тест n8n анализа
curl -X POST http://localhost:8081/n8n/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze project for n8n automation", "context": {"technologies": ["python", "fastapi"]}}'
```

## 📊 Преимущества

### **💰 Экономия средств**
- ✅ Используете уже купленные подписки
- ✅ Не нужно платить за отдельные AI API
- ✅ Максимальная экономия на n8n автоматизации

### **🎯 Качество**
- ✅ Те же модели, что и в ваших IDE
- ✅ Специализация GitHub Copilot на коде
- ✅ Архитектурное мышление Cursor

### **🔄 Гибкость**
- ✅ Автоматический выбор лучшего провайдера
- ✅ Fallback на платные API при необходимости
- ✅ Настраиваемая маршрутизация

## 🔍 Мониторинг

### **Метрики использования:**

```json
{
  "total_requests": 150,
  "requests_by_provider": {
    "cursor": 60,
    "github_copilot": 45,
    "claude": 30,
    "openai": 15
  },
  "average_response_time": 2.1,
  "error_rate": 0.01,
  "cost_savings": "$45.50"
}
```

### **Health Check:**

```bash
# Общий статус
curl http://localhost:8081/health

# Статус провайдеров
curl http://localhost:8081/providers

# Метрики
curl http://localhost:8081/metrics
```

## 🛠️ API Endpoints

### **Основные эндпоинты:**

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

# Генерация кода (GitHub Copilot приоритет)
POST /code/generate
{
  "prompt": "Generate Python function for data processing",
  "context": {"language": "python", "framework": "fastapi"}
}

# Предложения n8n узлов
POST /n8n/suggest-nodes
{
  "context": {"technologies": ["python", "postgresql", "docker"]}
}
```

## 🎯 Специализация провайдеров

### **Cursor IDE:**
- 🏗️ **Архитектурный анализ** - лучше понимает сложные системы
- 📊 **Структурированный анализ** - анализирует проекты и зависимости
- 🔍 **Длинное контекстное окно** - помнит всю структуру проекта

### **GitHub Copilot:**
- 💻 **Генерация кода** - специализирован на программировании
- 🔧 **Рефакторинг** - понимает паттерны кода
- 🐛 **Отладка** - помогает найти и исправить ошибки
- 🔗 **API интеграции** - знает популярные API и библиотеки

### **Fallback провайдеры:**
- **Claude** - для сложного анализа и архитектуры
- **OpenAI** - для быстрых задач и генерации

## 🚨 Troubleshooting

### **Проблема: Подписки недоступны**

```bash
# Проверка статуса провайдеров
curl http://localhost:8081/providers

# Решение: Система автоматически переключится на fallback
```

### **Проблема: Медленные ответы**

```bash
# Проверка метрик
curl http://localhost:8081/metrics

# Решение: Настройте приоритеты провайдеров
```

### **Проблема: Ошибки аутентификации**

```bash
# Проверка API ключей
curl -H "Authorization: Bearer YOUR_KEY" https://api.cursor.sh/v1/health
curl -H "Authorization: Bearer YOUR_KEY" https://api.githubcopilot.com/v1/models

# Решение: Обновите API ключи в .env файле
```

## 🎯 Использование в n8n

### **Автоматическое создание workflow'ов:**

```python
# n8n система автоматически использует ваши подписки
async def create_n8n_workflow(project_context):
    # Отправка в AI Router (использует ваши подписки)
    response = await ai_router.analyze_for_n8n(project_context)
    
    # Создание workflow на основе анализа
    workflow = await n8n_client.create_workflow(
        suggestions=response.workflow_suggestions,
        api_recommendations=response.api_recommendations,
        node_recommendations=response.node_recommendations
    )
    
    return workflow
```

### **Интеграция с VS Code расширением:**

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
    
    async generateCode(prompt: string, language: string) {
        const response = await this.httpClient.post('/code/generate', {
            prompt: prompt,
            context: { language: language }
        });
        
        return response.data.code;
    }
}
```

## ✅ Заключение

**Интеграция с подписками позволяет:**
- 💰 **Максимально экономить** - используете уже купленные подписки
- 🎯 **Получать качество** - те же современные модели
- 🔄 **Автоматизировать** - n8n работает через ваши подписки
- 🛡️ **Иметь fallback** - если подписки недоступны

**Идеальное решение для экономии и качества!** 🚀

## 📞 Поддержка

Если у вас возникли проблемы:
1. Проверьте логи: `docker logs rag-ai-router`
2. Проверьте здоровье: `curl http://localhost:8081/health`
3. Проверьте провайдеры: `curl http://localhost:8081/providers`

**Готово к использованию с вашими подписками!** 🎉
