#!/bin/bash

# 🏥 Health Check Script for RAG-Powered Code Assistant
# 
# Проверяет состояние всех компонентов системы:
# - AI Router Service
# - Supabase Stack (DB, Auth, Kong)
# - Ollama Service
# - LightRAG Service
# - n8n Workflows
# - VS Code Extension

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Конфигурация
BASE_URL="http://localhost:8000"
SUPABASE_URL="http://localhost:54321"
N8N_URL="http://localhost:5678"
OLLAMA_URL="http://localhost:11434"
LIGHTRAG_URL="http://localhost:8001"

# Счетчики
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Функции для логирования
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED_CHECKS++))
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNING_CHECKS++))
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED_CHECKS++))
}

log_header() {
    echo -e "${PURPLE}🔍 $1${NC}"
}

log_section() {
    echo -e "${CYAN}📋 $1${NC}"
}

# Функция проверки HTTP endpoint
check_http_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    local timeout=${4:-10}
    local auth_header=${5:-""}
    
    ((TOTAL_CHECKS++))
    
    local curl_cmd="curl -s -o /dev/null -w '%{http_code}' --max-time $timeout"
    
    if [ -n "$auth_header" ]; then
        curl_cmd="$curl_cmd -H '$auth_header'"
    fi
    
    curl_cmd="$curl_cmd '$url'"
    
    local response_code
    if response_code=$(eval "$curl_cmd" 2>/dev/null); then
        if [ "$response_code" = "$expected_status" ]; then
            log_success "$name: HTTP $response_code"
            return 0
        else
            log_error "$name: HTTP $response_code (ожидался $expected_status)"
            return 1
        fi
    else
        log_error "$name: недоступен (timeout или ошибка соединения)"
        return 1
    fi
}

# Функция проверки Docker контейнера
check_docker_container() {
    local container_name=$1
    local service_name=${2:-$container_name}
    
    ((TOTAL_CHECKS++))
    
    if docker ps --format "table {{.Names}}" | grep -q "^$container_name$"; then
        local status=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null)
        local health=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "no-health-check")
        
        if [ "$status" = "running" ]; then
            if [ "$health" = "healthy" ] || [ "$health" = "no-health-check" ]; then
                log_success "$service_name: контейнер запущен и работает"
                return 0
            else
                log_warning "$service_name: контейнер запущен, но health check: $health"
                return 1
            fi
        else
            log_error "$service_name: контейнер в статусе '$status'"
            return 1
        fi
    else
        log_error "$service_name: контейнер не найден"
        return 1
    fi
}

# Функция проверки порта
check_port() {
    local port=$1
    local service_name=$2
    
    ((TOTAL_CHECKS++))
    
    if netstat -an 2>/dev/null | grep -q ":$port " || ss -an 2>/dev/null | grep -q ":$port "; then
        log_success "$service_name: порт $port открыт"
        return 0
    else
        log_error "$service_name: порт $port не открыт"
        return 1
    fi
}

# Функция проверки использования ресурсов
check_resource_usage() {
    local container_name=$1
    local service_name=${2:-$container_name}
    
    ((TOTAL_CHECKS++))
    
    local stats
    if stats=$(docker stats --no-stream --format "{{.CPUPerc}},{{.MemUsage}}" "$container_name" 2>/dev/null); then
        local cpu_usage=$(echo "$stats" | cut -d',' -f1 | sed 's/%//')
        local mem_usage=$(echo "$stats" | cut -d',' -f2 | sed 's/MiB.*//')
        
        # Проверяем CPU (предупреждение при >80%, ошибка при >95%)
        if (( $(echo "$cpu_usage > 95" | bc -l) )); then
            log_error "$service_name: критическое использование CPU ($cpu_usage%)"
            return 1
        elif (( $(echo "$cpu_usage > 80" | bc -l) )); then
            log_warning "$service_name: высокое использование CPU ($cpu_usage%)"
        else
            log_success "$service_name: CPU $cpu_usage%"
        fi
        
        # Проверяем память (предупреждение при >85%, ошибка при >95%)
        if (( $(echo "$mem_usage > 95" | bc -l) )); then
            log_error "$service_name: критическое использование памяти (${mem_usage}MB)"
            return 1
        elif (( $(echo "$mem_usage > 85" | bc -l) )); then
            log_warning "$service_name: высокое использование памяти (${mem_usage}MB)"
        else
            log_success "$service_name: память ${mem_usage}MB"
        fi
        
        return 0
    else
        log_error "$service_name: не удалось получить статистику ресурсов"
        return 1
    fi
}

# Функция проверки логи на ошибки
check_logs_for_errors() {
    local container_name=$1
    local service_name=${2:-$container_name}
    local lines=${3:-50}
    
    ((TOTAL_CHECKS++))
    
    local error_count
    if error_count=$(docker logs --tail "$lines" "$container_name" 2>&1 | grep -i "error\|exception\|fatal\|panic" | wc -l); then
        if [ "$error_count" -eq 0 ]; then
            log_success "$service_name: ошибок в логах не найдено"
            return 0
        elif [ "$error_count" -lt 5 ]; then
            log_warning "$service_name: найдено $error_count ошибок в последних $lines строках логов"
            return 1
        else
            log_error "$service_name: найдено $error_count ошибок в последних $lines строках логов"
            return 1
        fi
    else
        log_warning "$service_name: не удалось проверить логи"
        return 1
    fi
}

