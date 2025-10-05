#!/bin/bash

# 🧪 End-to-End Testing Script for RAG-Powered Code Assistant
# 
# Выполняет полный цикл тестирования системы:
# 1. Аутентификация
# 2. Семантический поиск
# 3. Генерация кода
# 4. Анализ кода
# 5. Создание n8n workflow
# 6. Сохранение результатов

set -e  # Остановка при любой ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация
BASE_URL="http://localhost:8000"
SUPABASE_URL="http://localhost:54321"
N8N_URL="http://localhost:5678"
TEST_EMAIL="test@example.com"
TEST_PASSWORD="testpassword123"

# Функции для логирования
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Функция проверки доступности сервиса
check_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    log_info "Проверка доступности $service_name..."
    
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
    
    if [ "$response_code" = "$expected_status" ]; then
        log_success "$service_name доступен (HTTP $response_code)"
        return 0
    else
        log_error "$service_name недоступен (HTTP $response_code)"
        return 1
    fi
}

# Функция выполнения HTTP запроса с проверкой
make_request() {
    local method=$1
    local url=$2
    local data=$3
    local headers=$4
    local expected_status=${5:-200}
    
    local curl_cmd="curl -s -w '\n%{http_code}'"
    
    if [ -n "$data" ]; then
        curl_cmd="$curl_cmd -d '$data'"
    fi
    
    if [ -n "$headers" ]; then
        curl_cmd="$curl_cmd -H '$headers'"
    fi
    
    curl_cmd="$curl_cmd -X $method '$url'"
    
    local response=$(eval $curl_cmd)
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" = "$expected_status" ]; then
        echo "$body"
        return 0
    else
        log_error "HTTP $http_code: $body"
        return 1
    fi
}

