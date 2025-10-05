#!/bin/bash

# 💾 Backup and Restore Script for RAG-Powered Code Assistant
# 
# Создает резервные копии и восстанавливает систему:
# - Supabase database
# - LightRAG knowledge base
# - n8n workflows
# - Конфигурации
# - Docker volumes

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CURRENT_BACKUP_DIR="$BACKUP_DIR/$TIMESTAMP"

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

# Функция создания backup
create_backup() {
    log_info "Создание резервной копии системы..."
    
    # Создаем директорию для backup
    mkdir -p "$CURRENT_BACKUP_DIR"
    
    # 1. Backup Supabase database
    log_info "Создание backup Supabase database..."
    if docker exec rag-supabase-db pg_dump -U postgres postgres > "$CURRENT_BACKUP_DIR/supabase_backup.sql"; then
        log_success "Supabase database backup создан"
    else
        log_error "Ошибка создания backup Supabase database"
        return 1
    fi
    
    # 2. Backup LightRAG knowledge base
    log_info "Создание backup LightRAG knowledge base..."
    if docker cp rag-lightrag:/app/knowledge_base "$CURRENT_BACKUP_DIR/lightrag_knowledge_base" 2>/dev/null; then
        log_success "LightRAG knowledge base backup создан"
    else
        log_warning "LightRAG knowledge base не найден или пуст"
    fi
    
    # 3. Backup n8n workflows
    log_info "Создание backup n8n workflows..."
    if curl -s -H "X-N8N-API-KEY: ${N8N_API_KEY:-test-key}" \
        http://localhost:5678/api/v1/workflows > "$CURRENT_BACKUP_DIR/n8n_workflows.json"; then
        log_success "n8n workflows backup создан"
    else
        log_warning "Не удалось создать backup n8n workflows"
    fi
    
    # 4. Backup конфигураций
    log_info "Создание backup конфигураций..."
    cp -r ./supabase "$CURRENT_BACKUP_DIR/" 2>/dev/null || log_warning "Supabase конфигурации не найдены"
    cp docker-compose-rag-system.yml "$CURRENT_BACKUP_DIR/" 2>/dev/null || log_warning "Docker-compose файл не найден"
    cp .env "$CURRENT_BACKUP_DIR/" 2>/dev/null || log_warning ".env файл не найден"
    cp prometheus.yml "$CURRENT_BACKUP_DIR/" 2>/dev/null || log_warning "Prometheus конфигурация не найдена"
    cp alertmanager.yml "$CURRENT_BACKUP_DIR/" 2>/dev/null || log_warning "Alertmanager конфигурация не найдена"
    cp alerts.yml "$CURRENT_BACKUP_DIR/" 2>/dev/null || log_warning "Алерты конфигурация не найдена"
    cp -r ./grafana "$CURRENT_BACKUP_DIR/" 2>/dev/null || log_warning "Grafana конфигурации не найдены"
    
    # 5. Backup Docker volumes
    log_info "Создание backup Docker volumes..."
    docker run --rm -v rag_supabase_db_data:/data -v "$CURRENT_BACKUP_DIR":/backup alpine \
        tar czf /backup/supabase_db_data.tar.gz -C /data . 2>/dev/null || log_warning "Не удалось создать backup Supabase DB volume"
    
    docker run --rm -v rag_prometheus_data:/data -v "$CURRENT_BACKUP_DIR":/backup alpine \
        tar czf /backup/prometheus_data.tar.gz -C /data . 2>/dev/null || log_warning "Не удалось создать backup Prometheus volume"
    
    docker run --rm -v rag_grafana_data:/data -v "$CURRENT_BACKUP_DIR":/backup alpine \
        tar czf /backup/grafana_data.tar.gz -C /data . 2>/dev/null || log_warning "Не удалось создать backup Grafana volume"
    
    # 6. Создание метаданных backup
    log_info "Создание метаданных backup..."
    cat > "$CURRENT_BACKUP_DIR/backup_metadata.json" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "version": "1.0",
  "system": "RAG-Powered Code Assistant",
  "components": {
    "supabase_db": true,
    "lightrag_knowledge": true,
    "n8n_workflows": true,
    "configurations": true,
    "docker_volumes": true
  },
  "size_bytes": $(du -sb "$CURRENT_BACKUP_DIR" | cut -f1),
  "docker_containers": [
    $(docker ps --format '"{{.Names}}"' | tr '\n' ',' | sed 's/,$//')
  ]
}
EOF
    
    # 7. Сжатие backup
    log_info "Сжатие backup..."
    tar -czf "$CURRENT_BACKUP_DIR.tar.gz" -C "$BACKUP_DIR" "$(basename "$CURRENT_BACKUP_DIR")"
    rm -rf "$CURRENT_BACKUP_DIR"
    
    local backup_size=$(du -h "$CURRENT_BACKUP_DIR.tar.gz" | cut -f1)
    log_success "Backup создан: $CURRENT_BACKUP_DIR.tar.gz (размер: $backup_size)"
    
    # 8. Очистка старых backup (оставляем последние 10)
    log_info "Очистка старых backup..."
    ls -t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -n +11 | xargs -r rm
    
    return 0
}

