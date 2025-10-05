# Запуск автоматизации создания n8n workflow
# ==========================================

Write-Host "🚀 Запуск автоматизации создания n8n workflow..." -ForegroundColor Green

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

# Проверяем наличие Node.js
Write-Host "📋 Проверка Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js $nodeVersion найден" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js не найден. Установите Node.js для запуска автоматизации." -ForegroundColor Red
    Write-Host "Альтернатива: Откройте http://localhost:8080 вручную" -ForegroundColor Yellow
    exit 1
}

# Проверяем наличие Playwright
Write-Host "📋 Проверка Playwright..." -ForegroundColor Yellow
try {
    $playwrightVersion = npm list playwright
    Write-Host "✅ Playwright найден" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Playwright не найден. Устанавливаем..." -ForegroundColor Yellow
    npm install playwright
}

# Запускаем автоматизацию
Write-Host "🎬 Запуск автоматизации..." -ForegroundColor Green
try {
    node scripts/create-workflow-automation.js
} catch {
    Write-Host "❌ Ошибка запуска автоматизации: $_" -ForegroundColor Red
    Write-Host "🌐 Откройте n8n вручную: http://localhost:8080" -ForegroundColor Yellow
}

Write-Host "`n✅ Готово!" -ForegroundColor Green
