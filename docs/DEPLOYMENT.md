# Deployment

This project supports multiple deployment targets: local development, Docker Swarm with Traefik.

## 1) Configuration

Populate environment variables per [../app/config/settings.py](../app/config/settings.py). Examples:
- Core: `environment`, `log_level`, `cors_origins`, `rate_limit_per_minute`
- DB: `db_host`, `db_port`, `db_database`, `db_username`, `db_password`
- Redis: `rds_host`, `rds_port`, `rds_database`
- JWT: `secret_key`, `algorithm`, `access_token_expires_minutes`
- SMTP: `smtp_server`, `smtp_port`, `smtp_username`, `smtp_password`, `from_email`

Use env presets under [../env/](../env/), or a root `.env`. Never commit secrets.

## 2) Local Development

- Install deps and run

	```bash
	python3 -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt
	uvicorn main:app --reload
	```

- App mounts static at `/static` (see [../main.py](../main.py))
- Health:
	- `GET /health` — summary from [../app/services/healthcheck_service.py](../app/services/healthcheck_service.py)
	- `GET /health/report` — full diagnostics

> Note
> There is no Docker Swarm "stack" for local development. Run the API directly (uvicorn) and use either local services or individual Docker containers for MySQL and Redis.

### Local services (DB/Cache) options

- Option A — Use native services (macOS Homebrew)

	```bash
	brew install mysql redis
	brew services start mysql
	brew services start redis
	```

- Option B — Run standalone containers

	```bash
	# MySQL 8 (data persisted in a named volume)
	docker run -d --name ssgg-mysql \
		-e MYSQL_ROOT_PASSWORD=changeme \
		-e MYSQL_DATABASE=ssgg \
		-p 3306:3306 \
		-v ssgg-mysql:/var/lib/mysql \
		mysql:8.0 \
		--character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

	# Redis 7
	docker run -d --name ssgg-redis \
		-p 6379:6379 \
		-v ssgg-redis:/data \
		redis:7-alpine
	```

Configure `db_host` and `rds_host` accordingly:
- If the API runs on your host (uvicorn): `db_host=127.0.0.1`, `rds_host=127.0.0.1`.
- If the API runs in a Docker container: use `host.docker.internal` to reach host services.

## 3) Docker (Local / Testing)

- Build image

	```bash
	docker build -t ssgg-be:v2 -f dockerfile .
	```

- Run locally

	```bash
	docker run --env-file .env -p 8000:8000 ssgg-be:v2
	```

> Tip
> This runs only the API container. You still need MySQL and Redis running separately (via native services or the standalone containers above). If DB/Redis are on the host, set `db_host`/`rds_host` to `host.docker.internal` in the `.env` used by the container.

## 4) Docker Swarm + Traefik (Production / Staging)

> [!NOTE]
> below steps are performed by the `build_and_deploy` workflow.

Files:
- [../docker-stack-traefik.yml](../docker-stack-traefik.yml) (Traefik reverse proxy)
- [../docker-stack.staging.yml](../docker-stack.staging.yml)
- [../docker-stack.production.yml](../docker-stack.production.yml)
- Certificates storage under [../letsencrypt/](../letsencrypt/)

Build:
```bash
docker build -t ssgg-be:v2 -f dockerfile .
docker tag ssgg-be:v2 your-docker-repo/ssgg-be:v2
docker push your-docker-repo/ssgg-be:v2
```

Deploy:

```bash
# initialize swarm (first manager)
docker swarm init

# staging
docker stack deploy -c docker-stack.staging.yml ssgg

# production
docker stack deploy -c docker-stack.production.yml ssgg
```

Traefik:
- Routes traffic to the FastAPI service
- Terminates TLS using ACME (see `letsencrypt/acme.json`)

Prerequisites/Notes:
- Ensure the Traefik stack is deployed first (e.g., `docker stack deploy -c docker-stack-traefik.yml traefik`).
- Provide required environment variables/secrets referenced by the stacks on the Swarm managers.
- Create any named volumes on target nodes if the stacks expect them.

CI/CD:
- Automated builds/deployments are handled via GitHub Actions in [.github/workflows/](../.github/workflows) (e.g., staging and production pipelines). These workflows build the image and run `docker stack deploy` against your Swarm.

## 5) Database and Schema

- SQLAlchemy models: [../app/models/](../app/models)
- No migration tool is included; apply schema changes manually or via managed migrations (PR must include SQL or steps)
- Ensure collation/charset support (`utf8mb4`)
- Connection pooling via `QueuePool` (sync engine) in [../app/core/database.py](../app/core/database.py)

## 6) Observability and Operations

- Logging:
	- Structured logs through [../app/config/logging_config.py](../app/config/logging_config.py)
	- Request-context fields: request_id, method, url, status, time, client_ip
- Auditing:
	- [../app/core/auditing_middleware.py](../app/core/auditing_middleware.py) persists to [../app/models/audit_model.py](../app/models/audit_model.py)
	- Sensitive data masking implemented for requests/responses
- Health:
	- `/health` (summary) and `/health/report` (full)
	- Checks include: DB connectivity, pool status, DB schema presence, environment, Redis
- Security:
	- JWT enforced via [../app/services/token_service.py](../app/services/token_service.py) and access control middleware
	- Visualizer endpoint strictly validates SELECTs and excludes sensitive tables (see [../app/api/visualizer.py](../app/api/visualizer.py))
- Backups:
	- Maintain DB backups and snapshot policies externally (see any provided SQL dumps like [../Dump20250715.sql](../Dump20250715.sql))

## 7) Post-Deploy Verification

- Smoke tests:
	- `GET /health` — status healthy
	- Core routes (Members, Entities, Events) return 200 and expected schema
- RBAC:
	- Validate role/permission enforcement via [../app/api/permissions.py](../app/api/permissions.py) and [../app/api/roles.py](../app/api/roles.py)
- Audit:
	- Confirm audit entries appear for non-excluded paths (see exclusions in middleware)
