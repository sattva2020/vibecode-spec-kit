#!/bin/bash

# 📊 Monitoring Setup Script for RAG-Powered Code Assistant
# 
# Настраивает систему мониторинга:
# - Prometheus для сбора метрик
# - Grafana для визуализации
# - Алерты для критических событий
# - Дашборды для мониторинга системы

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация
PROMETHEUS_CONFIG_FILE="prometheus.yml"
GRAFANA_CONFIG_DIR="grafana"
ALERTMANAGER_CONFIG_FILE="alertmanager.yml"
ALERTS_CONFIG_FILE="alerts.yml"

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

# Создание конфигурации Prometheus
create_prometheus_config() {
    log_info "Создание конфигурации Prometheus..."
    
    cat > "$PROMETHEUS_CONFIG_FILE" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alerts.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # Prometheus сам себя
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # AI Router Service
  - job_name: 'ai-router'
    static_configs:
      - targets: ['ai-router:8000']
    metrics_path: /metrics
    scrape_interval: 10s

  # Supabase Database
  - job_name: 'supabase-db'
    static_configs:
      - targets: ['supabase-db:5432']
    metrics_path: /metrics
    scrape_interval: 30s

  # Ollama Service
  - job_name: 'ollama'
    static_configs:
      - targets: ['ollama:11434']
    metrics_path: /metrics
    scrape_interval: 15s

  # LightRAG Service
  - job_name: 'lightrag'
    static_configs:
      - targets: ['lightrag:8001']
    metrics_path: /metrics
    scrape_interval: 15s

  # n8n Workflows
  - job_name: 'n8n'
    static_configs:
      - targets: ['n8n:5678']
    metrics_path: /metrics
    scrape_interval: 30s

  # Docker containers
  - job_name: 'docker-containers'
    static_configs:
      - targets: ['host.docker.internal:9323']
    scrape_interval: 30s

  # Node Exporter (системные метрики)
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 15s
EOF

    log_success "Конфигурация Prometheus создана"
}

# Создание конфигурации Alertmanager
create_alertmanager_config() {
    log_info "Создание конфигурации Alertmanager..."
    
    cat > "$ALERTMANAGER_CONFIG_FILE" << 'EOF'
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@rag-system.local'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'default-receiver'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
    - match:
        severity: warning
      receiver: 'warning-alerts'

receivers:
  - name: 'default-receiver'
    webhook_configs:
      - url: 'http://localhost:5001/webhook'
        send_resolved: true

  - name: 'critical-alerts'
    webhook_configs:
      - url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        send_resolved: true
    email_configs:
      - to: 'admin@company.com'
        subject: 'CRITICAL ALERT: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}

  - name: 'warning-alerts'
    webhook_configs:
      - url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        send_resolved: true
EOF

    log_success "Конфигурация Alertmanager создана"
}

# Создание правил алертов
create_alerts_config() {
    log_info "Создание правил алертов..."
    
    cat > "$ALERTS_CONFIG_FILE" << 'EOF'
groups:
  - name: critical
    rules:
      # Критические алерты
      - alert: ServiceDown
        expr: up{job=~"ai-router|supabase-db|ollama|lightrag|n8n"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.instance }} is down"
          description: "Service {{ $labels.job }} on {{ $labels.instance }} has been down for more than 1 minute."

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: DatabaseConnectionFailure
        expr: pg_up == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: "Database connection failed"
          description: "PostgreSQL database is not accessible"

      - alert: HighMemoryUsage
        expr: (container_memory_usage_bytes / container_spec_memory_limit_bytes) > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage"
          description: "Container {{ $labels.name }} is using {{ $value }}% of its memory limit"

      - alert: HighCPUUsage
        expr: rate(container_cpu_usage_seconds_total[5m]) > 0.8
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High CPU usage"
          description: "Container {{ $labels.name }} is using {{ $value }}% CPU"

  - name: warning
    rules:
      # Предупреждающие алерты
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time"
          description: "95th percentile response time is {{ $value }}s"

      - alert: LowDiskSpace
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space"
          description: "Disk space is running low on {{ $labels.instance }}"

      - alert: HighAPIUsage
        expr: rate(ai_requests_total[1h]) > 1000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High API usage"
          description: "API usage rate is {{ $value }} requests per second"

      - alert: OllamaModelNotLoaded
        expr: ollama_model_loaded == 0
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Ollama model not loaded"
          description: "Required Ollama model is not loaded"

  - name: business
    rules:
      # Бизнес метрики
      - alert: LowCodeGenerationSuccess
        expr: rate(ai_requests_total{task_type="code_generation",status="success"}[1h]) < 0.8
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Low code generation success rate"
          description: "Code generation success rate is {{ $value }}"

      - alert: HighAPIErrorRate
        expr: rate(ai_requests_total{status="error"}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API error rate"
          description: "API error rate is {{ $value }}"
EOF

    log_success "Правила алертов созданы"
}

