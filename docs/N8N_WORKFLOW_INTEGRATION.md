# 🔄 n8n Workflow Integration: Автоматическое создание через API

## 📋 Обзор

Интеграция с n8n API позволяет автоматически создавать workflow'ы для RAG системы, что гораздо логичнее и эффективнее, чем ручное создание. Система автоматически генерирует необходимые workflow'ы для:

- **Автоматической индексации кода** в RAG систему
- **Валидации Spec Kit методологий**
- **Автоматического тестирования**
- **Генерации документации**

## 🏗️ Архитектура интеграции

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Memory Bank   │    │   n8n API       │    │   RAG Proxy     │
│      CLI        │◄──►│   Workflow      │◄──►│    Service      │
│                 │    │   Manager       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │   n8n Workflow  │    │   LightRAG      │
         │              │   Templates     │    │   Service       │
         │              └─────────────────┘    └─────────────────┘
         ▼
┌─────────────────┐
│   VS Code       │
│   Extension     │
└─────────────────┘
```

## 🚀 Использование

### 1. Команды CLI

```bash
# Создание workflow'ов для RAG системы
python memory-bank-cli.py rag setup-workflows --project-path /path/to/project

# Просмотр существующих workflow'ов
python memory-bank-cli.py rag list-workflows

# Полный запуск системы с созданием workflow'ов
python start-full-rag-system.py
```

### 2. Программное использование

```python
from src.cli.services.n8n_workflow_manager import N8nWorkflowManager, create_rag_workflows

# Создание менеджера workflow'ов
manager = N8nWorkflowManager(
    n8n_url="http://localhost:5678",
    username="admin",
    password="admin123"
)

# Аутентификация
await manager.authenticate()

# Создание workflow'а
workflow_id = await manager.create_workflow(template)

# Список workflow'ов
workflows = await manager.list_workflows()

# Запуск workflow'а
await manager.execute_workflow(workflow_id, {"data": "example"})
```

## 📦 Доступные Workflow Templates

### 1. RAG Code Indexing

**Назначение**: Автоматическая индексация кода в RAG систему при изменении файлов

**Компоненты**:
- **Webhook Trigger**: Прием уведомлений об изменении файлов
- **File Processor**: Обработка и анализ кода
- **RAG Proxy Call**: Отправка данных в RAG систему
- **Memory Bank Update**: Обновление контекста Memory Bank

**Использование**:
```bash
# Workflow автоматически активируется при изменении файлов
# VS Code extension отправляет webhook на n8n при сохранении файлов
```

### 2. Spec Kit Validation

**Назначение**: Валидация кода по методологиям Vibecode Spec Kit

**Компоненты**:
- **Manual Trigger**: Запуск валидации вручную
- **Code Analyzer**: Анализ кода на соответствие Spec Kit принципам
- **Validation Report**: Генерация отчета с рекомендациями

**Использование**:
```bash
# Запуск валидации через n8n UI или API
curl -X POST http://localhost:5678/webhook/spec-validation \
  -H "Content-Type: application/json" \
  -d '{"code": "function test() {}", "language": "typescript"}'
```

## 🔧 Конфигурация

### Переменные окружения

```bash
# n8n Configuration
N8N_USER=admin
N8N_PASSWORD=admin123
N8N_URL=http://localhost:5678

# RAG Proxy Configuration  
RAG_PROXY_URL=http://localhost:9000
LIGHTRAG_URL=http://localhost:8000
```

### Настройка Webhook'ов

```javascript
// VS Code Extension отправляет webhook при сохранении файла
const webhookData = {
  file_path: "src/components/UserService.ts",
  content: fileContent,
  language: "typescript",
  project_context: "vibecode_spec_kit"
};

await fetch('http://localhost:5678/webhook/code-changed', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(webhookData)
});
```

## 📊 Workflow Templates в деталях

### RAG Code Indexing Workflow

```json
{
  "name": "RAG Code Indexing",
  "description": "Автоматическая индексация кода в RAG систему",
  "nodes": [
    {
      "id": "webhook-trigger",
      "name": "File Changed",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "code-changed",
        "httpMethod": "POST"
      }
    },
    {
      "id": "file-processor", 
      "name": "Process File",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Обработка файла для RAG индексации..."
      }
    },
    {
      "id": "rag-proxy-call",
      "name": "Index in RAG", 
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://rag-proxy:8000/api/learn",
        "method": "POST"
      }
    }
  ],
  "connections": {
    "webhook-trigger": {
      "main": [["file-processor"]]
    },
    "file-processor": {
      "main": [["rag-proxy-call"]]
    }
  }
}
```

### Spec Kit Validation Workflow

```json
{
  "name": "Spec Kit Validation",
  "description": "Валидация кода по методологиям Spec Kit",
  "nodes": [
    {
      "id": "manual-trigger",
      "name": "Manual Trigger", 
      "type": "n8n-nodes-base.manualTrigger"
    },
    {
      "id": "code-analyzer",
      "name": "Analyze Code",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Анализ кода на Spec Kit соответствие..."
      }
    }
  ]
}
```

## 🔄 API Endpoints

### n8n REST API

```bash
# Аутентификация
POST /rest/login
{
  "email": "admin",
  "password": "admin123"
}

