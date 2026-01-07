# Architecture

This service implements a clean, layered architecture with clear boundaries and responsibilities.

- Entry Point and Routing
  - FastAPI app defined in [../main.py](../main.py)
  - Routers included:
    - Members: [../app/api/members.py](../app/api/members.py) → [../app/services/member_service.py](../app/services/member_service.py)
    - Entities: [../app/api/entities.py](../app/api/entities.py) → [../app/services/entity_service.py](../app/services/entity_service.py)
    - Events: [../app/api/events.py](../app/api/events.py) → [../app/services/event_service.py](../app/services/event_service.py)
    - Permissions: [../app/api/permissions.py](../app/api/permissions.py) → [../app/services/permission_service.py](../app/services/permission_service.py)
    - Roles: [../app/api/roles.py](../app/api/roles.py) → [../app/services/role_service.py](../app/services/role_service.py)
    - Users: [../app/api/users.py](../app/api/users.py) → [../app/services/user_service.py](../app/services/user_service.py)
    - Lookups: [../app/api/lookups.py](../app/api/lookups.py)
    - Health: [../app/api/health.py](../app/api/health.py) → [../app/services/healthcheck_service.py](../app/services/healthcheck_service.py)
    - Visualizer: [../app/api/visualizer.py](../app/api/visualizer.py) (safe SQL SELECT validation)

- Middleware Pipeline (in order, see [../main.py](../main.py))
  1) Access control: [../app/core/access_control_middleware.py](../app/core/access_control_middleware.py)
  2) User context: [../app/core/user_context_middleware.py](../app/core/user_context_middleware.py)
  3) Auditing: [../app/core/auditing_middleware.py](../app/core/auditing_middleware.py) persists to [../app/models/audit_model.py](../app/models/audit_model.py)
  4) Logging: [../app/core/logging_middleware.py](../app/core/logging_middleware.py)
  5) Rate limiting: [../app/core/rate_limitting.py](../app/core/rate_limitting.py)

- Error Handling
  - Centralized exception handlers in [../main.py](../main.py) for domain and auth errors defined in [../app/core/exceptions.py](../app/core/exceptions.py)
  - Database integrity errors surfaced as 400/500 via handlers in [../main.py](../main.py)

- Configuration and Settings
  - Settings class in [../app/config/settings.py](../app/config/settings.py) maps environment variables:
    - DB: `db_host`, `db_port`, `db_database`, `db_username`, `db_password`
    - Pool hints: `db_max_connections`, `db_min_connections`
    - Redis: `rds_host`, `rds_port`, `rds_database`
    - JWT: `secret_key`, `algorithm`, `access_token_expires_minutes`
    - CORS, rate limiting, SMTP, `log_level`
  - Loaded before router inclusion to configure middlewares and CORS

- Database Layer
  - Engines and sessions in [../app/core/database.py](../app/core/database.py):
    - Sync engine with `QueuePool`
    - Async engine for background/middleware needs
    - Session factories and FastAPI dependencies for scoped sessions
  - Models (sample domain):
    - Members: [../app/models/member_model.py](../app/models/member_model.py)
    - Entities and membership: [../app/models/entity_model.py](../app/models/entity_model.py), [../app/models/entity_member_model.py](../app/models/entity_member_model.py)
    - RBAC: [../app/models/rbac_models.py](../app/models/rbac_models.py), [../app/models/permission_model.py](../app/models/permission_model.py), [../app/models/role_model.py](../app/models/role_model.py), [../app/models/role_permission_model.py](../app/models/role_permission_model.py)
    - Events and attendance: [../app/models/event_model.py](../app/models/event_model.py), [../app/models/attendance_model.py](../app/models/attendance_model.py), [../app/models/attendance_state_model.py](../app/models/attendance_state_model.py)
    - Audit: [../app/models/audit_model.py](../app/models/audit_model.py)
  - Repository abstraction:
    - Base: [../app/repositories/base_repository.py](../app/repositories/base_repository.py)
    - Concrete repos encapsulate queries and transactions:
      - Members: [../app/repositories/member_repository.py](../app/repositories/member_repository.py)
      - Entities: [../app/repositories/entity_repository.py](../app/repositories/entity_repository.py)
      - Events: [../app/repositories/event_repository.py](../app/repositories/event_repository.py)
      - Roles: [../app/repositories/role_repository.py](../app/repositories/role_repository.py)
      - Permissions: [../app/repositories/permission_repository.py](../app/repositories/permission_repository.py)
      - Lookups: [../app/repositories/lookup_repository.py](../app/repositories/lookup_repository.py)

- Service Layer
  - Business orchestration and validation:
    - [../app/services/member_service.py](../app/services/member_service.py)
    - [../app/services/entity_service.py](../app/services/entity_service.py)
    - [../app/services/event_service.py](../app/services/event_service.py)
    - [../app/services/auth_service.py](../app/services/auth_service.py), [../app/services/token_service.py](../app/services/token_service.py)
    - [../app/services/permission_service.py](../app/services/permission_service.py), [../app/services/role_service.py](../app/services/role_service.py)
    - [../app/services/healthcheck_service.py](../app/services/healthcheck_service.py)

- Request Lifecycle (example)
  1) Request enters via FastAPI route (e.g., [../app/api/members.py](../app/api/members.py))
  2) Middlewares attach context, enforce ACL, audit, and log
  3) Route depends on a scoped DB session from dependencies in [../app/core/database.py](../app/core/database.py)
  4) Route calls Service; Service uses Repository to query/update models
  5) Response serialized via Pydantic schemas in [../app/schemas/](../app/schemas)
  6) Audit record saved by middleware in [../app/core/auditing_middleware.py](../app/core/auditing_middleware.py)

- Health and Diagnostics
  - Summary: GET `/health` (see [../app/api/health.py](../app/api/health.py))
  - Full report: GET `/health/report`
  - Pool introspection implemented in [../app/services/healthcheck_service.py](../app/services/healthcheck_service.py)
  - Structured logs formatted by [../app/config/logging_config.py](../app/config/logging_config.py)

- Security Notes
  - AuthN via JWT in Authorization header; token verification in [../app/services/token_service.py](../app/services/token_service.py)
  - RBAC enforced by access control middleware and route dependencies
  - Sensitive fields are masked in audits via [../app/core/auditing_middleware.py](../app/core/auditing_middleware.py)
  - Visualizer endpoint validates SELECT-only, excludes tables list in [../app/api/visualizer.py](../app/api/visualizer.py)
