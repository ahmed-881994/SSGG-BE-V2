# Deployment

This project supports multiple deployment targets: local development, Docker Swarm with Traefik.

## 1) Configuration

Populate environment variables per [../app/config/settings.py](../app/config/settings.py). Examples:
- Core: `environment`, `log_level`, `cors_origins`, `rate_limit_per_minute`
- DB: `db_host`, `db_port`, `db_database`, `db_username`, `db_password`, `db_max_connections`, `db_min_connections`
- Redis: `rds_host`, `rds_port`, `rds_database`
- JWT: `secret_key`, `algorithm`, `access_token_expires_minutes`
- SMTP: `smtp_server`, `smtp_port`, `smtp_username`, `smtp_password`, `from_email`
- OpenTelemetry (optional): `otel_exporter_otlp_endpoint`, `otel_service_name`, `otel_log_correlation`

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
> There is no Docker Swarm "stack" for local development. Run the API directly (uvicorn) and use either local services or individual Docker containers for MySQL and Redis. The staging and production Docker stacks include MySQL and Redis as integrated services, but for local development you need to run them separately.

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
> This runs only the API container. You still need MySQL and Redis running separately (via native services or the standalone containers above). MySQL and Redis are only bundled with the production/staging Docker Swarm stacks, not with the standalone Docker image. If DB/Redis are on the host, set `db_host`/`rds_host` to `host.docker.internal` in the `.env` used by the container.

## 4) Docker Swarm + Traefik (Production / Staging)

Files:
- [../docker/traefik-stack.yml](../docker/traefik-stack.yml) (Traefik reverse proxy)
- [../docker/docker-stack.staging.yml](../docker/docker-stack.staging.yml) (1 replica, MySQL on port 3316, Redis on port 6378)
- [../docker/docker-stack.production.yml](../docker/docker-stack.production.yml) (5 replicas, MySQL on port 3306, Redis on port 6379)
- [../docker/monitoring-stack.yml](../docker/monitoring-stack.yml) (Prometheus, Grafana, Loki, Tempo, Promtail, Node Exporter)

### Stack Configuration Details

**Staging Stack:**
- API: 1 replica
- Update strategy: `start-first`, parallelism 1, 5s delay, rollback on failure
- MySQL: `mysql:lts` on port 3316 (host) with healthcheck
- Redis: `redis:7` on port 6378 (host) with healthcheck
- Network: `stg-internal` (overlay) + `traefik-public` (external)
- Logging: Loki driver with `environment=staging` label

**Production Stack:**
- API: 5 replicas for high availability
- Update strategy: `start-first`, parallelism 1, 5s delay, rollback on failure
- MySQL: `mysql:lts` on port 3306 (host) with healthcheck
- Redis: `redis:7` on port 6379 (host) with healthcheck
- Network: `prd-internal` (overlay) + `traefik-public` (external)
- Logging: Loki driver with `environment=production` label
- Healthcheck: 60s interval, 10s timeout, 30s start period for all services

**Common Configuration:**
- Stop grace period: 5s for fast container replacement
- Restart policy: `on-failure` with delay 5s, max 3 attempts
- TLS: Let's Encrypt via Traefik with HTTP challenge
- Ingress: Traefik with host-based routing

### CI/CD Workflow

Automated builds and deployments are handled via GitHub Actions:

#### Main Application Workflow ([build_and_deploy.yml](../.github/workflows/build_and_deploy.yml))

**Deployment triggers:**
- **Staging**: Automatically deploys when pushing to:
  - `release/**` branches (e.g., `release/v2.1.0`) → tagged as `v{VERSION}-rc` (from VERSION file)
  - `hotfix/**` branches (e.g., `hotfix/critical-fix`) → tagged as `v{VERSION}-hotfix`
- **Production**: Automatically deploys when creating tags:
  - `v*` tags (e.g., `v2.1.0`) → production deployment (tag name used as image tag)