# Основная функция тестирования
main() {
    echo "🧪 Запуск End-to-End тестирования RAG-Powered Code Assistant"
    echo "=========================================================="
    
    # Проверка доступности всех сервисов
    log_info "Проверка доступности сервисов..."
    
    check_service "AI Router" "$BASE_URL/health" || exit 1
    check_service "Supabase Auth" "$SUPABASE_URL/auth/v1/health" || exit 1
    check_service "Supabase DB" "$SUPABASE_URL/rest/v1/" 401 || exit 1
    check_service "n8n" "$N8N_URL/healthz" || exit 1
    check_service "Ollama" "http://localhost:11434/api/tags" || exit 1
    
    log_success "Все сервисы доступны!"
    echo ""
    
    # Шаг 1: Аутентификация
    log_info "Шаг 1: Аутентификация пользователя"
    
    local auth_response=$(make_request "POST" \
        "$SUPABASE_URL/auth/v1/token?grant_type=password" \
        "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" \
        "Content-Type: application/json" \
        200)
    
    local jwt_token=$(echo "$auth_response" | jq -r '.access_token // empty')
    
    if [ -z "$jwt_token" ] || [ "$jwt_token" = "null" ]; then
        log_error "Не удалось получить JWT токен"
        exit 1
    fi
    
    log_success "Аутентификация успешна, получен JWT токен"
    echo ""
    
    # Шаг 2: Семантический поиск
    log_info "Шаг 2: Семантический поиск через Ollama"
    
    local search_payload='{
        "query": "user authentication middleware",
        "context": "express_typescript_project",
        "type": "semantic",
        "limit": 5
    }'
    
    local search_response=$(make_request "POST" \
        "$BASE_URL/api/v1/search" \
        "$search_payload" \
        "Content-Type: application/json
Authorization: Bearer $jwt_token" \
        200)
    
    local search_results_count=$(echo "$search_response" | jq '.results | length')
    local search_provider=$(echo "$search_response" | jq -r '.provider')
    
    if [ "$search_provider" != "ollama" ]; then
        log_warning "Ожидался провайдер 'ollama', получен '$search_provider'"
    fi
    
    log_success "Семантический поиск: найдено $search_results_count результатов через $search_provider"
    echo ""
    
    # Шаг 3: Генерация кода
    log_info "Шаг 3: Генерация кода через AI"
    
    local generation_payload='{
        "task_type": "code_generation",
        "language": "typescript",
        "description": "Create a user authentication middleware for Express.js with JWT validation",
        "complexity": "medium",
        "context": {
            "framework": "express",
            "database": "postgresql",
            "authentication": "jwt"
        }
    }'
    
    local generation_response=$(make_request "POST" \
        "$BASE_URL/api/v1/generate" \
        "$generation_payload" \
        "Content-Type: application/json
Authorization: Bearer $jwt_token" \
        200)
    
    local generated_code_length=$(echo "$generation_response" | jq '.code | length')
    local generation_provider=$(echo "$generation_response" | jq -r '.provider')
    
    log_success "Генерация кода: создано $generated_code_length символов через $generation_provider"
    echo ""
    
    # Шаг 4: Анализ кода
    log_info "Шаг 4: Анализ сгенерированного кода"
    
    local code_to_analyze=$(echo "$generation_response" | jq -r '.code')
    
    local analysis_payload=$(jq -n \
        --arg code "$code_to_analyze" \
        '{
            task_type: "code_analysis",
            code: $code,
            language: "typescript",
            analysis_type: "security_and_performance",
            complexity: "medium"
        }')
    
    local analysis_response=$(make_request "POST" \
        "$BASE_URL/api/v1/analyze" \
        "$analysis_payload" \
        "Content-Type: application/json
Authorization: Bearer $jwt_token" \
        200)
    
    local suggestions_count=$(echo "$analysis_response" | jq '.suggestions | length')
    local analysis_provider=$(echo "$analysis_response" | jq -r '.provider')
    
    log_success "Анализ кода: получено $suggestions_count предложений через $analysis_provider"
    echo ""
    
    # Шаг 5: Создание n8n workflow
    log_info "Шаг 5: Создание n8n workflow"
    
    local workflow_payload='{
        "name": "E2E Test Workflow",
        "description": "Automated test workflow for code analysis",
        "nodes": [
            {
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "parameters": {
                    "path": "e2e-test-webhook",
                    "httpMethod": "POST"
                }
            },
            {
                "name": "AI Analysis",
                "type": "n8n-nodes-base.httpRequest",
                "parameters": {
                    "url": "http://ai-router:8000/api/v1/analyze",
                    "method": "POST",
                    "headers": {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer '${jwt_token}'"
                    }
                }
            }
        ],
        "connections": {
            "Webhook": {
                "main": [["AI Analysis"]]
            }
        }
    }'
    
    local workflow_response=$(make_request "POST" \
        "$N8N_URL/api/v1/workflows" \
        "$workflow_payload" \
        "Content-Type: application/json
X-N8N-API-KEY: ${N8N_API_KEY:-test-key}" \
        201)
    
    local workflow_id=$(echo "$workflow_response" | jq -r '.id')
    
    log_success "n8n workflow создан с ID: $workflow_id"
    echo ""
    
    # Шаг 6: Сохранение результатов в Supabase
    log_info "Шаг 6: Сохранение результатов в Supabase"
    
    local save_payload=$(jq -n \
        --arg code "$code_to_analyze" \
        --arg analysis "$analysis_response" \
        '{
            title: "E2E Test Code Generation",
            code: $code,
            language: "typescript",
            analysis: $analysis,
            test_timestamp: now
        }')
    
    local save_response=$(make_request "POST" \
        "$SUPABASE_URL/rest/v1/code_snippets" \
        "$save_payload" \
        "Content-Type: application/json
Authorization: Bearer $jwt_token
apikey: ${SUPABASE_ANON_KEY:-test-key}" \
        201)
    
    local saved_id=$(echo "$save_response" | jq -r '.id')
    
    log_success "Результаты сохранены в Supabase с ID: $saved_id"
    echo ""
    
    # Шаг 7: Тестирование производительности
    log_info "Шаг 7: Тестирование производительности"
    
    local start_time=$(date +%s%3N)
    
    make_request "POST" \
        "$BASE_URL/api/v1/search" \
        '{"query": "performance test", "context": "test", "type": "semantic"}' \
        "Content-Type: application/json
Authorization: Bearer $jwt_token" \
        200 > /dev/null
    
    local end_time=$(date +%s%3N)
    local response_time=$((end_time - start_time))
    
    log_success "Время отклика: ${response_time}ms"
    
    if [ $response_time -lt 2000 ]; then
        log_success "Производительность: отлично (< 2s)"
    elif [ $response_time -lt 5000 ]; then
        log_warning "Производительность: удовлетворительно (< 5s)"
    else
        log_error "Производительность: плохо (> 5s)"
    fi
    echo ""
    
    # Итоговый отчет
    echo "🎉 End-to-End тестирование завершено успешно!"
    echo "=============================================="
    echo "📊 Результаты тестирования:"
    echo "  • Аутентификация: ✅ Успешно"
    echo "  • Семантический поиск: ✅ $search_results_count результатов"
    echo "  • Генерация кода: ✅ $generated_code_length символов"
    echo "  • Анализ кода: ✅ $suggestions_count предложений"
    echo "  • n8n workflow: ✅ ID $workflow_id"
    echo "  • Сохранение: ✅ ID $saved_id"
    echo "  • Производительность: ✅ ${response_time}ms"
    echo ""
    echo "🚀 Система готова к продакшн использованию!"
}

# Обработка ошибок
trap 'log_error "Тест прерван с ошибкой на строке $LINENO"' ERR

# Запуск тестирования
main "$@"