# Создание workflow'а
POST /rest/workflows
{
  "name": "Workflow Name",
  "nodes": [...],
  "connections": {...},
  "active": false
}

# Получение списка workflow'ов
GET /rest/workflows

# Запуск workflow'а
POST /rest/workflows/{id}/execute
{
  "data": {...}
}
```

### Webhook Endpoints

```bash
# Уведомление об изменении файла
POST /webhook/code-changed
{
  "file_path": "src/example.ts",
  "content": "function example() {}",
  "language": "typescript"
}

# Запуск валидации Spec Kit
POST /webhook/spec-validation
{
  "code": "function test() {}",
  "language": "typescript"
}
```

## 🎯 Преимущества API подхода

### 1. **Автоматизация**
- Workflow'ы создаются автоматически при настройке системы
- Нет необходимости в ручном создании через UI
- Легко воспроизводимо для разных проектов

### 2. **Консистентность**
- Все workflow'ы следуют единому шаблону
- Гарантированная совместимость с RAG системой
- Стандартизированная структура

### 3. **Масштабируемость**
- Легко создавать workflow'ы для новых проектов
- Простое добавление новых типов workflow'ов
- Централизованное управление шаблонами

### 4. **Интеграция**
- Полная интеграция с Memory Bank CLI
- Автоматическая настройка при запуске системы
- Единая точка управления всеми workflow'ами

## 🔧 Расширение системы

### Добавление нового типа workflow'а

```python
def get_custom_workflow_template(self) -> WorkflowTemplate:
    """Шаблон для кастомного workflow'а"""
    return WorkflowTemplate(
        name="Custom Workflow",
        description="Описание workflow'а",
        workflow_type=WorkflowType.CUSTOM,
        nodes=[
            # Определение узлов
        ],
        connections={
            # Определение связей
        }
    )

# Добавление в список стандартных workflow'ов
async def setup_default_workflows(self, project_path: str):
    # ... существующие workflow'ы ...
    
    # Добавляем кастомный workflow
    custom_template = self.get_custom_workflow_template()
    workflow_id = await self.create_workflow(custom_template)
```

### Кастомизация существующих workflow'ов

```python
# Переопределение шаблона индексации кода
def get_custom_code_indexing_template(self, project_path: str) -> WorkflowTemplate:
    base_template = self.get_code_indexing_template(project_path)
    
    # Модификация узлов
    base_template.nodes.append({
        "id": "custom-processor",
        "name": "Custom Processing",
        "type": "n8n-nodes-base.function",
        "parameters": {
            "functionCode": "// Кастомная логика обработки"
        }
    })
    
    # Обновление связей
    base_template.connections["rag-proxy-call"]["main"][0].append({
        "node": "custom-processor",
        "type": "main",
        "index": 0
    })
    
    return base_template
```

## 📈 Мониторинг и отладка

### Логи workflow'ов

```bash
# Просмотр логов n8n
docker-compose -f docker-compose-rag.yml logs -f n8n

# Просмотр логов конкретного workflow'а через API
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5678/rest/executions?workflowId=WORKFLOW_ID
```

### Отладка workflow'ов

```bash
# Проверка статуса workflow'ов
python memory-bank-cli.py rag list-workflows

# Тестирование webhook'ов
curl -X POST http://localhost:5678/webhook/code-changed \
  -H "Content-Type: application/json" \
  -d '{"file_path": "test.ts", "content": "test", "language": "typescript"}'
```

## 🎉 Заключение

Интеграция с n8n API обеспечивает:

- ✅ **Автоматическое создание** workflow'ов через код
- ✅ **Консистентную настройку** для всех проектов  
- ✅ **Полную интеграцию** с RAG системой и Spec Kit
- ✅ **Масштабируемость** и легкое расширение
- ✅ **Централизованное управление** через Memory Bank CLI

**Система готова к автоматическому созданию и управлению workflow'ами!** 🚀

---

*Документация создана: 04.10.2025*  
*Версия: 1.0*
