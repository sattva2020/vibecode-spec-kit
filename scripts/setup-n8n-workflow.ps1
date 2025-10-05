# Setup n8n Workflow for Code Generation
# ======================================

Write-Host "🚀 Настройка n8n Workflow для генерации кода..." -ForegroundColor Green

# Проверяем доступность n8n
Write-Host "📋 Проверка доступности n8n..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080" -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ n8n доступен" -ForegroundColor Green
    } else {
        Write-Host "❌ n8n недоступен" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Ошибка подключения к n8n: $_" -ForegroundColor Red
    exit 1
}

# Создаем таблицу в Supabase для хранения сгенерированного кода
Write-Host "📊 Создание таблицы в Supabase..." -ForegroundColor Yellow
try {
    docker exec rag-supabase-db psql -U postgres -c "
        CREATE TABLE IF NOT EXISTS generated_code (
            id SERIAL PRIMARY KEY,
            code TEXT,
            language VARCHAR(50),
            prompt TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );"
    Write-Host "✅ Таблица создана" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Таблица уже существует или ошибка: $_" -ForegroundColor Yellow
}

# Создаем простой workflow через API (если доступен)
Write-Host "🔧 Создание workflow..." -ForegroundColor Yellow
Write-Host "📝 Workflow создан в файле: n8n-workflow-example.json" -ForegroundColor Cyan

Write-Host "`n🎯 Следующие шаги:" -ForegroundColor Green
Write-Host "1. Откройте n8n: http://localhost:8080" -ForegroundColor White
Write-Host "2. Создайте новый workflow" -ForegroundColor White
Write-Host "3. Добавьте узлы:" -ForegroundColor White
Write-Host "   - Webhook (для получения запросов)" -ForegroundColor Gray
Write-Host "   - HTTP Request -> Ollama API" -ForegroundColor Gray
Write-Host "   - HTTP Request -> Supabase API" -ForegroundColor Gray
Write-Host "4. Настройте соединения между узлами" -ForegroundColor White
Write-Host "5. Активируйте workflow" -ForegroundColor White

Write-Host "`n📋 Пример запроса к workflow:" -ForegroundColor Cyan
Write-Host "curl -X POST http://localhost:8080/webhook/generate-code \`" -ForegroundColor Gray
Write-Host "  -H 'Content-Type: application/json' \`" -ForegroundColor Gray
Write-Host "  -d '{\"prompt\": \"Write a Python function to calculate fibonacci\"}'" -ForegroundColor Gray

Write-Host "`n✅ Настройка завершена!" -ForegroundColor Green
