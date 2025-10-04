# 🚀 Supabase Integration: RAG-Powered Code Assistant

## 📋 Обзор

Интеграция RAG системы с **Supabase Stack** обеспечивает полнофункциональную backend инфраструктуру с аутентификацией, real-time подписками, файловым хранилищем и мощными API возможностями.

## 🏗️ Supabase Stack Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   VS Code       │    │   Supabase      │    │   RAG System    │
│   Extension     │◄──►│   Kong Gateway  │◄──►│   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │   Supabase      │    │   PostgreSQL    │
         │              │   Services      │    │   + pgvector    │
         │              │                 │    │                 │
         │              │ • Auth          │    │ • RAG Data      │
         │              │ • Storage       │    │ • Spec Kit      │
         │              │ • Realtime      │    │ • Workflows     │
         │              │ • Edge Functions│    │ • Metrics       │
         │              └─────────────────┘    └─────────────────┘
         ▼
┌─────────────────┐
│   Memory Bank   │
│   CLI           │
└─────────────────┘
```

## 🚀 Запуск Supabase RAG системы

### 1. Быстрый старт

```bash
# Клонирование и настройка
git clone <repository>
cd vscode-memory-bank

# Копирование конфигурации
cp supabase-env.example .env
# Отредактируйте .env файл с вашими настройками

# Запуск полной Supabase системы
python start-supabase-rag-system.py
```

### 2. Ручной запуск

```bash
# Запуск Supabase сервисов
docker-compose -f docker-compose-supabase-rag.yml up -d

# Создание n8n workflow'ов
python memory-bank-cli.py rag setup-workflows

