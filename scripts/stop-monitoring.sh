#!/bin/bash

echo "⏹️ Остановка системы мониторинга..."

docker-compose -f docker-compose-rag-system.yml stop prometheus alertmanager grafana node-exporter

echo "✅ Система мониторинга остановлена"
