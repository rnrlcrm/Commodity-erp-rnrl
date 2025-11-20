# Release Checklist: Organization Settings Module

Use this checklist before merging to `main` to avoid broken deployments.

## 1. Branch & Sync
- [ ] Feature branch name: `feat/org-settings-final` (or update below).
- [ ] `git fetch origin` executed.
- [ ] `git checkout main && git pull --ff-only origin main` clean.
- [ ] `git checkout feat/org-settings-final && git rebase origin/main` completed (no conflicts remain).

## 2. Migrations
- [ ] Alembic heads count == 1 (`alembic heads`).
- [ ] New migration: `202511201030_add_financial_year_version.py` present.
- [ ] Test upgrade on clean DB:
  ```bash
  docker run -d --name release_pg -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=cotton_dev -p 55434:5432 postgres:15
  export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:55434/cotton_dev
  alembic upgrade head
  ```
- [ ] Rollback smoke (optional): `alembic downgrade -1` then `upgrade head` again.

## 3. Tests
- [ ] Install dev deps: `pip install -e backend[dev]`.
- [ ] Unit tests pass: `pytest -k organization_settings -q`.
- [ ] Integration test passes: `pytest backend/tests/integration/test_organization_settings_api.py -q`.
- [ ] Full suite (optional): `pytest -q` (or in CI). 

## 4. Static Analysis
- [ ] Ruff: `ruff check backend/modules/settings/organization` no critical errors.
- [ ] Mypy: `mypy backend/modules/settings/organization` passes or acceptable ignores.

## 5. Observability
- [ ] `/metrics` endpoint reachable locally: `curl http://localhost:8000/metrics | grep organization_document_number_latency_seconds`.
- [ ] Prometheus client dependency added (`prometheus-client` in `pyproject.toml` and `requirements.txt`).

## 6. API Contract
- [ ] Docs updated: `docs/api/organization_settings.md` reflects final endpoints and concurrency section.
- [ ] No duplicate headings / lint warnings (run markdown linter if available).

## 7. Performance Scripts
- [ ] Locust script exists: `scripts/perf/organization_settings_locust.py`.
- [ ] K6 script exists: `scripts/perf/organization_settings_k6.js`.
- [ ] Dry run (optional): start app and run 30s load; confirm no errors.

## 8. CI Workflow
- [ ] Workflow `.github/workflows/organization-settings-tests.yml` contains ruff, mypy, subset tests + coverage badge generation.
- [ ] Confirm run succeeded on latest branch push.

## 9. Commit & PR
- [ ] Stage new/changed files: `git add -A`.
- [ ] Commit message follows conventional format: `feat(settings/organization): complete module ...`.
- [ ] Push branch: `git push -u origin feat/org-settings-final`.
- [ ] Open PR: `gh pr create --fill --base main`.
- [ ] Review diff: ensure only intended files (no stray temp or editor artifacts).

## 10. Post-Merge
- [ ] Merge PR (squash recommended for clean history).
- [ ] Tag release: `git tag -a org-settings-v1 -m "Organization settings module v1" && git push origin org-settings-v1`.
- [ ] Record version in CHANGELOG (optional future step).

## 11. Rollback Plan (Optional)
- [ ] If production issues, revert commit: `git revert <merge_commit_sha>`.
- [ ] Downgrade migration: `alembic downgrade -1` if version column causes issues.

## 12. What to Monitor After Deploy
- Latency histogram: `organization_document_number_latency_seconds` (watch p95/p99).
- Version conflicts counter: `financial_year_version_conflicts_total` (should be low; spikes indicate client stale versions).
- Error rate for 4xx on organization settings endpoints.

## 13. Common Pitfalls
- Forgetting version in financial year PATCH requests (returns 400).
- Missing migration application leads to `version` column errors.
- Running tests against SQLite hides Postgres-specific constraint behavior—always run one Postgres suite before merge.

## Quick Commands Recap
```bash
git checkout -B feat/org-settings-final
git add -A
git commit -m "feat(settings/organization): complete module"
git fetch origin
git checkout main && git pull --ff-only origin main
git checkout feat/org-settings-final && git rebase origin/main
pytest -k organization_settings -q
git push -u origin feat/org-settings-final
gh pr create --fill --base main
```

Keep this checklist updated if process changes.