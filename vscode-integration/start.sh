#!/bin/bash

echo "🚀 Starting RAG-Powered VS Code Integration Stack..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration!"
    read -p "Press Enter after configuring .env file..."
fi

# Создаем необходимые директории
echo "📁 Creating directories..."
mkdir -p n8n/workflows
mkdir -p lightrag/config
mkdir -p supabase

# Инициализация базы данных
echo "🗄️ Initializing database..."
cat > supabase/init.sql << EOF
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create n8n database
CREATE DATABASE n8n;

-- Create vectors database for LightRAG
CREATE DATABASE vectors;

-- Create tables for code examples
CREATE TABLE IF NOT EXISTS code_examples (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    code TEXT NOT NULL,
    language TEXT NOT NULL,
    context JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for vector search
CREATE INDEX IF NOT EXISTS idx_code_examples_vector 
ON code_examples USING gin(context);
EOF

# Запуск Docker Compose
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Ожидание запуска сервисов
echo "⏳ Waiting for services to start..."
sleep 30

# Проверка статуса сервисов
echo "🔍 Checking service status..."
docker-compose ps

# Проверка здоровья сервисов
echo "🏥 Health check..."
curl -f http://localhost:9000/health || echo "❌ RAG Proxy not ready"
curl -f http://localhost:8000/health || echo "❌ LightRAG not ready"
curl -f http://localhost:5678/healthz || echo "❌ n8n not ready"

echo ""
echo "🎉 RAG-Powered VS Code Integration Stack is running!"
echo ""
echo "📊 Services:"
echo "  • RAG Proxy: http://localhost:9000"
echo "  • LightRAG: http://localhost:8000"
echo "  • n8n: http://localhost:5678"
echo "  • PostgreSQL: localhost:5432"
echo ""
echo "🔧 Next steps:"
echo "  1. Install VS Code extension from ./vscode-extension/"
echo "  2. Configure VS Code settings"
echo "  3. Start coding with AI assistance!"
echo ""
echo "📖 Logs: docker-compose logs -f [service-name]"
echo "🛑 Stop: docker-compose down"
