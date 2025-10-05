# 🧪 Руководство по тестированию продакшн системы

## 📋 Быстрый старт

### 1. Подготовка к тестированию
```bash
# Клонирование репозитория
git clone <repository-url>
cd vscode-memory-bank

# Установка зависимостей
npm install
pip install -r requirements.txt

# Настройка окружения
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

### 2. Запуск системы
```bash
# Запуск всех сервисов
docker-compose -f docker-compose-rag-system.yml up -d

# Проверка статуса
./scripts/health-check.sh
```

### 3. Выполнение тестов

#### Функциональное тестирование
```bash
# End-to-End тестирование
./scripts/e2e-test.sh

# Проверка здоровья системы
./scripts/health-check.sh
```

#### Нагрузочное тестирование
```bash
# Установка k6 (если не установлен)
# Windows: choco install k6
# macOS: brew install k6
# Linux: apt-get install k6

# Запуск нагрузочного тестирования
k6 run scripts/load-testing/k6-load-test.js
```

#### Мониторинг
```bash
# Настройка мониторинга
./scripts/monitoring-setup.sh

# Запуск мониторинга
./scripts/start-monitoring.sh

# Открыть Grafana: http://localhost:3000 (admin/admin123)
# Открыть Prometheus: http://localhost:9090
```

## 🎯 Типы тестирования

### 1. Функциональное тестирование
- ✅ Проверка всех API endpoints
- ✅ Тестирование аутентификации
- ✅ Проверка работы AI Router
- ✅ Тестирование VS Code Extension
- ✅ Проверка интеграции с n8n

### 2. Нагрузочное тестирование
- ⚡ Тестирование под нагрузкой 200+ пользователей
- ⚡ Проверка времени отклика < 2 секунд
- ⚡ Тестирование fallback механизмов
- ⚡ Проверка использования ресурсов

### 3. Интеграционное тестирование
- 🔗 End-to-End тестирование полного цикла
- 🔗 Проверка взаимодействия между сервисами
- 🔗 Тестирование n8n workflows
- 🔗 Проверка сохранения данных

### 4. Мониторинг и алерты
- 📊 Prometheus метрики
- 📊 Grafana дашборды
- 📊 Алерты для критических событий
- 📊 Мониторинг ресурсов

## 🚨 Критические метрики

### Производительность
- **Время отклика**: < 2 секунды (95% запросов)
- **Пропускная способность**: 1000 запросов/минуту
- **Доступность**: 99.9% uptime
- **Использование CPU**: < 80%
- **Использование памяти**: < 85%

### Качество
- **Успешность запросов**: > 95%
- **Точность AI ответов**: > 90%
- **Качество генерируемого кода**: > 85%
- **Время восстановления**: < 5 минут

## 🔧 Устранение неполадок

### Частые проблемы

#### 1. Сервисы не запускаются
```bash
# Проверка логов
docker-compose logs <service-name>

# Перезапуск сервиса
docker-compose restart <service-name>

# Полный перезапуск
docker-compose down && docker-compose up -d
```

#### 2. Высокое время отклика
```bash
# Проверка ресурсов
docker stats

# Проверка сети
docker network ls
docker network inspect rag-network

# Оптимизация конфигурации
# Увеличьте лимиты в docker-compose.yml
```

#### 3. Ошибки аутентификации
```bash
# Проверка Supabase
curl http://localhost:54321/auth/v1/health

# Проверка JWT токенов
# Убедитесь, что токены не истекли
```

#### 4. Проблемы с AI API
```bash
# Проверка API ключей
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY

# Проверка лимитов API
# Проверьте использование токенов в консоли провайдера
```

## 📊 Анализ результатов

### Успешное тестирование
```
✅ Все сервисы запущены
✅ Время отклика < 2 секунд
✅ Успешность запросов > 95%
✅ Нет критических ошибок
✅ Мониторинг работает
```

### Требуются исправления
```
⚠️  Высокое время отклика (> 5 секунд)
⚠️  Высокое использование ресурсов (> 90%)
⚠️  Частые ошибки в логах
⚠️  Проблемы с AI API
```

### Критические проблемы
```
❌ Сервисы недоступны
❌ Ошибки аутентификации
❌ Потеря данных
❌ Критические алерты
```

## 🔄 Регулярное тестирование

### Ежедневно
- [ ] Проверка здоровья системы
- [ ] Мониторинг метрик
- [ ] Проверка логов на ошибки

### Еженедельно
- [ ] Полное функциональное тестирование
- [ ] Нагрузочное тестирование
- [ ] Проверка backup

### Ежемесячно
- [ ] Полный аудит системы
- [ ] Обновление зависимостей
- [ ] Тестирование восстановления

## 📚 Дополнительные ресурсы

### Документация
- [Production Testing Protocol](PRODUCTION_TESTING_PROTOCOL.md)
- [Health Check Script](scripts/health-check.sh)
- [E2E Test Script](scripts/e2e-test.sh)
- [Load Testing Script](scripts/load-testing/k6-load-test.js)

### Мониторинг
- [Monitoring Setup](scripts/monitoring-setup.sh)
- [Grafana Dashboards](grafana/dashboards/)
- [Prometheus Config](prometheus.yml)
- [Alert Rules](alerts.yml)

### Backup и восстановление
- [Backup Script](scripts/backup-restore.sh)
- [Restore Procedure](PRODUCTION_TESTING_PROTOCOL.md#протокол-восстановления-после-сбоев)

## 🆘 Поддержка

При возникновении проблем:

1. **Проверьте логи**: `docker-compose logs`
2. **Запустите health check**: `./scripts/health-check.sh`
3. **Проверьте мониторинг**: Grafana/Prometheus
4. **Создайте backup**: `./scripts/backup-restore.sh backup`
5. **Обратитесь к документации**: [PRODUCTION_TESTING_PROTOCOL.md](PRODUCTION_TESTING_PROTOCOL.md)

---

**Система готова к продакшн использованию!** 🚀
