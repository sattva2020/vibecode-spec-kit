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
