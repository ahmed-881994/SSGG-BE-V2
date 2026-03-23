# Repository Maintenance

- Branching Strategy
  - Default branch: `main`
  - Long-lived environment branches: `stage` (current branch)
  - Workflow:
    - Feature branches from `stage` → PR to `stage`
    - Release branches from `stage` → PR to `main`
    - Hotfix branches from `main` → PR to `main` and `stage`
  - Protect `main`; require PR reviews and passing checks

- Directory Layout
  - Application code in [../app/](../app/)
  - API routers in [../app/api/](../app/api)
  - Services in [../app/services/](../app/services)
  - Repositories in [../app/repositories/](../app/repositories)
  - Models in [../app/models/](../app/models)
  - Core infra (DB, middleware) in [../app/core/](../app/core)
  - Config in [../app/config/](../app/config)
  - Schemas in [../app/schemas/](../app/schemas)
  - Static in [../static/](../static/)
  - Deployment manifests in repo root and [../letsencrypt/](../letsencrypt)
  - CI configs in [../.github/workflows/](../.github/workflows)

- Environment Management
  - Base settings class: [../app/config/settings.py](../app/config/settings.py)
  - Preset env files in [../env/](../env/) and optional `.env`; keep secrets out of VCS
  - Required keys (see `Settings`): `environment`, `db_*`, `rds_*`, `secret_key`, `algorithm`, `access_token_expires_minutes`, `cors_origins`, `rate_limit_per_minute`, `smtp_*`

- Dependencies
  - Pin/update in [../requirements.txt](../requirements.txt)
  - Use virtualenv:
    - `python3 -m venv venv && source venv/bin/activate`
    - `pip install -r requirements.txt`

- Code Quality
  - Keep service/repository boundaries clean; avoid business logic in routers
  - Log with context using [../app/config/logging_config.py](../app/config/logging_config.py)
  - Prefer parameterized queries via SQLAlchemy; avoid raw SQL in routes (Visualizer enforces SELECT-only)
  - Add tests under `tests/` (recommended) for services and repositories

- Database Hygiene
  - SQLAlchemy models under [../app/models/](../app/models)
  - No dedicated migration tool is present; when schema changes:
    - Update models and DB schema in lockstep
    - Provide SQL migrations alongside PRs (e.g., `*.sql` scripts)
    - Coordinate deploy windows to avoid drift

- CI/CD
  - GitHub Actions in [../.github/workflows/](../.github/workflows) (build/test/lint/deploy as configured)
  - Enforce status checks before merging to `main`

- Auditing and Logging
  - Audits persisted via [../app/core/auditing_middleware.py](../app/core/auditing_middleware.py) to [../app/models/audit_model.py](../app/models/audit_model.py)
  - Ensure new endpoints avoid logging or mask sensitive fields per audit middleware rules

- Health Checks
  - `/health` and `/health/report` endpoints
  - Update health checks in [../app/services/healthcheck_service.py](../app/services/healthcheck_service.py) if new dependencies are added

- Security
  - JWT secrets and DB credentials via environment variables only
  - Keep Visualizer’s `EXCLUDED_TABLES` in [../app/api/visualizer.py](../app/api/visualizer.py) updated
  - Validate permission coverage for new routes via RBAC models and middleware

- Release Process
  - Bump version banners and docs where applicable
  - Tag releases; merge `stage` → `main` after verification
  - Run smoke tests against `/health` and core APIs post-deploy