- **Build Only** (no deployment):
  - `main` branch pushes → tagged as `latest` and `v{VERSION}-{git-sha}`
  - `feature/**` branches → tagged as `v{VERSION}-{git-sha}`
- **Manual Trigger**: Supports `workflow_dispatch` with environment selection (staging/production)

**Workflow steps:**
1. **Setup**: Reads VERSION file and determines environment and image tag from branch/tag
2. **Build**: Builds Docker image with buildx caching and pushes to GitHub Container Registry (ghcr.io)
3. **Deploy**: Deploys to target environment using Docker Swarm (cssnr/stack-deploy-action)
4. **Health Check**: Waits 15s (staging) or 20s (production), then verifies /health endpoint
5. **Release** (production only): Creates GitHub release with changelog

**Image tags:**
- Staging (release branch): `ghcr.io/ahmed-881994/ssgg-be-v2:v{VERSION}-rc`
- Staging (hotfix branch): `ghcr.io/ahmed-881994/ssgg-be-v2:v{VERSION}-hotfix`
- Production: `ghcr.io/ahmed-881994/ssgg-be-v2:v{VERSION}` (from tag)
- Latest: `ghcr.io/ahmed-881994/ssgg-be-v2:latest` (main branch only)
- Environment-specific: `{environment}-latest` (for tracking)

**Deployment URLs:**
- Staging: https://api.stg.sportingscout.org
- Production: https://api.sportingscout.org

**Stack Configuration:**
- Staging: 1 replica, uses `stg-internal` network
- Production: 5 replicas, uses `prd-internal` network
- Both: Include MySQL 8 LTS and Redis 7 as part of the stack
- Both: Loki logging driver enabled with environment-specific labels

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

# 1. Create traefik-public network (required for all stacks)
docker network create --driver=overlay traefik-public

# 2. Deploy Traefik (if not already deployed)
docker stack deploy -c docker/traefik-stack.yml traefik

# 3. Deploy Monitoring (if not already deployed)
export CONFIG_VERSION=$(git rev-parse HEAD)
export GRAFANA_ADMIN_USER=admin
export GRAFANA_PASSWORD=<your-password>
export MONITORING_AUTH=<basic-auth-string>
docker stack deploy -c docker/monitoring-stack.yml ssgg-monitoring

# 4. Build and push application image
export VERSION=$(cat VERSION)
docker build -t ghcr.io/ahmed-881994/ssgg-be-v2:v${VERSION} -f docker/dockerfile .
docker push ghcr.io/ahmed-881994/ssgg-be-v2:v${VERSION}

# 5. Deploy application stack
# Create .env file with all required variables (see Prerequisites section above)
cat > .env << EOF
environment=staging
db_host=mysql
db_port=3306
db_database=ssgg
db_username=ssgg_user
db_password=<db-password>
db_max_connections=10
db_min_connections=2
rds_host=redis
rds_port=6379
rds_database=0
secret_key=<jwt-secret>
algorithm=HS256
access_token_expires_minutes=30
cors_origins=*
rate_limit_per_minute=60
log_level=INFO
smtp_server=<smtp-server>
smtp_port=587
smtp_username=<username>
smtp_password=<password>
from_email=<from-email>
MYSQL_ROOT_PASSWORD=<root-password>
MYSQL_DATABASE=ssgg
MYSQL_USER=ssgg_user
MYSQL_PASSWORD=<db-password>
IMAGE_TAG=v${VERSION}
EOF

# Deploy staging
docker stack deploy -c docker/docker-stack.staging.yml ssgg-be-v2-staging

