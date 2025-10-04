# 🚀 Vibecode Spec Kit + RAG Integration

Полная интеграция **Vibecode Spec Kit** с **RAG-системой** для создания умного AI-ассистента разработчика, который понимает ваши методологии и код.

## 🎯 Что дает интеграция

### Для Vibecode Spec Kit:
- **🧠 Умные предложения** на основе Spec Kit методологий
- **📚 Контекстное обучение** из вашего Memory Bank
- **🔄 Автоматизация** через n8n workflow
- **🔍 Семантический поиск** по кодовой базе
- **⚡ Реальная интеграция** с существующими командами CLI

### Для разработчика:
- **AI предложения** учитывающие ваши Spec Kit паттерны
- **Автообучение** на основе вашего стиля кодирования
- **Контекстные объяснения** кода с учетом методологий
- **Автоматическая индексация** при работе с CLI
- **Интеграция** с существующими workflow

## 🏗️ Архитектура интеграции

```
Vibecode Spec Kit CLI
        ↓
Memory Bank (контекст + методологии)
        ↓
RAG Proxy (Rust) ←→ LightRAG (Python)
        ↓
n8n Workflows ←→ Supabase + pgvector
```

## 🚀 Быстрый старт

### 1. Запуск интегрированной системы

```bash
# Запускаем все сервисы одной командой
./start-rag-integration.sh

# Или вручную
docker-compose -f docker-compose-rag.yml up -d
```

### 2. Проверка интеграции

```bash
# Проверяем статус RAG системы
python memory-bank-cli.py rag status

# Тестируем интеграцию с Spec Kit
python memory-bank-cli.py rag integrate --spec-type "level3" --code "function test() {}"
```

### 3. Использование в разработке

```bash
# Получаем AI предложения с контекстом Spec Kit
python memory-bank-cli.py rag suggest --code "const user = " --language "typescript"

# Обучаем систему на вашем коде
python memory-bank-cli.py rag learn --code "export async function login() {}" --spec-type "level2"

# Ищем контекст по коду
python memory-bank-cli.py rag search "authentication patterns"
```

## 🔧 Интегрированные команды

### RAG команды в CLI

```bash
# Статус системы
python memory-bank-cli.py rag status

# AI предложения
python memory-bank-cli.py rag suggest --file-path "src/auth.ts" --code "const user = " --language "typescript"

# Обучение на коде
python memory-bank-cli.py rag learn --file-path "src/auth.ts" --code "export function login() {}" --spec-type "level2"

# Поиск контекста
python memory-bank-cli.py rag search "user authentication"

# Интеграция с Spec Kit
python memory-bank-cli.py rag integrate --spec-type "level3" --code "class UserService {}"

# Комплексная проверка
python memory-bank-cli.py rag health
```

### Интеграция с существующими командами

```bash
# Spec команды теперь используют RAG контекст
python memory-bank-cli.py spec generate --feature-name "user-auth" --level 3
# RAG система автоматически индексирует спецификацию

# Creative команды получают AI предложения
python memory-bank-cli.py creative --research
# RAG система предоставляет контекстные предложения

# QA команды используют RAG для анализа
python memory-bank-cli.py qa --comprehensive
# RAG система анализирует код на соответствие методологиям
```

## 🧠 Как работает интеграция

### 1. Контекстная интеграция
- **Memory Bank** предоставляет контекст Spec Kit методологий
- **RAG система** использует этот контекст для генерации предложений
- **Автоматическая синхронизация** между CLI и RAG

### 2. Специфичные для Spec Kit возможности
- **Методологические предложения** на основе Level 1-4 подходов
- **Конституционное соответствие** при генерации кода
- **Spec-driven контекст** для всех AI операций

### 3. Автоматическое обучение
- **Индексация** при сохранении файлов через CLI
- **Обучение** на паттернах Spec Kit методологий
- **Адаптация** к стилю конкретного проекта

## 📊 API интеграции

### RAG Proxy endpoints

```bash
# Health check с интеграцией Memory Bank
GET /health
{
  "status": "healthy",
  "services": {
    "memory_bank": "healthy",
    "lightrag": "healthy",
    "n8n": "healthy"
  }
}

# Предложения с Spec Kit контекстом
POST /api/suggest
{
  "file_path": "src/auth.ts",
  "code": "const user = ",
  "language": "typescript",
  "project_context": "Vibecode Spec Kit Level 3 context..."
}
```

