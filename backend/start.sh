#!/bin/bash
set -e

echo "Running database migrations..."
# Use the comprehensive migration script that handles extensions
# Auto-detect script location (works in dev and prod)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_SCRIPT="${SCRIPT_DIR}/../scripts/run_migrations.sh"

if [ -f "$MIGRATION_SCRIPT" ]; then
    "$MIGRATION_SCRIPT"
else
    echo "Warning: Migration script not found at $MIGRATION_SCRIPT"
    echo "Running migrations directly..."
    cd "${SCRIPT_DIR}"
    python -m alembic upgrade head
fi

echo "Starting FastAPI application..."
exec python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