# OR deploy production
docker stack deploy -c docker/docker-stack.production.yml ssgg-be-v2-production
```

**Important Notes:**
- Each stack (staging/production) includes its own MySQL and Redis instances
- Service names within stacks: `mysql`, `redis`, `api`
- API connects to MySQL/Redis using service names (DNS resolution via overlay network)
- Staging uses `stg-internal` network, production uses `prd-internal` network
- Both connect to `traefik-public` network for ingress routing

### Prerequisites

- Docker Swarm initialized on target node(s)
- GitHub secrets configured:
  - `GH_TOKEN` - GitHub token with package write permissions
  - `SSH_HOST`, `SSH_USER`, `SSH_PRIVATE_KEY` - SSH credentials for Swarm manager
  - Database secrets: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `MYSQL_ROOT_PASSWORD`
  - Connection pool: `DB_MAX_CONNECTIONS`, `DB_MIN_CONNECTIONS`
  - Redis secrets: `REDIS_HOST`, `REDIS_PORT`, `REDIS_DATABASE`
  - JWT secrets: `JWT_SECRET`, `JWT_ALGORITHM`
  - JWT variables: `JWT_EXPIRES_IN`
  - Security variables: `RATE_LIMIT_PER_MINUTE`, `LOG_LEVEL`
  - SMTP secrets: `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`
  - Infrastructure auth: `TRAEFIK_AUTH`, `MONITORING_AUTH`, `GRAFANA_ADMIN_USER`, `GRAFANA_PASSWORD`
- DNS records pointing to your Swarm node:
  - `api.sportingscout.org` (production)
  - `api.stg.sportingscout.org` (staging)
  - `traefik.sportingscout.org` (Traefik dashboard)
  - `prometheus.sportingscout.org`, `grafana.sportingscout.org`, `loki.sportingscout.org`, `tempo.sportingscout.org` (monitoring)
- Traefik stack must be deployed first (provides `traefik-public` network)

**Note**: MySQL and Redis are deployed as services within the staging and production stacks, not as external dependencies. Each environment has its own isolated MySQL and Redis instances:
- **Staging**: MySQL on port 3316 (host), Redis on port 6378 (host), network `stg-internal`
- **Production**: MySQL on port 3306 (host), Redis on port 6379 (host), network `prd-internal`

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

- **Prometheus**: Collects metrics from API instances, system resources, and services (30-day retention)
- **Grafana**: Visualizes metrics through dashboards (provisioned datasources disabled by default)
- **Loki 3.0.0**: Collects and indexes logs (exposed on port 3100)
- **Tempo 2.6.1**: Distributed tracing backend (exposed on ports 3200, 4317, 4318 for OTLP)
- **Promtail 3.0.0**: Log collection agent (deployed globally on all nodes)
- **Node Exporter**: System metrics collection (deployed globally on all nodes)

**Network Architecture:**
- All monitoring services connect to three networks:
  - `traefik-public`: For external access via Traefik
  - `stg-internal`: To scrape staging stack metrics
  - `prd-internal`: To scrape production stack metrics
- Placement: All services run on manager nodes except Promtail and Node Exporter (global mode)

### Deployment

The monitoring stack is deployed independently via a **manual workflow** in GitHub Actions.

**Prerequisites**:
1. Ensure Traefik is deployed first (handles routing and TLS, provides `traefik-public` network)
2. Configure monitoring secrets in GitHub:
   ```bash
   MONITORING_AUTH=<basic auth credentials>  # Format: username:password (will be hashed)
   GRAFANA_ADMIN_USER=admin
   GRAFANA_PASSWORD=<secure password>
   ```

3. Ensure DNS records point to your server:
   - `prometheus.sportingscout.org`
   - `grafana.sportingscout.org`
   - `loki.sportingscout.org`
   - `tempo.sportingscout.org`
   - `traefik.sportingscout.org`

4. All monitoring services require basic auth except Grafana (uses its own authentication)
   - Default basic auth user: `admin` (password hash generated from MONITORING_AUTH)

**Deployment via GitHub Actions**:

1. Go to: **Actions → Deploy Monitoring → Run workflow**
2. The workflow will:
   - Deploy the monitoring stack to Docker Swarm
   - Verify health of all services (Prometheus, Grafana, Loki, Tempo)

**Manual deployment** (alternative):
```bash
# Prepare environment file
cat > .env << EOF
MONITORING_AUTH=<basic auth - will be hashed by Traefik>
GRAFANA_ADMIN_USER=admin
GRAFANA_PASSWORD=<password>
CONFIG_VERSION=$(git rev-parse HEAD)
EOF

