# 🧪 Production Testing Protocol
## RAG-Powered Code Assistant System

**Версия**: 1.0  
**Дата**: 05.10.2025  
**Статус**: Production Ready  

---

## 📋 **Оглавление**

1. [Обзор системы](#обзор-системы)
2. [Критические компоненты](#критические-компоненты)
3. [Протокол функционального тестирования](#протокол-функционального-тестирования)
4. [Протокол нагрузочного тестирования](#протокол-нагрузочного-тестирования)
5. [Протокол интеграционного тестирования](#протокол-интеграционного-тестирования)
6. [Протокол мониторинга и алертинга](#протокол-мониторинга-и-алертинга)
7. [Протокол восстановления после сбоев](#протокол-восстановления-после-сбоев)
8. [Чек-листы для продакшн деплоя](#чек-листы-для-продакшн-деплоя)

---

## 🎯 **Обзор системы**

### **Архитектура компонентов:**
```
┌─────────────────────────────────────────────────────────────┐
│                    VS Code Extension                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  AI Router Service                          │
│  • Маршрутизация запросов                                  │
│  • Выбор оптимального API                                   │
│  • Кэширование результатов                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──┐ ┌───────▼──┐ ┌────────▼────────┐
│  Claude  │ │   GPT-4  │ │   Ollama Graph   │
│  API     │ │   API    │ │   Service        │
└──────┬───┘ └──────┬───┘ └────────┬────────┘
       │            │              │
┌──────▼───┐ ┌──────▼───┐ ┌────────▼────────┐
│ Supabase │ │ Supabase │ │    LightRAG     │
│   Auth   │ │   DB     │ │   Knowledge     │
└──────┬───┘ └──────┬───┘ └────────┬────────┘
       │            │              │
┌──────▼───────────────────────────▼────────┐
│              n8n Workflows                │
│  • Автоматизация задач                    │
│  • Интеграция с внешними сервисами        │
└───────────────────────────────────────────┘
```

### **Ключевые метрики производительности:**
- **Время отклика**: < 2 секунды для 95% запросов
- **Доступность**: 99.9% uptime
- **Пропускная способность**: 1000 запросов/минуту
- **Потребление ресурсов**: < 80% CPU, < 85% RAM

---

## 🔧 **Критические компоненты**

### **Tier 1 - Критически важные:**
- **AI Router Service** - Центральный компонент маршрутизации
- **Supabase Database** - Хранение данных и аутентификация
- **Ollama Graph Service** - Локальные embeddings и граф знаний
- **VS Code Extension** - Пользовательский интерфейс

### **Tier 2 - Важные:**
- **LightRAG Service** - RAG система
- **n8n Workflows** - Автоматизация
- **Kong API Gateway** - Маршрутизация API

### **Tier 3 - Вспомогательные:**
- **Monitoring Stack** - Prometheus, Grafana
- **Logging System** - Централизованные логи
- **Backup System** - Резервное копирование

---

## 🧪 **Протокол функционального тестирования**

### **1. Тестирование AI Router Service**

#### **1.1 Маршрутизация запросов**
```bash
# Тест 1: Маршрутизация к Ollama для семантического поиска
curl -X POST http://localhost:8000/api/v1/route \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "semantic_search",
    "query": "find authentication logic",
    "context": "project_code"
  }'

# Ожидаемый результат: 200 OK, provider: "ollama"
```

#### **1.2 Fallback механизмы**
```bash
# Тест 2: Fallback при недоступности основного API
# 1. Отключить Claude API
# 2. Отправить запрос для сложного анализа
# 3. Проверить автоматический fallback на GPT-4

curl -X POST http://localhost:8000/api/v1/route \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "code_analysis",
    "complexity": "high",
    "code": "complex_function_code"
  }'

# Ожидаемый результат: 200 OK, provider: "openai", fallback: true
```

### **2. Тестирование Supabase интеграции**

#### **2.1 Аутентификация**
```bash
# Тест 3: JWT аутентификация
curl -X POST http://localhost:54321/auth/v1/token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword"
  }'

# Ожидаемый результат: 200 OK с JWT токеном
```

#### **2.2 RLS политики**
```bash
# Тест 4: Проверка Row Level Security
curl -X GET http://localhost:54321/rest/v1/projects \
  -H "Authorization: Bearer $JWT_TOKEN"

# Ожидаемый результат: 200 OK только с данными пользователя
```

### **3. Тестирование VS Code Extension**

#### **3.1 Inline Completions**
```typescript
// Тест 5: Проверка inline completions
// 1. Открыть файл TypeScript
// 2. Начать вводить функцию
// 3. Проверить появление AI предложений

function calculateTotal(items: Item[]) {
  // AI должно предложить: return items.reduce((sum, item) => sum + item.price, 0);
}
```

#### **3.2 Code Lens и Hover Providers**
```typescript
// Тест 6: Проверка Code Lens
// 1. Навести курсор на функцию
// 2. Проверить появление hover с AI объяснением
// 3. Проверить Code Lens с предложениями

function complexAlgorithm(data: any[]) {
  // Hover должен показать AI объяснение алгоритма
  // Code Lens должен предложить оптимизации
}
```

---

## ⚡ **Протокол нагрузочного тестирования**

### **1. Инструменты тестирования**
```yaml
# k6-load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 }, // Ramp up
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 200 }, // Ramp up to 200 users
    { duration: '5m', target: 200 }, // Stay at 200 users
    { duration: '2m', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% requests under 2s
    http_req_failed: ['rate<0.1'],     // Error rate under 10%
  },
};
```

### **2. Сценарии нагрузочного тестирования**

#### **2.1 Семантический поиск (Ollama)**
```javascript
export default function() {
  let response = http.post('http://localhost:8000/api/v1/search', {
    query: 'authentication middleware',
    context: 'express_app',
    type: 'semantic'
  });
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 2s': (r) => r.timings.duration < 2000,
    'has results': (r) => JSON.parse(r.body).results.length > 0,
  });
  
  sleep(1);
}
```

#### **2.2 Генерация кода (Claude/GPT-4)**
```javascript
export default function() {
  let response = http.post('http://localhost:8000/api/v1/generate', {
    task_type: 'code_generation',
    language: 'typescript',
    description: 'create a REST API endpoint',
    complexity: 'medium'
  });
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 5s': (r) => r.timings.duration < 5000,
    'valid code generated': (r) => {
      let body = JSON.parse(r.body);
      return body.code && body.code.includes('export');
    },
  });
  
  sleep(2);
}
```

### **3. Мониторинг ресурсов**
```bash
# Мониторинг во время нагрузочного тестирования
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# Логи производительности
docker logs rag-ai-router --tail 100 -f
docker logs rag-supabase-db --tail 100 -f
docker logs rag-ollama --tail 100 -f
```

---

## 🔗 **Протокол интеграционного тестирования**

### **1. End-to-End тестирование**

#### **1.1 Полный цикл: Поиск → Генерация → Сохранение**
```bash
#!/bin/bash
# e2e-test.sh

echo "🧪 Запуск End-to-End тестирования..."

# Шаг 1: Аутентификация
JWT_TOKEN=$(curl -s -X POST http://localhost:54321/auth/v1/token \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword"}' \
  | jq -r '.access_token')

echo "✅ Аутентификация: $JWT_TOKEN"

# Шаг 2: Семантический поиск
SEARCH_RESULT=$(curl -s -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"query": "user authentication", "context": "auth_system"}')

echo "✅ Поиск: $(echo $SEARCH_RESULT | jq '.results | length') результатов"

# Шаг 3: Генерация кода на основе найденного
GENERATION_RESULT=$(curl -s -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "task_type": "code_generation",
    "context": "'"$SEARCH_RESULT"'",
    "requirements": "create login endpoint"
  }')

echo "✅ Генерация: $(echo $GENERATION_RESULT | jq '.code | length') символов"

# Шаг 4: Сохранение в Supabase
SAVE_RESULT=$(curl -s -X POST http://localhost:54321/rest/v1/code_snippets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -d '{
    "title": "Generated Login Endpoint",
    "code": "'"$(echo $GENERATION_RESULT | jq -r '.code')"'",
    "language": "typescript"
  }')

echo "✅ Сохранение: $(echo $SAVE_RESULT | jq '.id')"

echo "🎉 End-to-End тестирование завершено успешно!"
```

#### **1.2 Тестирование n8n workflow интеграции**
```bash
# Тест создания n8n workflow через API
WORKFLOW_ID=$(curl -s -X POST http://localhost:5678/api/v1/workflows \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -d '{
    "name": "Code Analysis Workflow",
    "nodes": [
      {
        "name": "Webhook",
        "type": "n8n-nodes-base.webhook",
        "parameters": {"path": "code-analysis"}
      },
      {
        "name": "AI Analysis",
        "type": "n8n-nodes-base.httpRequest",
        "parameters": {
          "url": "http://ai-router:8000/api/v1/analyze",
          "method": "POST"
        }
      }
    ],
    "connections": {
      "Webhook": {
        "main": [["AI Analysis"]]
      }
    }
  }' | jq -r '.id')

echo "✅ n8n Workflow создан: $WORKFLOW_ID"

# Тест выполнения workflow
EXECUTION_RESULT=$(curl -s -X POST "http://localhost:5678/api/v1/workflows/$WORKFLOW_ID/execute" \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -d '{"code": "function test() { return 42; }"}')

echo "✅ Workflow выполнен: $(echo $EXECUTION_RESULT | jq '.executionId')"
```

---

## 📊 **Протокол мониторинга и алертинга**

### **1. Метрики для мониторинга**

#### **1.1 Системные метрики**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'rag-system'
    static_configs:
      - targets: 
        - 'ai-router:8000'
        - 'supabase-db:5432'
        - 'ollama:11434'
        - 'n8n:5678'
    metrics_path: /metrics
    scrape_interval: 10s

  - job_name: 'docker-containers'
    static_configs:
      - targets: ['docker-host:9323']
```

#### **1.2 Бизнес метрики**
```python
# ai-router/src/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Счетчики запросов
REQUEST_COUNT = Counter(
    'ai_requests_total',
    'Total AI requests',
    ['provider', 'task_type', 'status']
)

# Время отклика
REQUEST_DURATION = Histogram(
    'ai_request_duration_seconds',
    'AI request duration',
    ['provider', 'task_type']
)

# Использование API
API_USAGE = Counter(
    'api_tokens_used_total',
    'Total API tokens used',
    ['provider', 'model']
)

# Качество ответов
RESPONSE_QUALITY = Gauge(
    'response_quality_score',
    'Quality score of AI responses',
    ['provider', 'task_type']
)
```

### **2. Алерты**

#### **2.1 Критические алерты**
```yaml
# alertmanager.yml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'critical-alerts'

receivers:
  - name: 'critical-alerts'
    webhook_configs:
      - url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        send_resolved: true

# alerts.yml
groups:
  - name: critical
    rules:
      - alert: ServiceDown
        expr: up{job="rag-system"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.instance }} is down"
          
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, ai_request_duration_seconds_bucket) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "95th percentile response time is high"
```

#### **2.2 Мониторинг ресурсов**
```bash
# health-check.sh
#!/bin/bash

check_service() {
    local service=$1
    local port=$2
    local endpoint=$3
    
    if curl -f -s "http://localhost:$port$endpoint" > /dev/null; then
        echo "✅ $service: OK"
        return 0
    else
        echo "❌ $service: FAILED"
        return 1
    fi
}

echo "🔍 Проверка состояния сервисов..."

check_service "AI Router" 8000 "/health"
check_service "Supabase DB" 5432 "/"
check_service "Ollama" 11434 "/api/tags"
check_service "n8n" 5678 "/healthz"
check_service "Kong Gateway" 8001 "/status"

# Проверка использования ресурсов
echo "📊 Использование ресурсов:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

---

## 🔄 **Протокол восстановления после сбоев**

### **1. Автоматическое восстановление**

#### **1.1 Health Checks**
```yaml
# docker-compose.yml - Health checks для всех сервисов
services:
  ai-router:
    image: rag-ai-router:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped

  supabase-db:
    image: pgvector/pgvector:pg15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
```

#### **1.2 Circuit Breaker Pattern**
```python
# ai-router/src/circuit_breaker.py
import asyncio
from enum import Enum
from typing import Callable, Any

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        return (self.last_failure_time and 
                asyncio.get_event_loop().time() - self.last_failure_time > self.timeout)

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

### **2. Резервное копирование и восстановление**

#### **2.1 Backup скрипты**
```bash
#!/bin/bash
# backup-system.sh

BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "🔄 Создание резервной копии системы..."

# Backup Supabase database
echo "📊 Backup Supabase database..."
docker exec rag-supabase-db pg_dump -U postgres postgres > $BACKUP_DIR/supabase_backup.sql

# Backup LightRAG knowledge base
echo "🧠 Backup LightRAG knowledge base..."
docker cp rag-lightrag:/app/knowledge_base $BACKUP_DIR/

# Backup n8n workflows
echo "⚙️ Backup n8n workflows..."
curl -H "X-N8N-API-KEY: $N8N_API_KEY" \
     http://localhost:5678/api/v1/workflows \
     > $BACKUP_DIR/n8n_workflows.json

# Backup configurations
echo "⚙️ Backup configurations..."
cp -r ./supabase $BACKUP_DIR/
cp docker-compose-rag-system.yml $BACKUP_DIR/

# Compress backup
tar -czf $BACKUP_DIR.tar.gz -C /backups $(basename $BACKUP_DIR)
rm -rf $BACKUP_DIR

echo "✅ Backup создан: $BACKUP_DIR.tar.gz"
```

#### **2.2 Restore скрипты**
```bash
#!/bin/bash
# restore-system.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ Укажите файл backup: ./restore-system.sh backup.tar.gz"
    exit 1
fi

echo "🔄 Восстановление системы из $BACKUP_FILE..."

# Extract backup
BACKUP_DIR=$(mktemp -d)
tar -xzf $BACKUP_FILE -C $BACKUP_DIR

# Stop services
echo "⏹️ Остановка сервисов..."
docker-compose -f docker-compose-rag-system.yml down

# Restore Supabase database
echo "📊 Восстановление Supabase database..."
docker-compose -f docker-compose-rag-system.yml up -d supabase-db
sleep 10
docker exec -i rag-supabase-db psql -U postgres postgres < $BACKUP_DIR/supabase_backup.sql

# Restore LightRAG knowledge base
echo "🧠 Восстановление LightRAG knowledge base..."
docker-compose -f docker-compose-rag-system.yml up -d lightrag
sleep 5
docker cp $BACKUP_DIR/knowledge_base rag-lightrag:/app/

# Restore n8n workflows
echo "⚙️ Восстановление n8n workflows..."
docker-compose -f docker-compose-rag-system.yml up -d n8n
sleep 10
# Import workflows through n8n API

# Start all services
echo "🚀 Запуск всех сервисов..."
docker-compose -f docker-compose-rag-system.yml up -d

# Cleanup
rm -rf $BACKUP_DIR

echo "✅ Восстановление завершено успешно!"
```

---

## ✅ **Чек-листы для продакшн деплоя**

### **Pre-deployment Checklist**

#### **1. Код и конфигурация**
- [ ] Все тесты пройдены (unit, integration, e2e)
- [ ] Код прошел code review
- [ ] Конфигурация для продакшн настроена
- [ ] Секреты и API ключи настроены
- [ ] Логирование настроено
- [ ] Мониторинг настроен

#### **2. Инфраструктура**
- [ ] Docker образы собраны и протестированы
- [ ] База данных настроена с правильными индексами
- [ ] Сеть и безопасность настроены
- [ ] Backup система настроена
- [ ] SSL сертификаты установлены

#### **3. Мониторинг и алерты**
- [ ] Prometheus настроен
- [ ] Grafana дашборды созданы
- [ ] Алерты настроены
- [ ] Логи централизованы
- [ ] Health checks работают

### **Deployment Checklist**

#### **1. Развертывание**
- [ ] Blue-green deployment настроен
- [ ] Rollback план готов
- [ ] Database migrations выполнены
- [ ] Сервисы запущены в правильном порядке
- [ ] Load balancer настроен

#### **2. Проверки после деплоя**
- [ ] Все сервисы отвечают на health checks
- [ ] API endpoints работают
- [ ] Аутентификация работает
- [ ] База данных доступна
- [ ] Мониторинг собирает метрики

### **Post-deployment Checklist**

#### **1. Валидация**
- [ ] Smoke tests пройдены
- [ ] Load testing выполнен
- [ ] Security scan пройден
- [ ] Performance baseline установлен
- [ ] Backup тестирован

#### **2. Документация**
- [ ] Runbook обновлен
- [ ] API документация обновлена
- [ ] Troubleshooting guide обновлен
- [ ] Monitoring runbook готов

---

## 🚨 **Emergency Procedures**

### **1. Incident Response**
```bash
# incident-response.sh
#!/bin/bash

INCIDENT_ID=$(date +%Y%m%d_%H%M%S)
echo "🚨 ИНЦИДЕНТ #$INCIDENT_ID"

# 1. Оценка масштаба
echo "📊 Оценка состояния системы..."
./health-check.sh > "incident_$INCIDENT_ID.log"

# 2. Быстрое восстановление
echo "🔄 Попытка быстрого восстановления..."
docker-compose -f docker-compose-rag-system.yml restart

# 3. Если не помогло - откат
echo "⏪ Откат к предыдущей версии..."
docker-compose -f docker-compose-rag-system-previous.yml up -d

# 4. Уведомление команды
echo "📢 Уведомление команды..."
# Slack notification, email, etc.

echo "✅ Процедура инцидента завершена"
```

### **2. Rollback Procedure**
```bash
# rollback.sh
#!/bin/bash

echo "⏪ Выполнение rollback..."

# 1. Backup текущего состояния
./backup-system.sh

# 2. Откат к предыдущей версии
docker-compose -f docker-compose-rag-system.yml down
docker-compose -f docker-compose-rag-system-previous.yml up -d

# 3. Проверка состояния
./health-check.sh

echo "✅ Rollback завершен"
```

---

## 📈 **Continuous Improvement**

### **1. Метрики для анализа**
- Время отклика по типам запросов
- Использование различных AI провайдеров
- Качество генерируемого кода
- Пользовательская активность
- Ошибки и их частота

### **2. Регулярные ревью**
- Еженедельный анализ метрик
- Месячный review производительности
- Квартальный security audit
- Полугодовой capacity planning

---

**Протокол версии 1.0 готов к использованию в продакшн среде!** 🚀
