# ===========================================
# LightRAG Docker Configuration
# ===========================================

FROM python:3.11-slim

# Set working directory
WORKDIR /workspace/lightrag

# Install system dependencies
RUN apt-get update && apt-get install -y \
  build-essential \
  curl \
  git \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /workspace/lightrag/data \
  /workspace/lightrag/models \
  /workspace/lightrag/logs

# Set environment variables
ENV PYTHONPATH=/workspace/lightrag
ENV LIGHTRAG_WORKSPACE=/workspace/lightrag
ENV LIGHTRAG_HOST=0.0.0.0
ENV LIGHTRAG_PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "-m", "lightrag.server"]
