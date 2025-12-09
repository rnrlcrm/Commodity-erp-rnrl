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
# Use PORT environment variable (default 8080 for Cloud Run compatibility)
PORT=${PORT:-8080}
echo "Listening on port $PORT"

# Add verbose error output
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT 2>&1 || {
    echo "Failed to start uvicorn, trying to import app directly to see error:"
    python -c "from backend.app.main import app; print('App imported successfully')" 2>&1
    exit 1
}