# Deploy stack
docker stack deploy -c docker/monitoring-stack.yml ssgg-monitoring

# Verify deployment
docker stack ps ssgg-monitoring
```

**Configuration Management:**
- Monitoring configs use Docker configs with versioning: `{config-name}-${CONFIG_VERSION}`
- Config files:
  - `configs/prometheus/prometheus.yml`
  - `configs/loki/loki-config.yml`
  - `configs/promtail/promtail-config.yml`
  - `configs/tempo/tempo-config.yml`
  - `configs/grafana/provisioning/datasources/datasources.yml` (disabled by default)
- To update configs: modify files, change CONFIG_VERSION, redeploy stack

**Verify deployment**:
```bash
# Check services
docker stack ps ssgg-monitoring

# View logs
docker service logs ssgg-monitoring_prometheus -f
docker service logs ssgg-monitoring_grafana -f
docker service logs ssgg-monitoring_loki -f
docker service logs ssgg-monitoring_tempo -f

# Health checks (as performed by GitHub Actions)
curl -s -o /dev/null -w "%{http_code}" https://prometheus.sportingscout.org/-/ready  # Should return 200
curl -s -o /dev/null -w "%{http_code}" https://grafana.sportingscout.org/api/health  # Should return 200
curl -s -o /dev/null -w "%{http_code}" https://loki.sportingscout.org/ready  # Should return 200
curl -s -o /dev/null -w "%{http_code}" https://tempo.sportingscout.org/ready  # Should return 200
curl -s -o /dev/null -w "%{http_code}" https://traefik.sportingscout.org/ping  # Should return 200
```

### Logging Integration

Both staging and production stacks integrate with Loki for centralized logging:

**Loki Driver Configuration:**
```yaml
x-logging: &default-logging
  driver: loki
  options:
    loki-url: "http://loki:3100/loki/api/v1/push"
    loki-batch-size: "400"
    loki-retries: "2"
    loki-external-labels: "environment=staging,stack=ssgg-be-v2-staging"
```

**Applied to all services:**
- MySQL, Redis, and API containers automatically ship logs to Loki
- Environment-specific labels for filtering: `environment=staging` or `environment=production`
- Stack-specific labels: `stack=ssgg-be-v2-staging` or `stack=ssgg-be-v2-production`
- Query logs in Grafana using LogQL with these labels

**Note:** Ensure the monitoring stack with Loki is deployed before application stacks, or disable Loki logging driver in stack files to avoid service startup failures.

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

**Data retention**: Prometheus retains 30 days of metrics (configurable via `--storage.tsdb.retention.time=30d` in [../docker/monitoring-stack.yml](../docker/monitoring-stack.yml))

**Persistent volumes:**
- `prometheus-data` - Prometheus time-series database
- `grafana-data` - Grafana dashboards and configuration
- `loki-data` - Loki log storage
- `tempo-data` - Tempo trace storage

**Reload configuration**:
```bash
# Update config files in configs/ directory
# Change CONFIG_VERSION to force config update
export CONFIG_VERSION=$(git rev-parse HEAD)

# Redeploy stack to apply changes
docker stack deploy -c docker/monitoring-stack.yml ssgg-monitoring