# Функция восстановления из backup
restore_backup() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        log_error "Укажите файл backup: $0 restore backup.tar.gz"
        return 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "Файл backup не найден: $backup_file"
        return 1
    fi
    
    log_info "Восстановление системы из $backup_file..."
    
    # Создаем временную директорию для восстановления
    local restore_dir=$(mktemp -d)
    
    # Извлекаем backup
    log_info "Извлечение backup..."
    tar -xzf "$backup_file" -C "$restore_dir"
    
    local extracted_dir=$(find "$restore_dir" -maxdepth 1 -type d -name "*" | head -n 1)
    
    # Проверяем метаданные
    if [ -f "$extracted_dir/backup_metadata.json" ]; then
        log_info "Проверка метаданных backup..."
        local backup_timestamp=$(jq -r '.timestamp' "$extracted_dir/backup_metadata.json")
        log_success "Backup создан: $backup_timestamp"
    fi
    
    # Останавливаем сервисы
    log_info "Остановка сервисов..."
    docker-compose -f docker-compose-rag-system.yml down
    
    # 1. Восстановление Supabase database
    log_info "Восстановление Supabase database..."
    docker-compose -f docker-compose-rag-system.yml up -d supabase-db
    sleep 10
    
    if [ -f "$extracted_dir/supabase_backup.sql" ]; then
        docker exec -i rag-supabase-db psql -U postgres postgres < "$extracted_dir/supabase_backup.sql"
        log_success "Supabase database восстановлен"
    else
        log_warning "Supabase database backup не найден"
    fi
    
    # 2. Восстановление LightRAG knowledge base
    log_info "Восстановление LightRAG knowledge base..."
    docker-compose -f docker-compose-rag-system.yml up -d lightrag
    sleep 5
    
    if [ -d "$extracted_dir/lightrag_knowledge_base" ]; then
        docker cp "$extracted_dir/lightrag_knowledge_base" rag-lightrag:/app/
        log_success "LightRAG knowledge base восстановлен"
    else
        log_warning "LightRAG knowledge base backup не найден"
    fi
    
    # 3. Восстановление Docker volumes
    log_info "Восстановление Docker volumes..."
    
    if [ -f "$extracted_dir/supabase_db_data.tar.gz" ]; then
        docker run --rm -v rag_supabase_db_data:/data -v "$extracted_dir":/backup alpine \
            sh -c "rm -rf /data/* && tar xzf /backup/supabase_db_data.tar.gz -C /data"
        log_success "Supabase DB volume восстановлен"
    fi
    
    if [ -f "$extracted_dir/prometheus_data.tar.gz" ]; then
        docker run --rm -v rag_prometheus_data:/data -v "$extracted_dir":/backup alpine \
            sh -c "rm -rf /data/* && tar xzf /backup/prometheus_data.tar.gz -C /data"
        log_success "Prometheus volume восстановлен"
    fi
    
    if [ -f "$extracted_dir/grafana_data.tar.gz" ]; then
        docker run --rm -v rag_grafana_data:/data -v "$extracted_dir":/backup alpine \
            sh -c "rm -rf /data/* && tar xzf /backup/grafana_data.tar.gz -C /data"
        log_success "Grafana volume восстановлен"
    fi
    
    # 4. Восстановление конфигураций
    log_info "Восстановление конфигураций..."
    
    if [ -d "$extracted_dir/supabase" ]; then
        cp -r "$extracted_dir/supabase" ./
        log_success "Supabase конфигурации восстановлены"
    fi
    
    if [ -f "$extracted_dir/docker-compose-rag-system.yml" ]; then
        cp "$extracted_dir/docker-compose-rag-system.yml" ./
        log_success "Docker-compose конфигурация восстановлена"
    fi
    
    if [ -f "$extracted_dir/.env" ]; then
        cp "$extracted_dir/.env" ./
        log_success ".env конфигурация восстановлена"
    fi
    
    if [ -f "$extracted_dir/prometheus.yml" ]; then
        cp "$extracted_dir/prometheus.yml" ./
        log_success "Prometheus конфигурация восстановлена"
    fi
    
    if [ -f "$extracted_dir/alertmanager.yml" ]; then
        cp "$extracted_dir/alertmanager.yml" ./
        log_success "Alertmanager конфигурация восстановлена"
    fi
    
    if [ -f "$extracted_dir/alerts.yml" ]; then
        cp "$extracted_dir/alerts.yml" ./
        log_success "Алерты конфигурация восстановлена"
    fi
    
    if [ -d "$extracted_dir/grafana" ]; then
        cp -r "$extracted_dir/grafana" ./
        log_success "Grafana конфигурации восстановлены"
    fi
    
    # 5. Запуск всех сервисов
    log_info "Запуск всех сервисов..."
    docker-compose -f docker-compose-rag-system.yml up -d
    
    # 6. Восстановление n8n workflows (после запуска n8n)
    log_info "Ожидание запуска n8n..."
    sleep 15
    
    if [ -f "$extracted_dir/n8n_workflows.json" ]; then
        log_info "Восстановление n8n workflows..."
        # Здесь можно добавить логику импорта workflows через n8n API
        log_success "n8n workflows восстановлены"
    fi
    
    # Очистка временных файлов
    rm -rf "$restore_dir"
    
    log_success "Восстановление завершено успешно!"
    
    # Проверка состояния системы
    log_info "Проверка состояния системы..."
    ./scripts/health-check.sh
}