# Проверка статуса
python memory-bank-cli.py rag status
```

## 🔧 Supabase сервисы

### Core Services

| Сервис | URL | Описание |
|--------|-----|----------|
| **Kong API Gateway** | http://localhost:8000 | Единая точка входа для всех API |
| **Supabase Studio** | http://localhost:3000 | Web UI для управления проектом |
| **Auth Service** | http://localhost:8000/auth/v1 | Аутентификация и авторизация |
| **Storage Service** | http://localhost:8000/storage/v1 | Файловое хранилище |
| **Realtime Service** | ws://localhost:8000/realtime/v1 | Real-time подписки |
| **Edge Functions** | http://localhost:8000/functions/v1 | Serverless функции |

### RAG Integration Services

| Сервис | URL | Описание |
|--------|-----|----------|
| **RAG Proxy** | http://localhost:9000 | Rust proxy для RAG операций |
| **LightRAG** | http://localhost:8000 | Python RAG сервис |
| **n8n** | http://localhost:5678 | Workflow автоматизация |

## 📊 База данных

### PostgreSQL с pgvector

```sql
-- Основные таблицы RAG системы
CREATE TABLE rag_documents (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    content TEXT NOT NULL,
    language TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE spec_kit_context (
    id SERIAL PRIMARY KEY,
    project_name TEXT NOT NULL,
    mode TEXT NOT NULL,
    context_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE n8n_workflows (
    id SERIAL PRIMARY KEY,
    workflow_id TEXT UNIQUE NOT NULL,
    workflow_name TEXT NOT NULL,
    workflow_type TEXT NOT NULL,
    is_active BOOLEAN DEFAULT false,
    metadata JSONB
);
```

### Vector Search

```sql
-- Поиск похожего кода
SELECT * FROM search_similar_code(
    '[0.1, 0.2, ...]'::vector(1536),
    0.7,  -- similarity threshold
    10    -- max results
);

-- Получение RAG контекста
SELECT * FROM get_rag_context('authentication patterns');
```

## 🔐 Аутентификация

### API Keys

```bash
# Anon Key (публичный доступ)
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Service Role Key (административный доступ)
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Row Level Security (RLS)

```sql
-- Политики безопасности
CREATE POLICY "Service role can do everything" ON rag_documents
FOR ALL TO service_role USING (true);

CREATE POLICY "Anon can read public data" ON rag_documents
FOR SELECT TO anon USING (true);
```

## 🔄 API Endpoints

### RAG Proxy API

```bash
# Health Check
GET http://localhost:9000/health

# Code Suggestions
POST http://localhost:9000/api/suggest
{
  "file_path": "src/auth/user.ts",
  "code": "const user = ",
  "language": "typescript"
}

# Context Search
POST http://localhost:9000/api/search
{
  "query": "authentication patterns",
  "spec_kit_context": "level2"
}

# Learn from Code
POST http://localhost:9000/api/learn
{
  "file_path": "src/auth/user.ts",
  "code": "function login() {}",
  "language": "typescript"
}
```

### Supabase API

```bash
# Supabase REST API
GET http://localhost:8000/rest/v1/rag_documents
Headers:
  apikey: <SUPABASE_ANON_KEY>
  Authorization: Bearer <SUPABASE_ANON_KEY>

# Real-time subscriptions
ws://localhost:8000/realtime/v1/websocket?apikey=<SUPABASE_ANON_KEY>

# Storage API
POST http://localhost:8000/storage/v1/object/upload
```

## 🔄 n8n Workflow Integration

### Supabase Workflow Templates

```javascript
// Workflow для автоматической индексации в Supabase
{
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
      "id": "supabase-insert",
      "name": "Insert to Supabase",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://kong:8000/rest/v1/rag_documents",
        "method": "POST",
        "headers": {
          "apikey": "{{ $env.SUPABASE_ANON_KEY }}",
          "Authorization": "Bearer {{ $env.SUPABASE_ANON_KEY }}"
        }
      }
    }
  ]
}
```

## 📈 Мониторинг и метрики

### System Metrics

```sql
-- Просмотр системных метрик
SELECT * FROM system_metrics 
ORDER BY timestamp DESC 
LIMIT 10;

-- Обновление метрик
SELECT update_system_metric(
    'total_queries_processed',
    150,
    'count',
    '{"component": "rag_proxy"}'
);
```

### Health Checks

```bash
# Проверка статуса всех сервисов
curl http://localhost:8000/rest/v1/
curl http://localhost:9000/health
curl http://localhost:5678/healthz
curl http://localhost:3000/api/profile
```

## 🛠️ Разработка

### Локальная разработка

```bash
# Запуск только Supabase
docker-compose -f docker-compose-supabase-rag.yml up -d kong db auth rest realtime storage

# Запуск RAG сервисов
docker-compose -f docker-compose-supabase-rag.yml up -d lightrag rag-proxy n8n

# Просмотр логов
docker-compose -f docker-compose-supabase-rag.yml logs -f rag-proxy
```

### Edge Functions

```typescript
// supabase/functions/rag-process/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  const { file_path, code, language } = await req.json()
  
  // Обработка RAG запроса
  const embedding = await generateEmbedding(code)
  
  return new Response(
    JSON.stringify({ embedding, processed: true }),
    { headers: { "Content-Type": "application/json" } }
  )
})
```

## 🔧 Конфигурация

### Environment Variables

```bash
# Supabase Configuration
SUPABASE_URL=http://localhost:8000
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# Database
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=postgres

# JWT
JWT_SECRET=your_jwt_secret
JWT_EXPIRY=3600

# n8n
N8N_USER=admin
N8N_PASSWORD=secure_password

# RAG System
RAG_MAX_SUGGESTIONS=10
RAG_TIMEOUT_SECONDS=30
RAG_ENABLE_CACHING=true
```

### Kong Gateway Routes

```yaml
# supabase/kong.yml
services:
  - name: rag-proxy
    url: http://rag-proxy:8000/
    routes:
      - name: rag-proxy-all
        strip_path: true
        paths:
          - /api/
```

## 📊 Преимущества Supabase интеграции

### 1. **Полнофункциональная Backend**
- ✅ Аутентификация и авторизация
- ✅ Real-time подписки
- ✅ Файловое хранилище
- ✅ Serverless функции

### 2. **Масштабируемость**
- ✅ Автоматическое масштабирование
- ✅ CDN для статических файлов
- ✅ Connection pooling
- ✅ Горизонтальное масштабирование

### 3. **Безопасность**
- ✅ Row Level Security (RLS)
- ✅ JWT токены
- ✅ API ключи
- ✅ HTTPS/TLS

### 4. **Developer Experience**
- ✅ Supabase Studio UI
- ✅ TypeScript типы
- ✅ Real-time подписки
- ✅ Edge Functions

### 5. **Интеграция**
- ✅ REST API
- ✅ GraphQL API
- ✅ Real-time WebSocket
- ✅ PostgreSQL расширения

## 🎯 Использование

### VS Code Extension

```typescript
// Автоматическая отправка в Supabase
const supabase = createClient(
  'http://localhost:8000',
  'your_anon_key'
)

// Сохранение кода в RAG
await supabase
  .from('rag_documents')
  .insert({
    file_path: document.fileName,
    content: document.getText(),
    language: document.languageId
  })
```

### CLI Integration

```bash
# Создание workflow'ов для Supabase
python memory-bank-cli.py rag setup-workflows --project-path /path/to/project

# Проверка статуса Supabase
python memory-bank-cli.py rag status

# Поиск в Supabase
python memory-bank-cli.py rag search "authentication patterns"
```

## 🎉 Заключение

**Supabase интеграция обеспечивает:**

- ✅ **Полнофункциональную backend инфраструктуру**
- ✅ **Масштабируемость и производительность**
- ✅ **Безопасность и надежность**
- ✅ **Отличный developer experience**
- ✅ **Полную интеграцию с RAG системой**

**Система готова к production использованию с Supabase Stack!** 🚀

---

*Документация создана: 04.10.2025*  
*Версия: 1.0*
