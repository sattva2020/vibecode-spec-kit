# Create n8n Workflow via API
# ===========================

Write-Host "🚀 Создание n8n workflow через API..." -ForegroundColor Green

# Проверяем доступность n8n
Write-Host "📋 Проверка n8n..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080" -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ n8n доступен" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ n8n недоступен: $_" -ForegroundColor Red
    exit 1
}

# Читаем workflow JSON
$workflowJson = Get-Content -Path "create-n8n-workflow.json" -Raw

# Создаем workflow через n8n API
Write-Host "🔧 Создание workflow..." -ForegroundColor Yellow
try {
    $headers = @{
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/workflows" -Method POST -Body $workflowJson -Headers $headers
    
    if ($response.id) {
        Write-Host "✅ Workflow создан с ID: $($response.id)" -ForegroundColor Green
        Write-Host "🌐 URL: http://localhost:8080/workflow/$($response.id)" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️ Workflow создан, но ID не получен" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Ошибка создания workflow: $_" -ForegroundColor Red
}

Write-Host "`n🎯 Следующие шаги:" -ForegroundColor Green
Write-Host "1. Откройте n8n: http://localhost:8080" -ForegroundColor White
Write-Host "2. Найдите workflow 'Code Generation with Ollama'" -ForegroundColor White
Write-Host "3. Активируйте workflow" -ForegroundColor White
Write-Host "4. Протестируйте через webhook" -ForegroundColor White

Write-Host "`n📋 Тест workflow:" -ForegroundColor Cyan
Write-Host "curl -X POST http://localhost:8080/webhook/generate-code" -ForegroundColor Gray
Write-Host "  -H 'Content-Type: application/json'" -ForegroundColor Gray
Write-Host "  -d '{\"prompt\": \"Write a Python function to calculate fibonacci\"}'" -ForegroundColor Gray

Write-Host "`n✅ Готово!" -ForegroundColor Green
