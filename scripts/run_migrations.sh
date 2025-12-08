#!/bin/bash
#
# Migration Runner Script for Production Deployments
#
# This script MUST run before the application starts to ensure
# the database schema is up-to-date.
#
# Usage:
#   ./scripts/run_migrations.sh
#
# Environment Variables Required:
#   DATABASE_URL - PostgreSQL connection string
#
# Exit Codes:
#   0 - Success
#   1 - Migration failed
#   2 - Environment check failed

set -e  # Exit on any error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# ============================================
# CONFIGURATION
# ============================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/../backend" && pwd)"
LOG_FILE="${LOG_FILE:-/tmp/migrations.log}"

# ============================================
# COLORS FOR OUTPUT
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================
# LOGGING FUNCTIONS
# ============================================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "${LOG_FILE}"
}

# ============================================
# PRE-FLIGHT CHECKS
# ============================================
preflight_checks() {
    log_info "Running pre-flight checks..."
    
    # Check if DATABASE_URL is set
    if [ -z "${DATABASE_URL:-}" ]; then
        log_error "DATABASE_URL environment variable is not set"
        log_error "Example: postgresql://user:password@host:5432/dbname"
        exit 2
    fi
    
    # Check if alembic is available
    if ! command -v alembic &> /dev/null; then
        log_error "Alembic is not installed"
        log_error "Install it with: pip install alembic"
        exit 2
    fi
    
    # Check if backend directory exists
    if [ ! -d "${BACKEND_DIR}" ]; then
        log_error "Backend directory not found: ${BACKEND_DIR}"
        exit 2
    fi
    
    # Check if migrations directory exists
    if [ ! -d "${BACKEND_DIR}/db/migrations" ]; then
        log_error "Migrations directory not found: ${BACKEND_DIR}/db/migrations"
        exit 2
    fi
    
    log_success "Pre-flight checks passed"
}

# ============================================
# DATABASE CONNECTION TEST
# ============================================
test_database_connection() {
    log_info "Testing database connection..."
    
    cd "${BACKEND_DIR}"
    
    # Try to get current alembic revision
    if alembic current 2>&1 | tee -a "${LOG_FILE}"; then
        log_success "Database connection successful"
        return 0
    else
        log_error "Cannot connect to database"
        log_error "Check your DATABASE_URL: ${DATABASE_URL}"
        exit 1
    fi
}

# ============================================
# SHOW CURRENT MIGRATION STATE
# ============================================
show_migration_state() {
    log_info "Current migration state:"
    cd "${BACKEND_DIR}"
    alembic current 2>&1 | tee -a "${LOG_FILE}"
}

# ============================================
# RUN MIGRATIONS
# ============================================
run_migrations() {
    log_info "Running database migrations..."
    
    cd "${BACKEND_DIR}"
    
    # Show what migrations will be applied
    log_info "Pending migrations:"
    alembic heads 2>&1 | tee -a "${LOG_FILE}"
    
    # Run migrations
    if alembic upgrade head 2>&1 | tee -a "${LOG_FILE}"; then
        log_success "Migrations applied successfully"
        return 0
    else
        log_error "Migration failed!"
        log_error "Check logs at: ${LOG_FILE}"
        exit 1
    fi
}

# ============================================
# VERIFY MIGRATION SUCCESS
# ============================================
verify_migrations() {
    log_info "Verifying migrations..."
    
    cd "${BACKEND_DIR}"
    
    # Check current revision
    CURRENT_REVISION=$(alembic current 2>&1 | grep -oP '(?<=\(head\) )[a-zA-Z0-9_]+' || echo "unknown")
    
    if [ "${CURRENT_REVISION}" != "unknown" ]; then
        log_success "Database is at revision: ${CURRENT_REVISION}"
        return 0
    else
        log_warning "Could not verify current revision"
        alembic current 2>&1 | tee -a "${LOG_FILE}"
    fi
}

# ============================================
# MAIN EXECUTION
# ============================================
main() {
    log_info "=========================================="
    log_info "🚀 Starting Migration Runner"
    log_info "=========================================="
    log_info "Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
    log_info "Log file: ${LOG_FILE}"
    log_info ""
    
    preflight_checks
    echo ""
    
    test_database_connection
    echo ""
    
    show_migration_state
    echo ""
    
    run_migrations
    echo ""
    
    verify_migrations
    echo ""
    
    log_success "=========================================="
    log_success "✅ Migration Runner Completed Successfully"
    log_success "=========================================="
    
    # Pass through any additional command (e.g., start app)
    if [ $# -gt 0 ]; then
        log_info "Executing: $@"
        exec "$@"
    fi
}

# Run main function with all arguments
main "$@"
