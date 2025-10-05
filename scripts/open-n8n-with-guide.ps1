# Открытие n8n с готовыми инструкциями
# ====================================

Write-Host "🚀 Открытие n8n с инструкциями..." -ForegroundColor Green

# Проверяем доступность n8n
Write-Host "📋 Проверка n8n..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080" -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ n8n доступен" -ForegroundColor Green
    } else {
        Write-Host "❌ n8n недоступен" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ n8n недоступен: $_" -ForegroundColor Red
    exit 1
}

# Открываем n8n в браузере
Write-Host "🌐 Открываем n8n в браузере..." -ForegroundColor Green
Start-Process "http://localhost:8080"

# Показываем инструкции
Write-Host "`n📋 ИНСТРУКЦИИ ДЛЯ СОЗДАНИЯ WORKFLOW:" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

Write-Host "`n1️⃣ СОЗДАНИЕ WORKFLOW:" -ForegroundColor Yellow
Write-Host "   - Нажмите 'New workflow'" -ForegroundColor White
Write-Host "   - Назовите: 'Code Generation with Ollama'" -ForegroundColor White

Write-Host "`n2️⃣ УЗЕЛ 1 - WEBHOOK:" -ForegroundColor Yellow
Write-Host "   - Перетащите 'Webhook' на canvas" -ForegroundColor White
Write-Host "   - Path: generate-code" -ForegroundColor White
Write-Host "   - HTTP Method: POST" -ForegroundColor White
Write-Host "   - Response Mode: On Received" -ForegroundColor White

Write-Host "`n3️⃣ УЗЕЛ 2 - OLLAMA HTTP REQUEST:" -ForegroundColor Yellow
Write-Host "   - Перетащите 'HTTP Request' на canvas" -ForegroundColor White
Write-Host "   - URL: http://rag-ollama:11434/api/generate" -ForegroundColor White
Write-Host "   - Method: POST" -ForegroundColor White
Write-Host "   - Headers: Content-Type: application/json" -ForegroundColor White
Write-Host "   - Body (JSON):" -ForegroundColor White
Write-Host "     {" -ForegroundColor Gray
Write-Host "       'model': 'qwen2.5-coder:1.5b'," -ForegroundColor Gray
Write-Host "       'prompt': '={{ `$json.prompt }}'," -ForegroundColor Gray
Write-Host "       'stream': false" -ForegroundColor Gray
Write-Host "     }" -ForegroundColor Gray

Write-Host "`n4️⃣ УЗЕЛ 3 - SUPABASE HTTP REQUEST:" -ForegroundColor Yellow
Write-Host "   - Перетащите 'HTTP Request' на canvas" -ForegroundColor White
Write-Host "   - URL: http://rag-supabase-db:5432/rest/v1/generated_code" -ForegroundColor White
Write-Host "   - Method: POST" -ForegroundColor White
Write-Host "   - Headers:" -ForegroundColor White
Write-Host "     Content-Type: application/json" -ForegroundColor Gray
Write-Host "     Authorization: Bearer [ваш-ключ]" -ForegroundColor Gray
Write-Host "   - Body (JSON):" -ForegroundColor White
Write-Host "     {" -ForegroundColor Gray
Write-Host "       'code': '={{ `$json.response }}'," -ForegroundColor Gray
Write-Host "       'language': 'python'," -ForegroundColor Gray
Write-Host "       'prompt': '={{ `$('Webhook').item.json.prompt }}'" -ForegroundColor Gray
Write-Host "     }" -ForegroundColor Gray

Write-Host "`n5️⃣ УЗЕЛ 4 - RESPONSE:" -ForegroundColor Yellow
Write-Host "   - Перетащите 'Respond to Webhook' на canvas" -ForegroundColor White
Write-Host "   - Response Body (JSON):" -ForegroundColor White
Write-Host "     {" -ForegroundColor Gray
Write-Host "       'code': '={{ `$('HTTP Request').item.json.response }}'," -ForegroundColor Gray
Write-Host "       'status': 'success'," -ForegroundColor Gray
Write-Host "       'saved_to_db': 'yes'" -ForegroundColor Gray
Write-Host "     }" -ForegroundColor Gray

Write-Host "`n6️⃣ СОЕДИНЕНИЯ:" -ForegroundColor Yellow
Write-Host "   - Webhook → HTTP Request (Ollama)" -ForegroundColor White
Write-Host "   - HTTP Request (Ollama) → HTTP Request (Supabase)" -ForegroundColor White
Write-Host "   - HTTP Request (Supabase) → Respond to Webhook" -ForegroundColor White

Write-Host "`n7️⃣ АКТИВАЦИЯ:" -ForegroundColor Yellow
Write-Host "   - Нажмите 'Active' в правом верхнем углу" -ForegroundColor White
Write-Host "   - Workflow должен стать зеленым" -ForegroundColor White

Write-Host "`n8️⃣ ТЕСТИРОВАНИЕ:" -ForegroundColor Yellow
Write-Host "   curl -X POST http://localhost:8080/webhook/generate-code \" -ForegroundColor White
Write-Host "     -H 'Content-Type: application/json' \" -ForegroundColor Gray
Write-Host "     -d '{\"prompt\": \"Write a Python function to calculate fibonacci\"}'" -ForegroundColor Gray

Write-Host "`n🎯 ГОТОВО! n8n открыт в браузере с инструкциями!" -ForegroundColor Green
