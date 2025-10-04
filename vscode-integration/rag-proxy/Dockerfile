FROM rust:1.75-slim as builder

WORKDIR /app

# Установка зависимостей
RUN apt-get update && apt-get install -y \
  pkg-config \
  libssl-dev \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Копирование Cargo.toml и Cargo.lock
COPY Cargo.toml Cargo.lock ./

# Скачивание зависимостей
RUN cargo fetch

# Копирование исходного кода
COPY src ./src

# Сборка приложения
RUN cargo build --release

# Финальный образ
FROM debian:bookworm-slim

WORKDIR /app

# Установка runtime зависимостей
RUN apt-get update && apt-get install -y \
  curl \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Копирование собранного приложения
COPY --from=builder /app/target/release/rag-proxy /app/rag-proxy

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["./rag-proxy"]
