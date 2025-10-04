# ===========================================
# RAG Proxy (Rust) Docker Configuration
# ===========================================

FROM rust:1.75-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
  build-essential \
  curl \
  pkg-config \
  libssl-dev \
  && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/src/app

# Copy Cargo files
COPY Cargo.toml Cargo.lock ./

# Create dummy main.rs to build dependencies
RUN mkdir src && echo "fn main() {}" > src/main.rs

# Build dependencies
RUN cargo build --release

# Copy source code
COPY src ./src

# Build the application
RUN cargo build --release

# Runtime stage
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
  ca-certificates \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Copy the binary from builder stage
COPY --from=builder /usr/src/app/target/release/rag-proxy /usr/local/bin/rag-proxy

# Create app user
RUN useradd -r -s /bin/false appuser && \
  mkdir -p /app/data /app/logs && \
  chown -R appuser:appuser /app

# Switch to app user
USER appuser

# Set working directory
WORKDIR /app

# Set environment variables
ENV RAG_PROXY_HOST=0.0.0.0
ENV RAG_PROXY_PORT=8080

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Start command
CMD ["rag-proxy"]