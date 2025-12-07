#!/bin/bash
set -e

echo "Running database migrations..."
cd /app/backend && alembic upgrade head

echo "Starting FastAPI application..."
exec python -m uvicorn backend.app.main:create_app --factory --host 0.0.0.0 --port 8000