# Создание Grafana дашбордов
create_grafana_dashboards() {
    log_info "Создание Grafana дашбордов..."
    
    mkdir -p "$GRAFANA_CONFIG_DIR/dashboards"
    mkdir -p "$GRAFANA_CONFIG_DIR/provisioning/dashboards"
    mkdir -p "$GRAFANA_CONFIG_DIR/provisioning/datasources"
    
    # Конфигурация источника данных
    cat > "$GRAFANA_CONFIG_DIR/provisioning/datasources/prometheus.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

    # Конфигурация дашбордов
    cat > "$GRAFANA_CONFIG_DIR/provisioning/dashboards/dashboards.yml" << 'EOF'
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF

    # Основной дашборд системы
    cat > "$GRAFANA_CONFIG_DIR/dashboards/system-overview.json" << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "RAG System Overview",
    "tags": ["rag", "system"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "System Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=~\"ai-router|supabase-db|ollama|lightrag|n8n\"}",
            "legendFormat": "{{job}}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "green", "value": 1}
              ]
            }
          }
        }
      },
      {
        "id": 2,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(ai_requests_total[5m])",
            "legendFormat": "{{task_type}} - {{provider}}"
          }
        ]
      },
      {
        "id": 3,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "id": 4,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(ai_requests_total{status=\"error\"}[5m])",
            "legendFormat": "Errors per second"
          }
        ]
      },
      {
        "id": 5,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "container_memory_usage_bytes / 1024 / 1024",
            "legendFormat": "{{name}}"
          }
        ]
      },
      {
        "id": 6,
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total[5m]) * 100",
            "legendFormat": "{{name}}"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
EOF

    log_success "Grafana дашборды созданы"
}

# Добавление мониторинга в docker-compose
update_docker_compose() {
    log_info "Обновление docker-compose для мониторинга..."
    
    # Проверяем, есть ли уже секция мониторинга
    if grep -q "prometheus:" docker-compose-rag-system.yml; then
        log_warning "Мониторинг уже настроен в docker-compose"
        return 0
    fi
    
    # Добавляем сервисы мониторинга
    cat >> docker-compose-rag-system.yml << 'EOF'

  # ===========================================
  # MONITORING STACK
  # ===========================================
  prometheus:
    image: prom/prometheus:latest
    container_name: rag-prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./alerts.yml:/etc/prometheus/alerts.yml:ro
      - prometheus_data:/prometheus
    networks:
      - rag-network
    restart: unless-stopped

  alertmanager:
    image: prom/alertmanager:latest
    container_name: rag-alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
      - alertmanager_data:/alertmanager
    networks:
      - rag-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: rag-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
      - ./grafana/dashboards:/var/lib/grafana/dashboards:ro
    networks:
      - rag-network
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:latest
    container_name: rag-node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - rag-network
    restart: unless-stopped

volumes:
  prometheus_data:
  alertmanager_data:
  grafana_data:
EOF

    log_success "Docker-compose обновлен для мониторинга"
}

# Создание скрипта для запуска мониторинга
create_monitoring_scripts() {
    log_info "Создание скриптов мониторинга..."
    
    # Скрипт запуска мониторинга
    cat > "scripts/start-monitoring.sh" << 'EOF'
#!/bin/bash

echo "🚀 Запуск системы мониторинга..."

# Запуск сервисов мониторинга
docker-compose -f docker-compose-rag-system.yml up -d prometheus alertmanager grafana node-exporter

echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверка статуса
echo "📊 Проверка статуса мониторинга:"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana: http://localhost:3000 (admin/admin123)"
echo "  Alertmanager: http://localhost:9093"

# Проверка доступности
curl -f http://localhost:9090/-/healthy && echo "✅ Prometheus готов"
curl -f http://localhost:3000/api/health && echo "✅ Grafana готов"
curl -f http://localhost:9093/-/healthy && echo "✅ Alertmanager готов"

echo "🎉 Система мониторинга запущена!"
EOF

    chmod +x scripts/start-monitoring.sh
    
    # Скрипт остановки мониторинга
    cat > "scripts/stop-monitoring.sh" << 'EOF'
#!/bin/bash

echo "⏹️ Остановка системы мониторинга..."

docker-compose -f docker-compose-rag-system.yml stop prometheus alertmanager grafana node-exporter

echo "✅ Система мониторинга остановлена"
EOF

    chmod +x scripts/stop-monitoring.sh
    
    log_success "Скрипты мониторинга созданы"
}

# Основная функция
main() {
    echo "📊 Настройка системы мониторинга для RAG-Powered Code Assistant"
    echo "==============================================================="
    echo ""
    
    create_prometheus_config
    create_alertmanager_config
    create_alerts_config
    create_grafana_dashboards
    update_docker_compose
    create_monitoring_scripts
    
    echo ""
    echo "🎉 Система мониторинга настроена!"
    echo ""
    echo "📋 Следующие шаги:"
    echo "1. Запустите мониторинг: ./scripts/start-monitoring.sh"
    echo "2. Откройте Grafana: http://localhost:3000 (admin/admin123)"
    echo "3. Настройте алерты в Alertmanager: http://localhost:9093"
    echo "4. Проверьте метрики в Prometheus: http://localhost:9090"
    echo ""
    echo "📚 Документация:"
    echo "- Дашборды: grafana/dashboards/"
    echo "- Алерты: alerts.yml"
    echo "- Конфигурация: prometheus.yml, alertmanager.yml"
}

# Запуск
main "$@"