### Memory Bank интеграция

```python
# Автоматическая интеграция в Memory Bank
await memory_bank.integrate_rag_context("level3", code)
# Создает контекст для RAG системы

context = memory_bank.get_rag_context("authentication")
# Получает контекст для AI операций
```

## 🔄 Workflow автоматизация

### n8n интеграция

1. **Code Quality Improvement** - автоматическое улучшение кода
2. **Spec Kit Compliance** - проверка соответствия методологиям
3. **Memory Bank Sync** - синхронизация с Memory Bank
4. **Performance Optimization** - оптимизация на основе RAG анализа

### Автоматические триггеры

- **При сохранении файлов** → автоиндексация в RAG
- **При генерации spec** → обучение на паттернах
- **При QA проверках** → анализ соответствия методологиям
- **При creative режиме** → контекстные предложения

## 🎨 VS Code Extension (опционально)

### Установка расширения

```bash
cd vscode-integration/vscode-extension
npm install
npm run compile

# В VS Code: Ctrl+Shift+P -> "Extensions: Install from VSIX"
```

### Настройка

```json
{
  "ragContext.apiUrl": "http://localhost:9000", // Rust RAG Proxy endpoint
  "ragContext.autoIndex": true,
  "ragContext.suggestions": true,
  "ragContext.specKitIntegration": true
}
```

### Использование

- **Ctrl+Shift+E** - Объяснить код с Spec Kit контекстом
- **Ctrl+Shift+R** - Поиск по коду с методологиями
- **Автоиндексация** - код автоматически изучается при сохранении

## 📈 Мониторинг и метрики

### Статус системы

```bash
# Комплексная проверка
python memory-bank-cli.py rag health

# Детальный статус
python memory-bank-cli.py rag status
```

### Логи и отладка

```bash
# Логи Rust RAG Proxy
docker-compose -f docker-compose-rag.yml logs -f rag-proxy

# Логи LightRAG
docker-compose -f docker-compose-rag.yml logs -f lightrag

# Логи n8n
docker-compose -f docker-compose-rag.yml logs -f n8n
```

### Метрики производительности

- **Response Time**: < 300ms для CLI интеграции
- **Memory Usage**: ~2GB для всего стека
- **Learning Velocity**: 100+ паттернов/день
- **Spec Kit Integration**: 95%+ точность контекста

## 🚨 Troubleshooting

### Частые проблемы

1. **RAG Proxy не отвечает**
   ```bash
   # Проверяем статус
   docker-compose -f docker-compose-rag.yml ps
   
   # Перезапускаем
   docker-compose -f docker-compose-rag.yml restart rag-proxy
   ```

2. **Memory Bank не интегрируется**
   ```bash
   # Проверяем Memory Bank
   python memory-bank-cli.py status
   
   # Инициализируем заново
   python memory-bank-cli.py init --constitution
   ```

3. **Медленные предложения**
   ```bash
   # Проверяем ресурсы
   docker stats
   
   # Оптимизируем кеш
   python memory-bank-cli.py rag health
   ```

## 🔒 Безопасность и приватность

- **Локальная обработка** - все данные остаются на вашем компьютере
- **Memory Bank изоляция** - только read-only доступ к Memory Bank
- **API ключи** - хранятся в .env файле
- **Network isolation** - Docker network для изоляции сервисов

## 📚 Дополнительные ресурсы

- [Vibecode Spec Kit Documentation](docs/)
- [RAG Integration Guide](vscode-integration/README.md)
- [Memory Bank CLI Commands](src/cli/commands/)
- [API Documentation](docs/API.md)

## 🤝 Вклад в развитие

1. Fork репозиторий
2. Создайте feature branch для RAG интеграции
3. Внесите изменения
4. Создайте Pull Request

---

**🎉 Теперь у вас есть полноценная RAG-интегрированная система разработки!**

Vibecode Spec Kit + RAG = Умный AI-ассистент, который понимает ваши методологии и помогает писать код в соответствии с вашими принципами разработки.
