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
	docker build -t ssgg-be:v2 -f docker/dockerfile .
	```

- Run locally

	```bash
	docker run --env-file .env -p 8000:8000 ssgg-be:v2
	```

> Tip
> This runs only the API container. You still need MySQL and Redis running separately (via native services or the standalone containers above). If DB/Redis are on the host, set `db_host`/`rds_host` to `host.docker.internal` in the `.env` used by the container.

## 4) Docker Swarm + Traefik (Production / Staging)

Files:
- [../docker/traefik-stack.yml](../docker/traefik-stack.yml) (Traefik reverse proxy)
- [../docker/docker-stack.staging.yml](../docker/docker-stack.staging.yml)
- [../docker/docker-stack.production.yml](../docker/docker-stack.production.yml)
- [../docker/monitoring-stack.yml](../docker/monitoring-stack.yml)

### CI/CD Workflow

Automated builds and deployments are handled via GitHub Actions:

#### Main Application Workflow ([build_and_deploy.yml](../.github/workflows/build_and_deploy.yml))

**Deployment triggers:**
- **Staging**: Automatically deploys when pushing to:
  - `release/**` branches (e.g., `release/v2.1.0`) → tagged as `v2.1.0-rc`
  - `hotfix/**` branches (e.g., `hotfix/critical-fix`) → tagged as `v2.1.0-hotfix`
- **Production**: Automatically deploys when creating tags:
  - `v*` tags (e.g., `v2.1.0`) → production deployment
- **Build Only** (no deployment):
  - `main` branch pushes
  - `feature/**` branches
  - Pull requests to `main`

**Workflow steps:**
1. **Setup**: Determines environment and version from branch/tag
2. **Build**: Builds Docker image and pushes to GitHub Container Registry (ghcr.io)
3. **Deploy**: Deploys to target environment using Docker Swarm
4. **Health Check**: Verifies deployment success
5. **Release** (production only): Creates GitHub release

**Image tags:**
- Staging: `ghcr.io/ahmed-881994/ssgg-be-v2:v{VERSION}-rc`
- Production: `ghcr.io/ahmed-881994/ssgg-be-v2:v{VERSION}`
- Latest: `ghcr.io/ahmed-881994/ssgg-be-v2:latest` (main branch)

**Deployment URLs:**
- Staging: https://api.stg.sportingscout.org
- Production: https://api.sportingscout.org

#### Infrastructure Workflows

These are **manual workflows** (workflow_dispatch) for infrastructure setup:

1. **Traefik Deployment** ([deploy_traefik.yml](../.github/workflows/deploy_traefik.yml))
   - Must be deployed first (reverse proxy)
   - Handles TLS termination and routing
   - Health check: https://traefik.sportingscout.org/ping

2. **Monitoring Deployment** ([deploy_monitoring.yml](../.github/workflows/deploy_monitoring.yml))
   - Deploys Prometheus, Grafana, Loki, Tempo, Promtail
   - Independent of application deployments
   - Health checks for all monitoring services

### Manual Deployment

If needed, you can deploy manually:

```bash
# Initialize swarm (first time only)
docker swarm init

# 1. Deploy Traefik (if not already deployed)
docker stack deploy -c docker/traefik-stack.yml traefik

# 2. Deploy Monitoring (if not already deployed)
docker stack deploy -c docker/monitoring-stack.yml ssgg-monitoring

# 3. Build and push application image
docker build -t ghcr.io/ahmed-881994/ssgg-be-v2:v2.0.0 -f docker/dockerfile .
docker push ghcr.io/ahmed-881994/ssgg-be-v2:v2.0.0

# 4. Deploy application stack
# Set IMAGE_TAG and other env vars first
export IMAGE_TAG=v2.0.0
docker stack deploy -c docker/docker-stack.staging.yml ssgg-be-v2-staging
# or
docker stack deploy -c docker/docker-stack.production.yml ssgg-be-v2-production
```

### Prerequisites

- Docker Swarm initialized on target node(s)
- GitHub secrets configured:
  - `GH_TOKEN` - GitHub token with package write permissions
  - `SSH_HOST`, `SSH_USER`, `SSH_PRIVATE_KEY` - SSH credentials for Swarm manager
  - Database, Redis, JWT, SMTP secrets (see [../app/config/settings.py](../app/config/settings.py))
  - `TRAEFIK_AUTH`, `MONITORING_AUTH`, `GRAFANA_PASSWORD` - Infrastructure auth credentials
- DNS records pointing to your Swarm node:
  - `api.sportingscout.org` (production)
  - `api.stg.sportingscout.org` (staging)
  - `prometheus.sportingscout.org`, `grafana.sportingscout.org`, etc. (monitoring)

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

## 6.1) Monitoring Stack (Prometheus & Grafana)

The project includes a comprehensive observability stack using Prometheus, Grafana, Loki, and Tempo to monitor both staging and production environments.

### Architecture

- **Prometheus**: Collects metrics from API instances, system resources, and services
- **Grafana**: Visualizes metrics through dashboards
- **Loki**: Collects and indexes logs
- **Tempo**: Distributed tracing backend
- **Promtail**: Log collection agent that ships logs to Loki

### Deployment

The monitoring stack is deployed independently via a **manual workflow** in GitHub Actions.

**Prerequisites**:
1. Ensure Traefik is deployed first (handles routing and TLS)
2. Configure monitoring secrets in GitHub:
   ```bash
   MONITORING_AUTH=<basic auth credentials>
   GRAFANA_ADMIN_USER=admin
   GRAFANA_PASSWORD=<secure password>
   ```

3. Ensure DNS records point to your server:
   - `prometheus.sportingscout.org`
   - `grafana.sportingscout.org`
   - `loki.sportingscout.org`
   - `tempo.sportingscout.org`

**Deployment via GitHub Actions**:

1. Go to: **Actions → Deploy Monitoring → Run workflow**
2. The workflow will:
   - Deploy the monitoring stack to Docker Swarm
   - Verify health of all services (Prometheus, Grafana, Loki, Tempo)

**Manual deployment** (alternative):
```bash
# Prepare environment file
cat > .env << EOF
MONITORING_AUTH=<basic auth>
GRAFANA_ADMIN_USER=admin
GRAFANA_PASSWORD=<password>
CONFIG_VERSION=$(git rev-parse HEAD)
EOF

# Deploy stack
docker stack deploy -c docker/monitoring-stack.yml ssgg-monitoring

# Verify deployment
docker stack ps ssgg-monitoring
```

**Verify deployment**:
```bash
# Check services
docker stack ps ssgg-monitoring

# View logs
docker service logs ssgg-monitoring_prometheus -f
docker service logs ssgg-monitoring_grafana -f

# Health checks
curl -u admin:password https://prometheus.sportingscout.org/-/ready
curl https://grafana.sportingscout.org/api/health
curl https://loki.sportingscout.org/ready
curl https://tempo.sportingscout.org/ready
```

### Metrics Exposed

The FastAPI application exposes metrics at `/metrics` endpoint, including:

**Application Metrics** (auto-instrumented):
- `http_requests_total` - Total HTTP requests by method, endpoint, and status
- `http_request_duration_seconds` - Request duration histograms (p50, p95, p99)
- `http_request_size_bytes` - Request size metrics
- `http_response_size_bytes` - Response size metrics

**Custom Health Metrics**:
- `ssgg_db_health_status` - Database health status (1=healthy, 0=unhealthy)
- `ssgg_db_response_time_ms` - Database query response time
- `ssgg_db_connection_pool_size` - Connection pool size
- `ssgg_db_active_connections` - Active database connections
- `ssgg_redis_health_status` - Redis health status (1=healthy, 0=unhealthy)
- `ssgg_redis_response_time_ms` - Redis operation response time
- `ssgg_redis_operations_total` - Total Redis operations by type and status

All metrics are labeled with `environment="staging"` or `environment="production"` for easy filtering.

### Access

- **Prometheus**: https://prometheus.sportingscout.org (requires basic auth)
- **Grafana**: https://grafana.sportingscout.org (login: admin / `$GRAFANA_PASSWORD`)
- **Loki**: https://loki.sportingscout.org (accessed via Grafana)
- **Tempo**: https://tempo.sportingscout.org (accessed via Grafana)

### Grafana Dashboard Setup

Import recommended community dashboards:

1. **FastAPI Observability** (Dashboard ID: 16110)
   - API request rates, latencies, error rates
   - Environment-based filtering

2. **Node Exporter Full** (Dashboard ID: 1860)
   - System metrics: CPU, memory, disk, network
   - Per-node monitoring

**For Docker/Container monitoring**:

Due to datasource variable issues with many community dashboards, we recommend:

**Option A: Create custom dashboards**
- Build your own dashboards using the PromQL queries in the "Sample Queries" section below
- This ensures compatibility with your Prometheus setup

**Option B: Search for tested dashboards**
- Look for dashboards that explicitly support Prometheus (not using datasource variables)
- Test with a small dashboard first before importing complex ones
- Check dashboard reviews/comments for datasource issues

**Troubleshooting datasource errors:**

If you encounter `Datasource ${DS_PROMETHEUS} was not found`:
1. Download the dashboard JSON instead of importing by ID
2. Edit the JSON file and replace all instances of `"datasource": "${DS_PROMETHEUS}"` with `"datasource": "Prometheus"`
3. Import the modified JSON in Grafana

Example fix:
```bash
# Download dashboard JSON, replace datasource variable, then import
curl -o dashboard.json https://grafana.com/api/dashboards/<ID>/revisions/latest/download
sed -i 's/"datasource": "${DS_PROMETHEUS}"/"datasource": "Prometheus"/g' dashboard.json
# Then import dashboard.json via Grafana UI
```

Import steps:
1. Go to Grafana → Dashboards → Import
2. Enter dashboard ID or upload JSON file
3. Select "Prometheus" as the data source
4. Click Import

### Sample Queries

Monitor production API performance:
```promql
# Request rate (requests per second)
rate(http_requests_total{environment="production"}[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{environment="production"}[5m]))

# Error rate
rate(http_requests_total{environment="production",status=~"5.."}[5m])

# Database health across all replicas
min(ssgg_db_health_status{environment="production"})

# Connection pool utilization
ssgg_db_active_connections / ssgg_db_connection_pool_size * 100
```

Compare staging vs production:
```promql
# Response time comparison
ssgg_db_response_time_ms{environment=~"staging|production"}
```

### Alerting (Optional)

To configure alerts, create `prometheus-alerts.yml` and add to Prometheus config:
```yaml
groups:
  - name: ssgg_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
      
      - alert: DatabaseUnhealthy
        expr: ssgg_db_health_status == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database health check failing"
      
      - alert: HighDatabaseLatency
        expr: ssgg_db_response_time_ms > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database queries are slow"
```

### Maintenance

**Data retention**: Prometheus retains 30 days of metrics (configurable in [../docker/monitoring-stack.yml](../docker/monitoring-stack.yml))

**Reload configuration**:
```bash
# Update config files in configs/ directory
# Redeploy stack to apply changes
docker stack deploy -c docker/monitoring-stack.yml ssgg-monitoring
```

**Backup Grafana dashboards**:
```bash
# Export volume
docker run --rm -v ssgg-monitoring_grafana-data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz /data
```

See [../configs/grafana/provisioning/dashboards/README.md](../configs/grafana/provisioning/dashboards/README.md) for detailed dashboard configuration.

## 7) Post-Deploy Verification

- Smoke tests:
	- `GET /health` — status healthy
	- Core routes (Members, Entities, Events) return 200 and expected schema
- RBAC:
	- Validate role/permission enforcement via [../app/api/permissions.py](../app/api/permissions.py) and [../app/api/roles.py](../app/api/roles.py)
- Audit:
	- Confirm audit entries appear for non-excluded paths (see exclusions in middleware)
