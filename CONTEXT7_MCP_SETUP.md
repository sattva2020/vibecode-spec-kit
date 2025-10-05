# 📚 Context7 MCP Setup Guide

## 🎯 **Обзор**

Context7 MCP (Model Context Protocol) интегрирован в систему для автоматического получения актуальной документации по современным технологиям, библиотекам и API.

## 🔧 **Настройка автоматического одобрения Context7 MCP**

### **Автоматическая настройка (Рекомендуется)**

```powershell
# Запустите PowerShell скрипт
.\scripts\configure-cursor-mcp.ps1

# Или запустите batch файл
.\scripts\setup-cursor-auto-approval.bat
```

### **Что включает Context7 MCP:**

- ✅ `context7:resolve-library-id` - Поиск и резолв библиотек
- ✅ `context7:get-library-docs` - Получение документации библиотек
- ✅ Автоматическое определение актуальных версий
- ✅ Интеграция с современными технологиями

## 📋 **Обновленные конфигурации**

### **1. VS Code Settings (.vscode/settings.json)**
```json
{
  "cursor.mcp.autoApprove": true,
  "cursor.mcp.allowlist": [
    "sequential-thinking:sequentialthinking",
    "memory:*",
    "github:*",
    "filesystem:*",
    "supabase:*",
    "playwright:*",
    "context7:*"
  ],
  "cursor.mcp.trustedTools": [
    "sequential-thinking",
    "memory",
    "github",
    "filesystem",
    "supabase",
    "playwright",
    "context7"
  ]
}
```

### **2. MCP Allowlist (.cursor/mcp-allowlist.json)**
```json
{
  "mcpTools": {
    "allowlist": [
      "sequential-thinking:sequentialthinking",
      "memory:*",
      "github:*",
      "filesystem:*",
      "supabase:*",
      "playwright:*",
      "context7:*"
    ],
    "autoApprove": true
  },
  "toolPermissions": {
    "context7": {
      "*": {
        "autoApprove": true,
        "reason": "Context7 for modern technology documentation and API context"
      }
    }
  }
}
```

## 🚀 **Использование Context7 в проекте**

### **Автоматическое получение документации**

Context7 MCP будет автоматически использоваться для:

1. **Поиска библиотек:**
   ```javascript
   // При упоминании библиотеки автоматически найдется ID
   // Например: "React", "Vue", "Express", "Next.js"
   ```

2. **Получения документации:**
   ```javascript
   // Автоматически получается актуальная документация
   // С акцентом на нужные темы (hooks, routing, etc.)
   ```

3. **Интеграции с Knowledge Base:**
   ```python
   # Автоматическое обогащение графа знаний
   # Современными технологиями и их связями
   ```

### **Примеры использования в коде**

#### **React компонент с Context7:**
```typescript
// Context7 автоматически получит актуальную документацию React
import React, { useState, useEffect } from 'react';

// Документация по хукам будет получена автоматически
const MyComponent = () => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    // Context7 предоставит актуальные примеры useEffect
  }, []);
  
  return <div>{data}</div>;
};
```

#### **Express.js API с Context7:**
```javascript
// Context7 получит актуальную документацию Express
const express = require('express');
const app = express();

// Автоматическое получение лучших практик Express
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
```

## 🔄 **Интеграция с существующей системой**

### **Knowledge Ingestion Pipeline**
```python
# context7_client автоматически используется для:
# - Поиска новых технологий
# - Обогащения знаний
# - Обновления графа технологий

from intelligent_n8n_system.src.knowledge.knowledge_ingestion_pipeline import KnowledgeIngestionPipeline

pipeline = KnowledgeIngestionPipeline()
pipeline.sync_with_context7()  # Автоматическое обновление
```

### **AI Router Integration**
```python
# AI Router автоматически использует Context7 для:
# - Получения контекста технологий
# - Обогащения ответов актуальной документацией
# - Предоставления современных решений

from ai_router.src.services.knowledge_service import KnowledgeService

service = KnowledgeService()
tech_info = service.get_technology_context("react")  # Автоматически через Context7
```

## 📊 **Мониторинг Context7 использования**

### **Метрики для отслеживания:**
- 📈 Количество запросов к Context7
- 📚 Популярные библиотеки/технологии
- ⚡ Время отклика Context7 API
- 🎯 Качество получаемой документации

### **Grafana Dashboard:**
```yaml
# Добавьте в Grafana dashboard метрики:
- context7_requests_total
- context7_library_searches_total
- context7_documentation_quality_score
- context7_api_response_time
```

## 🛠️ **Troubleshooting Context7**

### **Частые проблемы:**

#### 1. Context7 недоступен
```bash
# Проверка доступности
curl -f https://context7.com/health

# Проверка в логах
docker logs rag-ai-router | grep context7
```

#### 2. Медленные запросы
```bash
# Оптимизация кэширования
# Увеличьте timeout в конфигурации
# Проверьте сетевые настройки
```

#### 3. Неточные результаты
```bash
# Обновите версии библиотек
# Проверьте актуальность контекста
# Улучшите промпты для поиска
```

## 🎯 **Преимущества Context7 интеграции**

### **Для разработки:**
- ✅ Актуальная документация автоматически
- ✅ Современные примеры кода
- ✅ Лучшие практики по технологиям
- ✅ Интеграция с Knowledge Base

### **Для системы:**
- ✅ Автоматическое обогащение знаний
- ✅ Актуальная информация о технологиях
- ✅ Улучшенные AI рекомендации
- ✅ Современные n8n интеграции

## 📚 **Дополнительные ресурсы**

- [Context7 Documentation](https://context7.com/docs)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Knowledge Ingestion Pipeline](../intelligent-n8n-system/src/knowledge/)
- [AI Router Integration](../ai-router/src/services/)

---

**Context7 MCP полностью интегрирован и готов к использованию!** 🚀
