# 🚀 RAG-Powered VS Code Integration

Полная интеграция VS Code с n8n + Supabase + LightRAG через Docker для создания умного AI-ассистента разработчика.

## 🎯 Что это дает

- **🧠 Самообучающийся AI** - изучает ваш код и предлагает релевантные решения
- **🔄 Автоматизация** - n8n workflow для автоматизации задач
- **🗄️ Векторный поиск** - быстрый поиск по кодовой базе через pgvector
- **🔒 Приватность** - все работает локально, данные не покидают ваш компьютер
- **⚡ Производительность** - оптимизированный стек для быстрой работы

## 🏗️ Архитектура

```
VS Code Extension
       ↓
RAG Proxy (Rust)
       ↓
┌─────────────────┬─────────────────┬─────────────────┐
│   LightRAG      │      n8n        │   Supabase      │
│   (Python)      │   (Workflows)   │  (PostgreSQL)   │
│                 │                 │   + pgvector    │
└─────────────────┴─────────────────┴─────────────────┘
```

## 🚀 Быстрый старт

### 1. Подготовка

```bash
# Клонируем проект
git clone <your-repo>
cd vscode-integration

# Копируем конфигурацию
cp env.example .env

# Редактируем .env файл
nano .env  # Добавляем ваш OPENAI_API_KEY
```

### 2. Запуск стека

```bash
# Запускаем все сервисы
chmod +x start.sh
./start.sh

# Или вручную
docker-compose up -d
```

### 3. Установка VS Code Extension

```bash
cd vscode-extension
npm install
npm run compile

# В VS Code: Ctrl+Shift+P -> "Extensions: Install from VSIX"
# Выбираем файл из папки vscode-extension
```

### 4. Настройка VS Code

Добавьте в настройки VS Code (`.vscode/settings.json`):

```json
{
  "ragContext.apiUrl": "http://localhost:9000",
  "ragContext.autoIndex": true,
  "ragContext.suggestions": true
}
```

## 🔧 Использование

### Основные команды

- **Ctrl+Shift+E** - Объяснить выделенный код
- **Ctrl+Shift+R** - Поиск по контексту
- **Правый клик** - "Explain Code with RAG" / "Learn from Current Code"

### Автоматические функции

- **Автоиндексация** - код автоматически добавляется в базу знаний при сохранении
- **Inline предложения** - AI предлагает код на основе контекста
- **Контекстный поиск** - поиск релевантных фрагментов кода

## 📊 API Endpoints

### RAG Proxy (http://localhost:9000)

```bash
# Health check
GET /health

# Получить предложения кода
POST /api/suggest
{
  "file_path": "src/app.ts",
  "code": "const user = ",
  "language": "typescript",
  "cursor_position": {"line": 10, "character": 15}
}

# Поиск по контексту
POST /api/context/search
{
  "query": "authentication with supabase"
}

# Обучение на коде
POST /api/learn
{
  "file_path": "src/auth.ts",
  "code": "export async function login() { ... }",
  "language": "typescript"
}

# Запуск n8n workflow
POST /api/workflow/trigger/{workflow_id}
{
  "data": {...}
}
```

### LightRAG (http://localhost:8000)

```bash
# Health check
GET /health

# Добавить документ
POST /insert
{
  "text": "Your code or documentation",
  "source": "file_path"
}

# Поиск в RAG
POST /query
{
  "query": "How to implement authentication?",
  "mode": "hybrid",
  "top_k": 5
}

# Добавить код с контекстом
POST /insert_code
{
  "file_path": "src/auth.ts",
  "code": "export function login() {...}",
  "language": "typescript"
}
```

## 🔄 n8n Workflows

### Доступные workflow

1. **Code Quality Improvement** - автоматическое улучшение качества кода
2. **Performance Optimization** - оптимизация производительности
3. **Team Learning Sync** - синхронизация знаний в команде

### Создание нового workflow

1. Откройте http://localhost:5678
2. Войдите (admin/admin123)
3. Создайте новый workflow
4. Добавьте HTTP Request node для вызова RAG Proxy

## 🛠️ Разработка

### Структура проекта

```
vscode-integration/
├── docker-compose.yml          # Docker стек
├── start.sh                   # Скрипт запуска
├── env.example               # Пример конфигурации
├── rag-proxy/                # Rust RAG Proxy
│   ├── Cargo.toml
│   ├── Dockerfile
│   └── src/main.rs
├── lightrag/                 # Python LightRAG сервис
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── vscode-extension/         # VS Code расширение
│   ├── package.json
│   └── src/extension.ts
├── n8n/
│   └── workflows/           # n8n workflow файлы
└── supabase/
    └── init.sql            # Инициализация БД
```

### Локальная разработка

```bash
# Запуск только инфраструктуры
docker-compose up -d postgres redis

# Разработка RAG Proxy
cd rag-proxy
cargo run

# Разработка LightRAG
cd lightrag
pip install -r requirements.txt
python app.py

# Разработка VS Code Extension
cd vscode-extension
npm install
npm run watch
```

## 🔍 Мониторинг

### Проверка статуса

```bash
# Статус контейнеров
docker-compose ps

# Логи сервисов
docker-compose logs -f rag-proxy
docker-compose logs -f lightrag
docker-compose logs -f n8n

# Health checks
curl http://localhost:9000/health
curl http://localhost:8000/health
curl http://localhost:5678/healthz
```

### Метрики производительности

- **Response Time**: < 300ms для большинства запросов
- **Memory Usage**: ~2GB для всего стека
- **CPU Usage**: 10-30% в зависимости от активности

## 🚨 Troubleshooting

### Частые проблемы

1. **Сервисы не запускаются**
   ```bash
   # Проверьте логи
   docker-compose logs
   
   # Перезапустите
   docker-compose down && docker-compose up -d
   ```

2. **VS Code extension не работает**
   ```bash
   # Проверьте настройки
   cat .vscode/settings.json
   
   # Перезапустите VS Code
   ```

3. **Медленные запросы**
   ```bash
   # Проверьте ресурсы
   docker stats
   
   # Увеличьте лимиты в docker-compose.yml
   ```

## 📈 Производительность

### Оптимизация

- **Кеширование**: LRU кеш в RAG Proxy (1000 записей)
- **Batch обработка**: Группировка запросов в LightRAG
- **Индексы**: Оптимизированные индексы в PostgreSQL
- **Connection pooling**: Переиспользование соединений

### Масштабирование

- **Horizontal scaling**: Добавление реплик сервисов
- **Load balancing**: Nginx для распределения нагрузки
- **Database sharding**: Разделение данных по проектам

## 🔒 Безопасность

- **Локальная обработка**: Все данные остаются на вашем компьютере
- **API ключи**: Хранятся в .env файле (не в коде)
- **Network isolation**: Docker network для изоляции сервисов
- **Authentication**: Базовая аутентификация для n8n

## 📚 Дополнительные ресурсы

- [LightRAG Documentation](https://github.com/HKUDS/LightRAG)
- [n8n Documentation](https://docs.n8n.io/)
- [Supabase Documentation](https://supabase.com/docs)
- [VS Code Extension API](https://code.visualstudio.com/api)

## 🤝 Вклад в проект

1. Fork репозиторий
2. Создайте feature branch
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - см. файл LICENSE для деталей.

---

**🎉 Готово! Теперь у вас есть умный AI-ассистент для VS Code!**
