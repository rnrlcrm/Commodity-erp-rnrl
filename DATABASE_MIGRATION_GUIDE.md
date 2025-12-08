# 🔄 Database Migration Workflow - Developer Guide

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [The Migration Flow](#the-migration-flow)
3. [Creating New Migrations](#creating-new-migrations)
4. [Testing Migrations Locally](#testing-migrations-locally)
5. [CI/CD Protection](#cicd-protection)
6. [Deployment Process](#deployment-process)
7. [Troubleshooting](#troubleshooting)
8. [Rules & Best Practices](#rules--best-practices)

---

## 🚀 Quick Start

### First Time Setup

```bash
# 1. Ensure PostgreSQL is running
docker-compose up -d postgres

# 2. Verify connection
psql postgresql://commodity_user:commodity_password@localhost:5432/commodity_erp

# 3. Check current migration state
cd backend
alembic current

# 4. Apply all migrations
alembic upgrade head
```

### Daily Development

```bash
# 1. Edit your SQLAlchemy models
vim backend/modules/partners/models.py

# 2. Generate migration automatically
cd backend
alembic revision --autogenerate -m "add partner rating field"

# 3. Review generated migration
cat db/migrations/versions/XXXXX_add_partner_rating_field.py

# 4. Test migration
alembic upgrade head

# 5. Commit and push
git add .
git commit -m "feat: add partner rating field"
git push
```

---

## 🔁 The Migration Flow

```
Developer edits models
        ↓
Creates Alembic migration
        ↓
Pushes code to GitHub
        ↓
CI verifies migration is valid ✅
        ↓
Deploy → Google Cloud DB applies migration
        ↓
Other developers run `alembic upgrade head`
        ↓
Everyone stays in sync 🎯
```

### Key Principles

1. **Models are Source of Truth** - SQLAlchemy models define the schema
2. **Alembic Tracks Changes** - Migrations are version-controlled
3. **CI Blocks Bad Migrations** - Automated tests prevent errors
4. **Deployment is Automated** - Migrations run before app starts

---

## ✨ Creating New Migrations

### When to Create a Migration

Create a migration whenever you:
- Add/remove a table
- Add/remove/modify a column
- Add/remove an index
- Add/remove a constraint
- Change column types
- Add/remove relationships

### Automatic Migration Generation

**Recommended for most changes:**

```bash
cd backend

# Generate migration from model changes
alembic revision --autogenerate -m "descriptive message"

# Examples of good messages:
alembic revision --autogenerate -m "add user avatar field"
alembic revision --autogenerate -m "add index on partner created_at"
alembic revision --autogenerate -m "change price column to decimal"
```

### Manual Migration Creation

**Use for complex operations:**

```bash
cd backend

# Create empty migration
alembic revision -m "custom data migration"
```

Then edit the generated file:

```python
def upgrade() -> None:
    # Custom SQL or data transformation
    op.execute("""
        UPDATE business_partners 
        SET status = 'active' 
        WHERE status IS NULL
    """)

def downgrade() -> None:
    # Reverse the operation
    op.execute("""
        UPDATE business_partners 
        SET status = NULL 
        WHERE status = 'active'
    """)
```

### Migration Naming Conventions

| Change Type | Example Migration Name |
|-------------|------------------------|
| Add field | `add_user_phone_number` |
| Remove field | `remove_deprecated_tax_field` |
| Add index | `add_index_on_partner_email` |
| Add table | `create_audit_log_table` |
| Data migration | `migrate_old_status_values` |
| Rename field | `rename_gstin_to_tax_id` |

---

## 🧪 Testing Migrations Locally

### Before Committing

```bash
cd backend

# 1. Apply migration
alembic upgrade head

# 2. Check if it worked
alembic current

# 3. Test downgrade (reversibility)
alembic downgrade -1

# 4. Re-apply
alembic upgrade head

# 5. Verify no schema drift
alembic revision --autogenerate -m "check" || true
git diff db/migrations/versions/  # Should show no changes
rm -f db/migrations/versions/*check.py
```

### Testing on Fresh Database

```bash
# Drop and recreate database
docker exec commodity-erp-postgres psql -U commodity_user -d postgres -c "DROP DATABASE IF EXISTS commodity_erp;"
docker exec commodity-erp-postgres psql -U commodity_user -d postgres -c "CREATE DATABASE commodity_erp;"

# Apply all migrations from scratch
cd backend
alembic upgrade head

# Verify all tables created
docker exec commodity-erp-postgres psql -U commodity_user -d commodity_erp -c "\dt"
```

---

## 🛡️ CI/CD Protection

### Automated Checks on Every PR

When you create a pull request, GitHub Actions automatically:

1. **Lints migration files** for syntax errors
2. **Tests migrations** on fresh PostgreSQL database
3. **Checks for missing migrations** (model changes without migration)
4. **Tests reversibility** (downgrade/upgrade)
5. **Security scans** for dangerous SQL operations

### What CI Blocks

❌ **PR will be BLOCKED if:**
- Migration file has syntax errors
- Migration fails to apply
- Models changed but no migration created
- Migration contains `DROP DATABASE`
- Downgrade function is missing

✅ **PR will PASS if:**
- All migrations apply successfully
- No schema drift detected
- Security checks pass
- Downgrade/upgrade cycle works

### Viewing CI Results

```bash
# Push your branch
git push origin feature/add-rating

# GitHub Actions will run automatically
# Check status at: https://github.com/rnrlcrm/Commodity-erp-rnrl/actions

# Fix any errors shown in CI output
# Push fixes until all checks pass ✅
```

---

## 🚀 Deployment Process

### How Migrations Run in Production

```yaml
# Cloud Build automatically runs this on deploy:

1. Pull latest code
2. Build Docker image
3. Run migrations (scripts/run_migrations.sh)
4. Start application

# If migration fails → deployment fails ❌
# If migration succeeds → app starts ✅
```

### Migration Script Workflow

The `scripts/run_migrations.sh` script:

1. Checks `DATABASE_URL` is set
2. Tests database connection
3. Shows current migration state
4. Runs `alembic upgrade head`
5. Verifies migrations succeeded
6. Starts application

### Monitoring Deployments

```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Check for migration errors
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~'migration'" --limit 20
```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue: "Migration failed - column already exists"

**Cause:** Database and migrations out of sync

**Fix:**
```bash
# Option 1: Mark database as current
cd backend
alembic stamp head

# Option 2: Drop and recreate local DB
docker exec commodity-erp-postgres psql -U commodity_user -d postgres -c "DROP DATABASE commodity_erp CASCADE;"
docker exec commodity-erp-postgres psql -U commodity_user -d postgres -c "CREATE DATABASE commodity_erp;"
alembic upgrade head
```

#### Issue: "Can't locate revision identified by 'XXXXX'"

**Cause:** Migration file missing or not committed

**Fix:**
```bash
# Pull latest migrations
git pull origin main

# Verify migration files exist
ls -la backend/db/migrations/versions/
```

#### Issue: "Target database is not up to date"

**Cause:** Local DB behind remote

**Fix:**
```bash
cd backend
alembic upgrade head
```

#### Issue: "Autogenerate created empty migration"

**Cause:** No model changes detected or imports missing in `env.py`

**Fix:**
```bash
# Check if your model is imported in env.py
cat backend/db/migrations/env.py | grep "your_model"

# If missing, add import:
from backend.modules.your_module.models import YourModel  # noqa: F401
```

---

## 📜 Rules & Best Practices

### ✅ DO

- **Always use Alembic** for schema changes
- **Test migrations locally** before pushing
- **Write descriptive migration names**
- **Include both upgrade() and downgrade()**
- **Commit migration files** with code changes
- **Review auto-generated migrations** before committing
- **Run `alembic upgrade head`** after pulling changes

### ❌ DON'T

- **Never modify the database manually** in staging/production
- **Never edit existing migrations** (create new ones instead)
- **Never use `DROP DATABASE`** in migrations
- **Never skip CI checks** ("I'll fix it later")
- **Never deploy without migrations** if models changed
- **Never commit without testing** migrations locally

### Critical Rules

| Rule | Why | Consequence if Violated |
|------|-----|------------------------|
| Models changed → Create migration | Keeps DB in sync | Production breaks 💥 |
| Test migration locally | Catches errors early | CI blocks PR ❌ |
| Never edit existing migrations | Breaks history | Others can't upgrade |
| Always have downgrade() | Enables rollbacks | Can't undo changes |
| Run migrations before app | Ensures schema ready | App crashes on startup |

---

## 📊 Migration Lifecycle

### Baseline → Incremental → Sync

```
Baseline Migration (Dec 8, 2025)
        ↓
    baseline_v1_2025_12_08
        ↓
Future Migrations (autogenerated)
        ↓
    add_partner_rating_field
        ↓
    add_trade_amendments_table
        ↓
    add_index_on_availability_status
        ↓
    ... (continues)
```

### Version Control

```bash
# Current baseline
revision: baseline_v1_2025_12_08
down_revision: None  # This is the start

# Future migrations link to it
revision: abc123_add_rating
down_revision: baseline_v1_2025_12_08  # Links to previous

# Next migration links to previous
revision: def456_add_index
down_revision: abc123_add_rating  # Chain continues
```

---

## 🎯 Quick Reference

### Common Commands

```bash
# Check current state
alembic current

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "description"

# Show migration history
alembic history

# Upgrade to specific revision
alembic upgrade abc123

# Show raw SQL without executing
alembic upgrade head --sql

# Mark database at specific revision
alembic stamp revision_id
```

### Environment Variables

```bash
# Local development
export DATABASE_URL="postgresql://commodity_user:commodity_password@localhost:5432/commodity_erp"

# CI/CD (automatically set)
export DATABASE_URL="postgresql://test_user:test_password@localhost:5432/test_db"

# Google Cloud Run (automatically set from secret)
export DATABASE_URL="postgresql://user:pass@/clouddb?host=/cloudsql/project:region:instance"
```

---

## 📞 Getting Help

- **Migration fails locally:** Check logs in `/tmp/migrations.log`
- **CI blocking your PR:** Read the error output in GitHub Actions
- **Schema drift detected:** Run `alembic upgrade head` locally
- **Stuck on production:** Check Cloud Run logs in GCP Console

---

**Last Updated:** December 8, 2025  
**Baseline Version:** `baseline_v1_2025_12_08`  
**Database:** PostgreSQL 15  
**Migration Tool:** Alembic 1.13+