# Основная функция проверки
main() {
    echo "🏥 Проверка состояния системы RAG-Powered Code Assistant"
    echo "======================================================="
    echo ""
    
    # Проверка Docker контейнеров
    log_section "Docker контейнеры"
    
    check_docker_container "rag-ai-router" "AI Router"
    check_docker_container "rag-supabase-db" "Supabase Database"
    check_docker_container "rag-supabase-kong" "Kong API Gateway"
    check_docker_container "rag-supabase-auth" "Supabase Auth"
    check_docker_container "rag-supabase-storage" "Supabase Storage"
    check_docker_container "rag-supabase-realtime" "Supabase Realtime"
    check_docker_container "rag-ollama" "Ollama Service"
    check_docker_container "rag-lightrag" "LightRAG Service"
    check_docker_container "rag-n8n" "n8n Workflows"
    check_docker_container "rag-prometheus" "Prometheus"
    check_docker_container "rag-grafana" "Grafana"
    
    echo ""
    
    # Проверка портов
    log_section "Сетевые порты"
    
    check_port 8000 "AI Router"
    check_port 5432 "Supabase DB"
    check_port 54321 "Supabase API"
    check_port 11434 "Ollama"
    check_port 8001 "LightRAG"
    check_port 5678 "n8n"
    check_port 9090 "Prometheus"
    check_port 3000 "Grafana"
    
    echo ""
    
    # Проверка HTTP endpoints
    log_section "HTTP Endpoints"
    
    check_http_endpoint "AI Router Health" "$BASE_URL/health"
    check_http_endpoint "AI Router Metrics" "$BASE_URL/metrics"
    check_http_endpoint "Supabase Health" "$SUPABASE_URL/rest/v1/" 401
    check_http_endpoint "Supabase Auth" "$SUPABASE_URL/auth/v1/health"
    check_http_endpoint "Ollama API" "$OLLAMA_URL/api/tags"
    check_http_endpoint "LightRAG Health" "$LIGHTRAG_URL/health"
    check_http_endpoint "n8n Health" "$N8N_URL/healthz"
    check_http_endpoint "Prometheus" "http://localhost:9090/-/healthy"
    check_http_endpoint "Grafana" "http://localhost:3000/api/health"
    
    echo ""
    
    # Проверка использования ресурсов
    log_section "Использование ресурсов"
    
    check_resource_usage "rag-ai-router" "AI Router"
    check_resource_usage "rag-supabase-db" "Supabase DB"
    check_resource_usage "rag-ollama" "Ollama"
    check_resource_usage "rag-lightrag" "LightRAG"
    check_resource_usage "rag-n8n" "n8n"
    
    echo ""
    
    # Проверка логов на ошибки
    log_section "Анализ логов"
    
    check_logs_for_errors "rag-ai-router" "AI Router" 100
    check_logs_for_errors "rag-supabase-db" "Supabase DB" 100
    check_logs_for_errors "rag-ollama" "Ollama" 100
    check_logs_for_errors "rag-lightrag" "LightRAG" 100
    check_logs_for_errors "rag-n8n" "n8n" 100
    
    echo ""
    
    # Дополнительные проверки
    log_section "Дополнительные проверки"
    
    # Проверка доступности AI моделей
    ((TOTAL_CHECKS++))
    if curl -s "$OLLAMA_URL/api/tags" | jq -e '.models[] | select(.name | contains("qwen2.5-coder"))' > /dev/null; then
        log_success "Ollama: модель qwen2.5-coder доступна"
        ((PASSED_CHECKS++))
    else
        log_warning "Ollama: модель qwen2.5-coder не найдена"
        ((WARNING_CHECKS++))
    fi
    
    # Проверка подключения к базе данных
    ((TOTAL_CHECKS++))
    if docker exec rag-supabase-db psql -U postgres -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
        log_success "Supabase DB: подключение успешно"
        ((PASSED_CHECKS++))
    else
        log_error "Supabase DB: не удается подключиться"
        ((FAILED_CHECKS++))
    fi
    
    # Проверка расширения pgvector
    ((TOTAL_CHECKS++))
    if docker exec rag-supabase-db psql -U postgres -d postgres -c "SELECT extname FROM pg_extension WHERE extname = 'vector';" | grep -q vector; then
        log_success "Supabase DB: расширение pgvector установлено"
        ((PASSED_CHECKS++))
    else
        log_error "Supabase DB: расширение pgvector не найдено"
        ((FAILED_CHECKS++))
    fi
    
    echo ""
    
    # Итоговый отчет
    log_header "Итоговый отчет"
    echo "==================="
    echo "Всего проверок: $TOTAL_CHECKS"
    echo -e "${GREEN}Успешно: $PASSED_CHECKS${NC}"
    echo -e "${YELLOW}Предупреждения: $WARNING_CHECKS${NC}"
    echo -e "${RED}Ошибки: $FAILED_CHECKS${NC}"
    echo ""
    
    # Определение общего статуса
    if [ $FAILED_CHECKS -eq 0 ]; then
        if [ $WARNING_CHECKS -eq 0 ]; then
            log_success "🎉 Система работает отлично!"
            exit 0
        else
            log_warning "⚠️  Система работает с предупреждениями"
            exit 0
        fi
    else
        log_error "❌ Обнаружены критические проблемы!"
        exit 1
    fi
}

# Обработка аргументов командной строки
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE=true
            shift
            ;;
        --quick)
            # Быстрая проверка только основных компонентов
            QUICK_CHECK=true
            shift
            ;;
        --help)
            echo "Использование: $0 [--verbose] [--quick] [--help]"
            echo "  --verbose  Подробный вывод"
            echo "  --quick    Быстрая проверка"
            echo "  --help     Показать эту справку"
            exit 0
            ;;
        *)
            echo "Неизвестный аргумент: $1"
            exit 1
            ;;
    esac
done

# Запуск основной функции
main "$@"
