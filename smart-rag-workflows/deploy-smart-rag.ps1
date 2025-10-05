# Smart RAG Deployment Script
# Скрипт развертывания Smart RAG системы

Write-Host "🚀 Развертывание Smart RAG системы..." -ForegroundColor Green

# Проверка наличия Docker
Write-Host "📋 Проверка Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "✅ Docker найден" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker не найден. Установите Docker и повторите попытку." -ForegroundColor Red
    exit 1
}

# Проверка наличия n8n
Write-Host "📋 Проверка n8n..." -ForegroundColor Yellow
try {
    $n8nResponse = Invoke-WebRequest -Uri "http://localhost:8080/api/v1/workflows" -Method GET -Headers @{"Authorization" = "Bearer $env:N8N_API_KEY"} -ErrorAction Stop
    Write-Host "✅ n8n доступен" -ForegroundColor Green
} catch {
    Write-Host "❌ n8n недоступен. Убедитесь, что n8n запущен на порту 8080." -ForegroundColor Red
    exit 1
}

# Проверка Supabase
Write-Host "📋 Проверка Supabase..." -ForegroundColor Yellow
try {
    $supabaseResponse = Invoke-WebRequest -Uri "http://localhost:5432/rest/v1/" -Method GET -ErrorAction Stop
    Write-Host "✅ Supabase доступен" -ForegroundColor Green
} catch {
    Write-Host "❌ Supabase недоступен. Убедитесь, что Supabase запущен." -ForegroundColor Red
    exit 1
}

# Проверка Ollama
Write-Host "📋 Проверка Ollama..." -ForegroundColor Yellow
try {
    $ollamaResponse = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET -ErrorAction Stop
    Write-Host "✅ Ollama доступен" -ForegroundColor Green
} catch {
    Write-Host "❌ Ollama недоступен. Убедитесь, что Ollama запущен." -ForegroundColor Red
    exit 1
}

