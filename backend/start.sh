#!/bin/bash
set -e

echo "=== Container Starting ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Checking alembic.ini..."
ls -la /app/backend/alembic.ini || echo "alembic.ini not found!"
echo "Checking migrations directory..."
ls -la /app/backend/db/migrations/ || echo "migrations dir not found!"
echo "DATABASE_URL set: ${DATABASE_URL:+YES}"
echo "=======================

"

echo "Running database migrations..."
cd /app/backend
python -m alembic upgrade head

echo "Starting FastAPI application..."
exec python -m uvicorn backend.app.main:create_app --factory --host 0.0.0.0 --port 8000