# Configs use Docker config objects with versioning:
# - prometheus_yml-${CONFIG_VERSION}
# - loki_config-${CONFIG_VERSION}
# - promtail_config-${CONFIG_VERSION}
# - tempo_config-${CONFIG_VERSION}
# - grafana_datasources-${CONFIG_VERSION}
```

**Backup Grafana dashboards**:
```bash
# Export volume
docker run --rm -v ssgg-monitoring_grafana-data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz /data
```

**Backup Prometheus data**:
```bash
# Export volume (large, may take time)
docker run --rm -v prometheus-data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz /data
```

See [../configs/grafana/provisioning/dashboards/README.md](../configs/grafana/provisioning/dashboards/README.md) for detailed dashboard configuration.

## 7) Troubleshooting

### Common Deployment Issues

**Loki logging driver not found:**
```bash
# Error: "Cannot start service api: failed to initialize logging driver: dial tcp: lookup loki"
# Solution: Deploy monitoring stack first, or disable Loki logging in stack files
# To disable Loki logging temporarily:
docker stack deploy --compose-file <(sed 's/logging: \*default-logging/# logging disabled/' docker/docker-stack.staging.yml) ssgg-be-v2-staging
```

**traefik-public network not found:**
```bash
# Error: "network traefik-public declared as external, but could not be found"
# Solution: Create the network or deploy Traefik stack first
docker network create --driver=overlay traefik-public
# OR
docker stack deploy -c docker/traefik-stack.yml traefik
```

**Service not connecting to MySQL/Redis:**
```bash
# Check service names resolve within stack
docker exec <api-container> ping mysql
docker exec <api-container> ping redis

# Verify environment variables
docker service inspect ssgg-be-v2-staging_api --format='{{json .Spec.TaskTemplate.ContainerSpec.Env}}' | jq

# Check if db_host and rds_host are set to service names (not IPs)
# Should be: db_host=mysql, rds_host=redis
```

**Container fails health check:**
```bash
# View service logs
docker service logs ssgg-be-v2-staging_api -f

# Check health status
docker service ps ssgg-be-v2-staging_api

# Manually test health endpoint
docker exec <container> curl -f http://localhost:8000/health
```

**Image pull authentication failure:**
```bash
# Error: "repository does not exist or may require 'docker login'"
# Ensure GitHub Container Registry authentication is configured
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# OR use Personal Access Token with packages:read scope
echo $GH_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

**Config version update not applied:**
```bash
# Docker configs are immutable once created with a specific version
# Change CONFIG_VERSION to force new config creation
export CONFIG_VERSION=$(date +%s)  # Use timestamp
docker stack deploy -c docker/monitoring-stack.yml ssgg-monitoring

# Remove old configs manually if needed
docker config ls | grep prometheus_yml | awk '{print $1}' | xargs docker config rm
```

**SSL certificate not issued:**
```bash
# Check Traefik logs for ACME challenge errors
docker service logs traefik_traefik -f | grep acme

# Verify DNS points to server
dig api.sportingscout.org

# Check Let's Encrypt rate limits: https://letsencrypt.org/docs/rate-limits/
# Staging certificates: Use acme-staging server for testing
```

### Deployment Order

For a clean deployment, follow this order:
1. **Initialize Swarm**: `docker swarm init`
2. **Create network**: `docker network create --driver=overlay traefik-public`
3. **Deploy Traefik**: `docker stack deploy -c docker/traefik-stack.yml traefik`
4. **Deploy Monitoring**: `docker stack deploy -c docker/monitoring-stack.yml ssgg-monitoring`
5. **Deploy Application**: `docker stack deploy -c docker/docker-stack.{staging|production}.yml ssgg-be-v2-{staging|production}`

## 8) Post-Deploy Verification

- Smoke tests:
	- `GET /health` — status healthy
	- Core routes (Members, Entities, Events) return 200 and expected schema
- RBAC:
	- Validate role/permission enforcement via [../app/api/permissions.py](../app/api/permissions.py) and [../app/api/roles.py](../app/api/roles.py)
- Audit:
	- Confirm audit entries appear for non-excluded paths (see exclusions in middleware)
