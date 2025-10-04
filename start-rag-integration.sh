#!/bin/bash

echo "🚀 Starting Vibecode Spec Kit with RAG Integration..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "📝 Creating .env file for RAG integration..."
    cat > .env << EOF
# Vibecode Spec Kit RAG Integration Configuration

# PostgreSQL Configuration
POSTGRES_PASSWORD=vibecode123

# n8n Configuration
N8N_USER=admin
N8N_PASSWORD=admin123

# OpenAI API Key (for LightRAG)
OPENAI_API_KEY=your_openai_api_key_here

# Ollama Configuration (optional)
OLLAMA_HOST=localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b

# RAG Integration URLs
RAG_PROXY_URL=http://localhost:9000
LIGHTRAG_URL=http://localhost:8000
N8N_URL=http://localhost:5678
EOF
    echo "⚠️  Please edit .env file with your OpenAI API key!"
    read -p "Press Enter after configuring .env file..."
fi

# Создаем необходимые директории
echo "📁 Creating directories..."
mkdir -p vscode-integration/n8n/workflows
mkdir -p vscode-integration/lightrag/config
mkdir -p supabase

# Инициализация базы данных для RAG
echo "🗄️ Initializing RAG database..."
cat > supabase/init.sql << EOF
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create n8n database
CREATE DATABASE n8n;

-- Create vectors database for LightRAG
CREATE DATABASE vectors;

-- Create tables for Vibecode Spec Kit integration
CREATE TABLE IF NOT EXISTS spec_kit_context (
    id SERIAL PRIMARY KEY,
    project_name TEXT NOT NULL,
    mode TEXT NOT NULL,
    context_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tables for code examples with Spec Kit metadata
CREATE TABLE IF NOT EXISTS code_examples (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    code TEXT NOT NULL,
    language TEXT NOT NULL,
    spec_type TEXT,
    complexity_level INTEGER,
    context JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for vector search
CREATE INDEX IF NOT EXISTS idx_code_examples_vector 
ON code_examples USING gin(context);

-- Create index for Spec Kit context
CREATE INDEX IF NOT EXISTS idx_spec_kit_context 
ON spec_kit_context USING gin(context_data);
EOF

# Проверяем наличие Memory Bank
if [ ! -d "memory-bank" ]; then
    echo "📋 Initializing Memory Bank..."
    python memory-bank-cli.py init --constitution --templates
fi

# Create cache directory for RAG Proxy
echo "📁 Creating RAG Proxy cache directory..."
mkdir -p rag-proxy/cache

# Запуск Docker Compose
echo "🐳 Starting RAG-integrated Docker containers..."
docker-compose -f docker-compose-rag.yml up -d

# Ожидание запуска сервисов
echo "⏳ Waiting for services to start..."
sleep 30

# Проверка статуса сервисов
echo "🔍 Checking service status..."
docker-compose -f docker-compose-rag.yml ps

# Проверка здоровья сервисов
echo "🏥 Health check..."
curl -f http://localhost:9000/health || echo "❌ RAG Proxy not ready"
curl -f http://localhost:8000/health || echo "❌ LightRAG not ready"
curl -f http://localhost:5678/healthz || echo "❌ n8n not ready"

# Тестирование RAG интеграции с Spec Kit
echo "🧪 Testing RAG integration with Spec Kit..."
python memory-bank-cli.py rag status

echo ""
echo "🎉 Vibecode Spec Kit with RAG Integration is running!"
echo ""
echo "📊 Services:"
echo "  • Vibecode Spec Kit CLI: python memory-bank-cli.py"
echo "  • RAG Proxy: http://localhost:9000"
echo "  • LightRAG: http://localhost:8000"
echo "  • n8n: http://localhost:5678"
echo "  • PostgreSQL: localhost:5432"
echo ""
echo "🔧 RAG Commands:"
echo "  • python memory-bank-cli.py rag status"
echo "  • python memory-bank-cli.py rag suggest --code 'const user = '"
echo "  • python memory-bank-cli.py rag learn --code 'function login() {}'"
echo "  • python memory-bank-cli.py rag search 'authentication'"
echo "  • python memory-bank-cli.py rag integrate --spec-type 'level3'"
echo ""
echo "📖 Logs: docker-compose -f docker-compose-rag.yml logs -f [service-name]"
echo "🛑 Stop: docker-compose -f docker-compose-rag.yml down"
echo ""
echo "💡 The RAG system is now integrated with your Vibecode Spec Kit!"
echo "   It will learn from your code and provide context-aware suggestions"
echo "   based on Spec Kit methodologies and your Memory Bank context."