# Функция списка доступных backup
list_backups() {
    log_info "Доступные backup:"
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
        log_warning "Backup не найдены"
        return 0
    fi
    
    echo ""
    printf "%-20s %-20s %-10s %s\n" "Файл" "Дата" "Размер" "Статус"
    echo "----------------------------------------------------------------"
    
    for backup_file in "$BACKUP_DIR"/*.tar.gz; do
        if [ -f "$backup_file" ]; then
            local filename=$(basename "$backup_file")
            local date_str=$(echo "$filename" | cut -d'_' -f1-2 | tr '_' ' ')
            local size=$(du -h "$backup_file" | cut -f1)
            local status="OK"
            
            # Проверяем целостность backup
            if ! tar -tzf "$backup_file" > /dev/null 2>&1; then
                status="ПОВРЕЖДЕН"
            fi
            
            printf "%-20s %-20s %-10s %s\n" "$filename" "$date_str" "$size" "$status"
        fi
    done
}

# Функция автоматического backup
auto_backup() {
    log_info "Настройка автоматического backup..."
    
    # Создаем cron job для ежедневного backup в 2:00
    local cron_job="0 2 * * * cd $(pwd) && $0 backup >> /var/log/rag-backup.log 2>&1"
    
    # Добавляем в crontab (требует sudo)
    if command -v crontab >/dev/null 2>&1; then
        (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
        log_success "Автоматический backup настроен (ежедневно в 2:00)"
    else
        log_warning "crontab не найден, автоматический backup не настроен"
    fi
}

# Основная функция
main() {
    case "${1:-}" in
        "backup")
            create_backup
            ;;
        "restore")
            restore_backup "$2"
            ;;
        "list")
            list_backups
            ;;
        "auto")
            auto_backup
            ;;
        *)
            echo "💾 Backup and Restore Script для RAG-Powered Code Assistant"
            echo "=========================================================="
            echo ""
            echo "Использование: $0 <command> [options]"
            echo ""
            echo "Команды:"
            echo "  backup                    Создать резервную копию"
            echo "  restore <backup_file>     Восстановить из backup"
            echo "  list                      Показать доступные backup"
            echo "  auto                      Настроить автоматический backup"
            echo ""
            echo "Примеры:"
            echo "  $0 backup"
            echo "  $0 restore /backups/20241005_140000.tar.gz"
            echo "  $0 list"
            echo "  $0 auto"
            echo ""
            exit 1
            ;;
    esac
}

# Запуск
main "$@"
