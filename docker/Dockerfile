# Multi-stage Dockerfile for building and running the application

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY frontend/ .

# Build frontend
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./backend/static

# Create static directory if it doesn't exist
RUN mkdir -p ./backend/static

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Expose port
EXPOSE 8000

# Run the application
# Railway provides PORT environment variable
CMD ["python", "backend/start.py"]

