# Multi-stage Dockerfile for CyberScope Enterprise Platform
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements-production.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements-production.txt

# Production stage
FROM base as production

# Create non-root user
RUN groupadd -r cyberscope && useradd -r -g cyberscope cyberscope

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/models /app/data/cache /app/data/exports && \
    chown -R cyberscope:cyberscope /app

# Switch to non-root user
USER cyberscope

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 8000 9090

# Default command (can be overridden)
CMD ["gunicorn", "backend.main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--access-logfile", "-", "--error-logfile", "-"]

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-asyncio black flake8 mypy

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /app/logs /app/models /app/data/cache /app/data/exports

# Expose ports
EXPOSE 8000 9090

# Development command
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Streamlit frontend stage
FROM base as frontend

# Install Streamlit and additional frontend dependencies
RUN pip install --no-cache-dir streamlit plotly

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /app/.streamlit

# Copy Streamlit config
COPY .streamlit/config.toml /app/.streamlit/

# Create non-root user
RUN groupadd -r streamlit && useradd -r -g streamlit streamlit && \
    chown -R streamlit:streamlit /app

USER streamlit

# Expose Streamlit port
EXPOSE 5000

# Streamlit command
CMD ["streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0"]