# 🐳 Docker Usage Guide

## Основной Docker Compose файл

**Используйте только**: `docker-compose-rag-system.yml`

## 🚀 Быстрый старт

```bash
# 1. Скопировать переменные окружения
cp env.rag-system.example .env

# 2. Запустить все сервисы
docker-compose -f docker-compose-rag-system.yml up -d

# 3. Проверить статус
docker-compose -f docker-compose-rag-system.yml ps
```

## 📊 Сервисы и порты

| Сервис | Порт | Назначение |
|--------|------|------------|
| **Supabase DB** | 5432 | PostgreSQL + pgvector |
| **Supabase Kong** | 8000 | API Gateway |
| **Supabase Realtime** | 4000 | Real-time подписки |
| **Ollama** | 11434 | Локальные LLM модели |
| **LightRAG** | 8001 | Knowledge Graph |
| **n8n** | 5678 | Workflow Engine |
| **Intelligent n8n API** | 8002 | AI API |
| **RAG Proxy** | 8080 | Rust Proxy |
| **Prometheus** | 9090 | Мониторинг |
| **Grafana** | 3000 | Дашборды |

## 🔧 Управление сервисами

```bash
# Запуск
docker-compose -f docker-compose-rag-system.yml up -d

# Остановка
docker-compose -f docker-compose-rag-system.yml down

# Перезапуск конкретного сервиса
docker-compose -f docker-compose-rag-system.yml restart ollama

# Просмотр логов
docker-compose -f docker-compose-rag-system.yml logs -f ollama

# Обновление образов
docker-compose -f docker-compose-rag-system.yml pull
```

## 🏥 Проверка здоровья

```bash
# Проверить все healthchecks
docker-compose -f docker-compose-rag-system.yml ps

# Тест интеграции
python test-rag-integration.py
```

## 📝 Переменные окружения

Основные переменные в `.env`:

```bash
# Database
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
POSTGRES_USER=postgres

# Supabase
SUPABASE_ANON_KEY=your-anon-key
JWT_SECRET=your-jwt-secret

# n8n
N8N_USER=admin
N8N_PASSWORD=password
N8N_ENCRYPTION_KEY=your-encryption-key

# Monitoring
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin

# Logging
LOG_LEVEL=INFO
```

## 🗑️ Удаленные файлы

Следующие файлы были удалены как устаревшие:
- `docker-compose-rag.yml` - упрощенная версия без Ollama
- `docker-compose-supabase-rag.yml` - избыточный полный Supabase стек

## ⚠️ Важные замечания

1. **Используйте только** `docker-compose-rag-system.yml`
2. **Всегда проверяйте** healthchecks перед использованием
3. **Мониторинг** доступен в Grafana: http://localhost:3000
4. **Логи** можно просматривать через `docker-compose logs`

## 🔍 Troubleshooting

```bash
# Проверить доступность портов
netstat -an | findstr ":5432\|:11434\|:5678\|:8000\|:8080"

# Проверить использование ресурсов
docker stats

# Очистить неиспользуемые образы
docker system prune -a
```