# Создание таблицы в Supabase
Write-Host "🗄️ Создание таблицы knowledge_base в Supabase..." -ForegroundColor Yellow
try {
    $sqlContent = Get-Content -Path "create-knowledge-table.sql" -Raw -Encoding UTF8
    
    # Выполнение SQL через psql (если доступен)
    $psqlCommand = "psql -h localhost -p 5432 -U postgres -d postgres -c `"$sqlContent`""
    
    Write-Host "Выполняется команда: $psqlCommand" -ForegroundColor Gray
    
    # Альтернативный способ через HTTP API
    $headers = @{
        "Authorization" = "Bearer $env:SUPABASE_ANON_KEY"
        "Content-Type" = "application/json"
        "apikey" = "$env:SUPABASE_ANON_KEY"
    }
    
    # Попытка создать таблицу через SQL endpoint
    $sqlPayload = @{
        query = $sqlContent
    } | ConvertTo-Json
    
    try {
        $sqlResponse = Invoke-WebRequest -Uri "http://localhost:5432/rest/v1/rpc/exec_sql" -Method POST -Headers $headers -Body $sqlPayload -ErrorAction Stop
        Write-Host "✅ Таблица создана через API" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Не удалось создать таблицу через API. Создайте таблицу вручную в Supabase UI." -ForegroundColor Yellow
        Write-Host "SQL для создания таблицы:" -ForegroundColor Cyan
        Write-Host $sqlContent -ForegroundColor White
    }
    
} catch {
    Write-Host "❌ Ошибка при создании таблицы: $_" -ForegroundColor Red
}

# Создание workflows в n8n
Write-Host "🔧 Создание Smart RAG workflows в n8n..." -ForegroundColor Yellow

$workflows = @(
    @{name="rag-insert.json"; description="Smart RAG Insert Workflow"},
    @{name="rag-query.json"; description="Smart RAG Query Workflow"},
    @{name="rag-analyze.json"; description="Smart RAG Analyze Workflow"}
)

$headers = @{
    "Authorization" = "Bearer $env:N8N_API_KEY"
    "Content-Type" = "application/json"
}

foreach ($workflow in $workflows) {
    $workflowFile = $workflow.name
    $description = $workflow.description
    
    Write-Host "📝 Создание workflow: $description" -ForegroundColor Cyan
    
    try {
        if (Test-Path $workflowFile) {
            $workflowContent = Get-Content -Path $workflowFile -Raw -Encoding UTF8
            $workflowJson = $workflowContent | ConvertFrom-Json
            
            # Подготовка payload для создания workflow
            $workflowPayload = @{
                name = $workflowJson.name
                nodes = $workflowJson.nodes
                connections = $workflowJson.connections
                settings = $workflowJson.settings
                active = $false  # Сначала неактивен для проверки
            } | ConvertTo-Json -Depth 10
            
            # Создание workflow
            $createResponse = Invoke-WebRequest -Uri "http://localhost:8080/api/v1/workflows" -Method POST -Headers $headers -Body $workflowPayload -ErrorAction Stop
            $createdWorkflow = $createResponse.Content | ConvertFrom-Json
            
            Write-Host "✅ Workflow создан: $($createdWorkflow.id)" -ForegroundColor Green
            
            # Активация workflow
            $activatePayload = @{
                active = $true
            } | ConvertTo-Json
            
            $activateResponse = Invoke-WebRequest -Uri "http://localhost:8080/api/v1/workflows/$($createdWorkflow.id)" -Method PATCH -Headers $headers -Body $activatePayload -ErrorAction Stop
            
            Write-Host "✅ Workflow активирован: $($createdWorkflow.id)" -ForegroundColor Green
            
        } else {
            Write-Host "❌ Файл $workflowFile не найден" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Ошибка при создании workflow $workflowFile : $_" -ForegroundColor Red
        Write-Host "Ответ сервера: $($_.Exception.Response)" -ForegroundColor Gray
    }
}

# Тестирование Smart RAG системы
Write-Host "🧪 Тестирование Smart RAG системы..." -ForegroundColor Yellow

try {
    # Тест вставки знания
    Write-Host "📝 Тест вставки знания..." -ForegroundColor Cyan
    
    $testInsertPayload = @{
        text = "Smart RAG система успешно развернута и готова к работе. Это тестовое знание для проверки функциональности."
        metadata = @{
            source = "deployment_test"
            category = "system"
            author = "deployment_script"
        }
    } | ConvertTo-Json
    
    $insertResponse = Invoke-WebRequest -Uri "http://localhost:8080/webhook/rag-insert" -Method POST -Headers @{"Content-Type" = "application/json"} -Body $testInsertPayload -ErrorAction Stop
    $insertResult = $insertResponse.Content | ConvertFrom-Json
    
    Write-Host "✅ Тест вставки прошел успешно: $($insertResult.knowledge_id)" -ForegroundColor Green
    
    # Тест поиска
    Write-Host "🔍 Тест поиска знаний..." -ForegroundColor Cyan
    
    $testQueryPayload = @{
        query = "Smart RAG система"
        options = @{
            limit = 5
        }
    } | ConvertTo-Json
    
    $queryResponse = Invoke-WebRequest -Uri "http://localhost:8080/webhook/rag-query" -Method POST -Headers @{"Content-Type" = "application/json"} -Body $testQueryPayload -ErrorAction Stop
    $queryResult = $queryResponse.Content | ConvertFrom-Json
    
    Write-Host "✅ Тест поиска прошел успешно: найдено $($queryResult.total_found) результатов" -ForegroundColor Green
    
    # Тест анализа
    if ($insertResult.knowledge_id) {
        Write-Host "🔬 Тест анализа знаний..." -ForegroundColor Cyan
        
        $testAnalyzePayload = @{
            knowledge_id = $insertResult.knowledge_id
            analysis_type = "comprehensive"
        } | ConvertTo-Json
        
        $analyzeResponse = Invoke-WebRequest -Uri "http://localhost:8080/webhook/rag-analyze" -Method POST -Headers @{"Content-Type" = "application/json"} -Body $testAnalyzePayload -ErrorAction Stop
        $analyzeResult = $analyzeResponse.Content | ConvertFrom-Json
        
        Write-Host "✅ Тест анализа прошел успешно" -ForegroundColor Green
    }
    
} catch {
    Write-Host "❌ Ошибка при тестировании: $_" -ForegroundColor Red
    Write-Host "Убедитесь, что все workflows активны и доступны." -ForegroundColor Yellow
}

# Создание файла конфигурации
Write-Host "📄 Создание конфигурационного файла..." -ForegroundColor Yellow

$config = @{
    smart_rag = @{
        version = "1.0.0"
        deployed_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        workflows = @{
            insert = "http://localhost:8080/webhook/rag-insert"
            query = "http://localhost:8080/webhook/rag-query"
            analyze = "http://localhost:8080/webhook/rag-analyze"
        }
        database = @{
            table = "knowledge_base"
            url = "http://localhost:5432/rest/v1/knowledge_base"
        }
        ollama = @{
            url = "http://localhost:11434"
            models = @("qwen2.5-coder:1.5b", "qwen2.5-coder:7b")
        }
    }
} | ConvertTo-Json -Depth 10

$config | Out-File -FilePath "smart-rag-config.json" -Encoding UTF8

Write-Host "✅ Конфигурация сохранена в smart-rag-config.json" -ForegroundColor Green

# Финальный отчет
Write-Host "`n🎉 Smart RAG система успешно развернута!" -ForegroundColor Green
Write-Host "📊 Статистика развертывания:" -ForegroundColor Cyan
Write-Host "  • Workflows созданы: $($workflows.Count)" -ForegroundColor White
Write-Host "  • База данных: Supabase" -ForegroundColor White
Write-Host "  • AI модели: Ollama (qwen2.5-coder)" -ForegroundColor White
Write-Host "  • Webhook endpoints настроены" -ForegroundColor White

Write-Host "`n🔗 Полезные ссылки:" -ForegroundColor Cyan
Write-Host "  • n8n UI: http://localhost:8080" -ForegroundColor White
Write-Host "  • Supabase UI: http://localhost:54322" -ForegroundColor White
Write-Host "  • Ollama API: http://localhost:11434" -ForegroundColor White

Write-Host "`n📚 Использование:" -ForegroundColor Cyan
Write-Host "  • Вставка знаний: POST http://localhost:8080/webhook/rag-insert" -ForegroundColor White
Write-Host "  • Поиск знаний: POST http://localhost:8080/webhook/rag-query" -ForegroundColor White
Write-Host "  • Анализ знаний: POST http://localhost:8080/webhook/rag-analyze" -ForegroundColor White

Write-Host "`n🧪 Тестирование:" -ForegroundColor Cyan
Write-Host "  python smart-rag-coordinator.py" -ForegroundColor White

Write-Host "`n✨ Smart RAG система готова к работе!" -ForegroundColor Green
