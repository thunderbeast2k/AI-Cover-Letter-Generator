# Multi-stage production build for AI Cover Letter Generator

# =========================================================================
# Stage 1: Build Frontend Vue 3 + Vite Application
# =========================================================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# =========================================================================
# Stage 2: Production Python WSGI Application (Waitress)
# =========================================================================
FROM python:3.11-slim AS production

# Install system utilities for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend application source
COPY backend/ ./backend/

# Copy compiled frontend distribution from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Set production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_HOST=0.0.0.0 \
    PORT=5000 \
    WAITRESS_THREADS=8 \
    FRONTEND_DIST_DIR=/app/frontend/dist

WORKDIR /app/backend

# Create temporary upload directory with secure permissions
RUN mkdir -p /app/backend/temp_uploads

EXPOSE 5000

# Health check verifies the live endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Start production Waitress server
CMD ["python", "serve.py", "--host", "0.0.0.0", "--port", "5000"]
