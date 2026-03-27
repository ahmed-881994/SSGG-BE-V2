# SSGG Monitoring Setup

This directory contains the monitoring and observability stack configuration for the SSGG backend application.

## Overview

The monitoring stack provides comprehensive observability for both **staging** and **production** environments using:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Unified visualization for metrics and logs
- **Loki**: Log aggregation and indexing
- **Promtail**: Log collection from Docker containers
- **Node Exporter**: System-level metrics collection

## Stack Components

| Component | Purpose | Data Type | Access |
|-----------|---------|-----------|--------|
| **Prometheus** | Time-series metrics | Numbers, rates, histograms | https://prometheus.sportingscout.org |
| **Grafana** | Visualization & dashboards | Both metrics and logs | https://grafana.sportingscout.org |
| **Loki** | Log aggregation | Structured & unstructured logs | https://loki.sportingscout.org |
| **Promtail** | Log collection | Container log shipping | (Internal) |
| **Node Exporter** | System metrics | CPU, RAM, disk, network | (Internal) |

## Quick Start

### 1. Prerequisites

Ensure you have:
- Docker Swarm initialized
- Traefik deployed and running
- Both staging and production stacks deployed
- DNS records configured:
  - `prometheus.sportingscout.org`
  - `grafana.sportingscout.org`
  - `loki.sportingscout.org`

### 2. Configure Environment Variables

Add to your environment configuration:

```bash
# Generate basic auth credentials for Prometheus
htpasswd -nb admin yourpassword

# Add to .env or deployment environment
MONITORING_AUTH=admin:$$apr1$$H6uskkkW$$IgXLP6ewTrSuBkTrqE8wj/
GRAFANA_PASSWORD=your-secure-grafana-password
GRAFANA_ADMIN_USER=admin
```

### 3. Deploy Monitoring Stack

```bash
# Deploy the monitoring stack
docker stack deploy -c docker-stack-monitoring.yml ssgg-monitoring

# Verify services are running
docker stack ps ssgg-monitoring

# Check service logs
docker service logs sssg-monitoring_prometheus -f
docker service logs ssgg-monitoring_grafana -f
```

### 4. Access Monitoring

- **Prometheus**: https://prometheus.sportingscout.org
  - Username: `admin`
  - Password: From `MONITORING_AUTH`

- **Grafana**: https://grafana.sportingscout.org
  - Username: `admin`
  - Password: From `GRAFANA_PASSWORD`

- **Loki**: https://loki.sportingscout.org
  - Username: `admin`
  - Password: From `MONITORING_AUTH`
  - (Usually accessed via Grafana, direct API access available)

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Traefik                               │
│                (Reverse Proxy + SSL)                         │
└────┬─────────────┬─────────────┬────────────────────────────┘
     │             │             │
     │             │             │
┌────▼──────┐ ┌───▼──────┐ ┌───▼──────┐
│Prometheus │ │ Grafana  │ │   Loki   │
│ (Metrics) │ │  (Viz)   │ │  (Logs)  │
└────┬──────┘ └────┬─────┘ └────┬─────┘
     │             │              │
     │             └──────┬───────┘
     │                    │
┌────▼────────────────────▼──────────────────┐
│           Collection Layer                 │
├────────────────────────────────────────────┤
│  • API Metrics (/metrics endpoint)        │
│  • Node Exporter (system metrics)         │
│  • Promtail (container log shipper)       │
└────────────────────────────────────────────┘
     │
┌────▼────────────────────────────────────────┐
│           Application Services              │
├────────────────────────────────────────────┤
│  • Staging API (1 replica)                 │
│  • Production API (5 replicas)             │
│  • MySQL (staging + production)            │
│  • Redis (staging + production)            │
└────────────────────────────────────────────┘
```

### Network Configuration

The monitoring stack connects to three networks:
- `traefik-public`: For external access via Traefik
- `stg-internal`: To scrape/collect from staging environment
- `prd-internal`: To scrape/collect from production environment

This allows a single monitoring instance to observe both environments while maintaining network isolation between staging and production.

## Data Collection Flow

### Metrics Flow (Prometheus)
1. **API Services** expose `/metrics` endpoint (protected to internal networks only) with Prometheus-formatted metrics
2. A **background health loop** runs every 30 seconds inside the application, calls the full health check, and updates health Gauges — completely off the request hot-path
3. **Prometheus** scrapes `/metrics` every 15 seconds via DNS service discovery
4. **Grafana** queries Prometheus for visualization

### Logs Flow (Loki)
1. **Docker containers** write logs to stdout/stderr
2. **Promtail** (running on each node) collects logs from `/var/lib/docker/containers`
3. **Promtail** parses JSON-formatted logs and adds labels
4. **Loki** receives and indexes logs by labels (not full-text)
5. **Grafana** queries Loki for log exploration and dashboards

## Metrics Collected

### Application Metrics (FastAPI)

Instrumented via a custom `MetricsMiddleware` (`app/core/metrics_middleware.py`). Labels on all HTTP metrics include `method`, `path`, and `app_name`:

- `fastapi_app_info`: Application metadata gauge (app name, version)
- `fastapi_requests_total`: Total request count by method and path
- `fastapi_responses_total`: Total response count by method, path, and status code
- `fastapi_requests_duration_seconds`: Request latency histogram by method and path
- `fastapi_exceptions_total`: Exception count by path and exception type
- `fastapi_requests_in_progress`: Current in-flight request count by method and path

### Health Metrics

Exposed via a background loop (`app/core/health_metrics.py`) that runs every 30 seconds and maps the full health report to Prometheus Gauges. Status values are normalised: `1.0` = healthy, `0.5` = warning, `0.0` = unhealthy.

- **Overall**:
  - `ssgg_health_overall_up`: Overall application health status
  - `ssgg_health_check_duration_ms`: Duration of the last full health check run
  - `ssgg_health_services_healthy_total`: Count of services in healthy state
  - `ssgg_health_services_warning_total`: Count of services in warning state
  - `ssgg_health_services_unhealthy_total`: Count of services in unhealthy state

- **Database Connectivity**:
  - `ssgg_health_database_up`: DB connectivity status
  - `ssgg_health_database_response_time_ms`: Test query response time

- **Connection Pool**:
  - `ssgg_health_connection_pool_up`: Pool health status
  - `ssgg_health_connection_pool_size`: Configured maximum pool size
  - `ssgg_health_connection_pool_active_connections`: Currently checked-out connections
  - `ssgg_health_connection_pool_available_connections`: Idle connections available
  - `ssgg_health_connection_pool_overflow_connections`: Open overflow connections
  - `ssgg_health_connection_pool_utilization_percent`: Pool utilization percentage
  - `ssgg_health_connection_pool_response_time_ms`: Pool inspection response time

- **Database Schema**:
  - `ssgg_health_db_schema_up`: Schema health status
  - `ssgg_health_db_schema_required_tables_total`: Number of required tables
  - `ssgg_health_db_schema_existing_tables_total`: Number of tables present in the DB
  - `ssgg_health_db_schema_missing_tables_total`: Number of required tables that are missing
  - `ssgg_health_db_schema_response_time_ms`: Schema inspection response time

- **Environment Configuration**:
  - `ssgg_health_environment_up`: Environment config health status
  - `ssgg_health_environment_response_time_ms`: Config check response time

- **Redis**:
  - `ssgg_health_redis_up`: Redis connectivity status
  - `ssgg_health_redis_response_time_ms`: Redis check response time
  - `ssgg_health_redis_connected_clients`: Connected Redis clients
  - `ssgg_health_redis_keyspace_hits_total`: Cumulative keyspace hits (snapshot)
  - `ssgg_health_redis_keyspace_misses_total`: Cumulative keyspace misses (snapshot)

### System Metrics (Node Exporter)

- CPU usage per core
- Memory (total, available, used)
- Disk I/O and space utilization
- Network traffic (bytes sent/received)
- System load averages

## Logs Collected

### Application Logs (Loki)

The application outputs JSON-formatted logs that are automatically collected by Promtail and indexed in Loki:

**Log Fields**:
- `timestamp`: Log timestamp (Unix epoch)
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `logger`: Logger name
- `module`: Python module name
- `function`: Function name
- `line`: Line number in code
- `message`: Log message
- `environment`: Environment (staging/production)
- `app`: Application name (ssgg-api)
- `version`: Application version
- `pid`: Process ID
- `thread`: Thread ID

**Request Context** (when available):
- `request_id`: Unique request identifier
- `user_id`: Authenticated user ID
- `method`: HTTP method
- `url`: Request URL
- `endpoint`: API endpoint
- `status_code`: HTTP response status
- `process_time`: Request processing time (ms)
- `duration`: Alias for process_time
- `client_ip`: Client IP address

**Container Labels** (added by Promtail):
- `container`: Container name
- `container_id`: Short container ID
- `image`: Docker image name
- `stack`: Docker stack name (ssgg-production, ssgg-staging)
- `service`: Swarm service name
- `task_id`: Swarm task ID
- `node_id`: Swarm node ID
- `environment`: Derived from stack name

### Log Retention

- **Retention Period**: 30 days (configurable in `loki-config.yml`)
- **Automatic Compaction**: Runs every 10 minutes
- **Storage**: Filesystem-based (using BoltDB)

## Environment Labeling

HTTP metrics (`fastapi_*`) include the `app_name` label set from the `app_name` setting, allowing filtering per deployment.

Health Gauges (`ssgg_health_*`) are **instance-scoped** — each API replica exposes its own values. Use the Prometheus `instance` or `job` label to differentiate environments:

```promql
# Production API request rate (by job)
rate(fastapi_requests_total{job="ssgg-be-v2-api-production"}[5m])

# Staging database health
ssgg_health_database_up{job="ssgg-be-v2-api-staging"}

# Any unhealthy service across all environments
ssgg_health_overall_up < 1
```

## Grafana Dashboards

### Recommended Community Dashboards

Import these pre-built dashboards for comprehensive monitoring:

1. **FastAPI Observability** - Dashboard ID: `16110`
   - Request rates and error rates
   - Latency percentiles (p50, p95, p99)
   - Endpoint-level metrics

2. **Node Exporter Full** - Dashboard ID: `1860`
   - System resources (CPU, RAM, Disk, Network)
   - Per-node breakdown
   - Historical trends

3. **Docker Swarm** - Dashboard ID: `9792`
   - Service health and replica status
   - Container resource usage
   - Swarm cluster overview

### Import Instructions

1. Login to Grafana (https://grafana.sportingscout.org)
2. Navigate to **Dashboards** → **Import**
3. Enter the dashboard ID (e.g., `16110`)
4. Select **Prometheus** as the data source
5. Click **Import**

### Custom Dashboards

Place custom dashboard JSON files in:
```
grafana/provisioning/dashboards/
```

They will be automatically loaded on Grafana startup.

## Sample Queries

### API Performance

```promql
# Requests per second (production)
rate(fastapi_requests_total{job="ssgg-be-v2-api-production"}[5m])

# 95th percentile response time
histogram_quantile(0.95,
  rate(fastapi_requests_duration_seconds_bucket{job="ssgg-be-v2-api-production"}[5m])
)

# Error rate percentage (5xx responses)
rate(fastapi_responses_total{job="ssgg-be-v2-api-production", status_code=~"5.."}[5m]) /
rate(fastapi_requests_total{job="ssgg-be-v2-api-production"}[5m]) * 100

# Top 10 slowest endpoints
topk(10,
  histogram_quantile(0.95,
    rate(fastapi_requests_duration_seconds_bucket{job="ssgg-be-v2-api-production"}[5m])
  ) by (path)
)

# Current in-flight requests
sum(fastapi_requests_in_progress{job="ssgg-be-v2-api-production"}) by (path)

# Exception count by type
rate(fastapi_exceptions_total{job="ssgg-be-v2-api-production"}[5m])
```

### Database Health

```promql
# Database connectivity status (1=healthy, 0.5=warning, 0=unhealthy)
ssgg_health_database_up

# Database test query response time
ssgg_health_database_response_time_ms

# Connection pool utilization percentage
ssgg_health_connection_pool_utilization_percent

# Active vs available connections
ssgg_health_connection_pool_active_connections
ssgg_health_connection_pool_available_connections

# Schema drift — should always be 0
ssgg_health_db_schema_missing_tables_total

# Alert if any replica has unhealthy DB
ssgg_health_database_up == 0
```

### Redis Monitoring

```promql
# Redis health status (1=healthy, 0=unhealthy)
ssgg_health_redis_up

# Redis check response time
ssgg_health_redis_response_time_ms

# Connected clients
ssgg_health_redis_connected_clients

# Cache hit rate
ssgg_health_redis_keyspace_hits_total /
  (ssgg_health_redis_keyspace_hits_total + ssgg_health_redis_keyspace_misses_total)
```

### Overall Application Health

```promql
# Overall health (1=healthy, 0.5=warning, 0=unhealthy)
ssgg_health_overall_up

# Count of unhealthy services (alert threshold: > 0)
ssgg_health_services_unhealthy_total

# Full health check duration trend
ssgg_health_check_duration_ms
```

### System Resources

```promql
# CPU usage percentage
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage percentage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk space usage
(node_filesystem_size_bytes - node_filesystem_free_bytes) /
node_filesystem_size_bytes * 100

# Network throughput (MB/s)
rate(node_network_receive_bytes_total[5m]) / 1024 / 1024
```

### Environment Comparison

```promql
# Compare DB response time across environments
ssgg_health_database_response_time_ms

# Request rate comparison by job
sum(rate(fastapi_requests_total[5m])) by (job)

# Error rate comparison by job
sum(rate(fastapi_responses_total{status_code=~"5.."}[5m])) by (job)
```

## Sample Log Queries (LogQL)

Loki uses LogQL, a query language similar to PromQL but for logs. Access via Grafana → Explore → Loki datasource.

### Basic Queries

```logql
# All logs from production API
{environment="production", service="ssgg-production_api"}

# All logs from staging
{environment="staging"}

# Logs from specific container
{container="ssgg-production_api.1.abc123"}

# Logs from all monitoring services
{stack="ssgg-monitoring"}
```

### Filtering by Log Level

```logql
# Error logs only (production)
{environment="production"} | json | level="ERROR"

# Warning and above
{environment="production"} | json | level=~"WARNING|ERROR|CRITICAL"

# Info logs from specific module
{environment="production"} | json | level="INFO" | module="auth_service"
```

### Request-Specific Queries

```logql
# Logs for specific endpoint
{environment="production"} | json | endpoint="/api/members"

# Slow requests (>1000ms)
{environment="production"} | json | process_time > 1000

# Failed requests (5xx errors)
{environment="production"} | json | status_code=~"5.."

# Authentication errors
{environment="production"} | json | message=~"(?i)authentication|unauthorized|forbidden"
```

### User Activity

```logql
# Logs for specific user
{environment="production"} | json | user_id="123"

# All user authentication attempts
{environment="production"} | json | module="auth_service"

# Failed login attempts
{environment="production"} | json | level="WARNING" | message=~"(?i)login.*failed|invalid.*credentials"
```

### Database Queries

```logql
# Database errors
{environment="production"} | json | level="ERROR" | message=~"(?i)database|connection|query"

# Long-running database queries
{environment="production"} | json | message=~"(?i)query" | duration > 500

# Connection pool warnings
{environment="production"} | json | message=~"(?i)connection.*pool"
```

### Aggregations and Metrics from Logs

```logql
# Count errors per minute
sum(count_over_time({environment="production", level="ERROR"}[1m])) by (service)

# Rate of 5xx errors
rate({environment="production"} | json | status_code=~"5.." [5m])

# Average request duration
avg_over_time({environment="production"} | json | unwrap process_time [5m]) by (endpoint)

# Top 10 slowest endpoints
topk(10, 
  avg_over_time({environment="production"} | json | unwrap process_time [1h]) by (endpoint)
)
```

### Request Tracing

```logql
# Find all logs for a specific request ID
{environment="production"} | json | request_id="abc-123-def"

# Trace request through multiple services
{environment="production"} | json | request_id="abc-123-def" | line_format "{{.timestamp}} [{{.level}}] {{.service}} - {{.message}}"
```

### Comparison Queries

```logql
# Compare error rates across environments
sum(rate({environment=~"staging|production", level="ERROR"}[5m])) by (environment)

# Compare log volume
sum(rate({stack=~"ssgg-staging|ssgg-production"}[1m])) by (stack)
```

### Pattern Matching

```logql
# Find specific error patterns
{environment="production"} | json | message=~".*timeout.*" or message=~".*connection refused.*"

# Extract and count specific patterns
{environment="production"} 
  | json 
  | message |~ "User .* logged in" 
  | regexp `User (?P<username>\\w+) logged in`
  | line_format "{{.username}}"
```

## Log Dashboard Examples

Create Grafana dashboard panels using these queries:

### 1. Log Volume Over Time
```logql
sum(count_over_time({environment="production"}[1m])) by (level)
```
**Panel Type**: Time series  
**Legend**: `{{level}}`

### 2. Error Rate
```logql
sum(rate({environment="production", level="ERROR"}[5m]))
```
**Panel Type**: Stat  
**Thresholds**: < 1 (green), < 5 (yellow), >= 5 (red)

### 3. Recent Errors Table
```logql
{environment="production", level="ERROR"} | json
```
**Panel Type**: Logs  
**Max Lines**: 50

### 4. Slowest Endpoints
```logql
topk(10, avg_over_time({environment="production"} | json | unwrap process_time [1h]) by (endpoint))
```
**Panel Type**: Bar chart

### 5. Failed Authentication Attempts
```logql
sum(count_over_time({environment="production"} | json | level="WARNING" | message=~"(?i)authentication.*failed" [5m]))
```
**Panel Type**: Time series

## Alerts from Logs

Configure alert rules in Grafana using log queries:

### High Error Rate Alert
```yaml
- alert: HighErrorRateInLogs
  expr: |
    sum(rate({environment="production", level="ERROR"}[5m])) > 5
  for: 5m
  annotations:
    summary: "High error rate detected in production logs"
    description: "Error rate is {{ $value }} errors/sec"
```

### Database Connection Failures
```yaml
- alert: DatabaseConnectionErrors
  expr: |
    sum(count_over_time({environment="production"} 
      | json 
      | level="ERROR" 
      | message=~"(?i)database.*connection" [5m])) > 10
  for: 2m
  annotations:
    summary: "Database connection errors detected"
```

### Authentication Failures Spike
```yaml
- alert: AuthenticationFailuresSpike
  expr: |
    sum(rate({environment="production"} 
      | json 
      | message=~"(?i)authentication.*failed" [5m])) > 0.5
  for: 3m
  annotations:
    summary: "Unusual authentication failure rate"
    description: "May indicate brute force attack"
```

## Alerting

### Setup Alert Rules

Create `prometheus-alerts.yml`:

```yaml
groups:
  - name: ssgg_critical
    interval: 30s
    rules:
      - alert: APIHighErrorRate
        expr: |
          rate(fastapi_responses_total{status_code=~"5.."}[5m]) /
          rate(fastapi_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "API error rate above 5% on {{ $labels.job }}"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: DatabaseDown
        expr: ssgg_health_database_up == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database is unhealthy on {{ $labels.instance }}"

      - alert: RedisDown
        expr: ssgg_health_redis_up == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Redis is unhealthy on {{ $labels.instance }}"

      - alert: SchemaDrift
        expr: ssgg_health_db_schema_missing_tables_total > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Required database tables are missing on {{ $labels.instance }}"
          description: "{{ $value }} required table(s) missing from the database"

      - alert: AnyServiceUnhealthy
        expr: ssgg_health_services_unhealthy_total > 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "{{ $value }} service(s) unhealthy on {{ $labels.instance }}"

  - name: ssgg_warnings
    interval: 1m
    rules:
      - alert: HighDatabaseLatency
        expr: ssgg_health_database_response_time_ms > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database latency on {{ $labels.instance }}"
          description: "DB response time is {{ $value }}ms"

      - alert: HighConnectionPoolUsage
        expr: ssgg_health_connection_pool_utilization_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Connection pool usage above 80% on {{ $labels.instance }}"
          description: "Pool utilization is {{ $value }}%"

      - alert: HighMemoryUsage
        expr: |
          (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 0.85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Memory usage above 85% on {{ $labels.instance }}"
```

Update `prometheus.yml`:
```yaml
rule_files:
  - 'prometheus-alerts.yml'
```

## Troubleshooting

### Prometheus Not Scraping Targets

Check target status:
```bash
# Via API
curl -u admin:password https://prometheus.sportingscout.org/api/v1/targets

# View in UI
# Go to Status → Targets
```

Common issues:
- DNS resolution: Ensure Docker Swarm DNS is working (`tasks.ssgg-staging_api`)
- Network connectivity: Verify Prometheus can reach internal networks
- Firewall rules: Check port 8000 is accessible on API containers

### Metrics Not Appearing

1. Check if `/metrics` endpoint is exposed:
   ```bash
   curl http://api.stg.sportingscout.org/metrics
   ```

2. Verify Prometheus is scraping:
   ```promql
   up{job="ssgg-api-staging"}
   ```

3. Check Prometheus logs:
   ```bash
   docker service logs ssgg-monitoring_prometheus | grep error
   ```

### Grafana Data Source Issues

1. Test Prometheus connection in Grafana:
   - Go to Configuration → Data Sources → Prometheus
   - Click "Test" button

2. Verify Prometheus is reachable from Grafana:
   ```bash
   docker exec $(docker ps -q -f name=ssgg-monitoring_grafana) wget -O- http://prometheus:9090/-/healthy
   ```

### Loki Not Receiving Logs

1. Check if Loki is running:
   ```bash
   docker service ps ssgg-monitoring_loki
   docker service logs ssgg-monitoring_loki --tail 50
   ```

2. Verify Promtail is scraping containers:
   ```bash
   docker service logs ssgg-monitoring_promtail --tail 100 | grep -i "error\|warn"
   ```

3. Check if Promtail can reach Loki:
   ```bash
   docker exec $(docker ps -q -f name=promtail) wget -O- http://loki:3100/ready
   ```

4. Test Loki ingestion:
   ```bash
   # Send a test log
   curl -X POST http://loki:3100/loki/api/v1/push \
     -H "Content-Type: application/json" \
     -d '{"streams":[{"stream":{"test":"log"},"values":[["'"$(date +%s)"'000000000","test message"]]}]}'
   ```

5. Query Loki for recent logs:
   ```bash
   curl -G -s "http://loki:3100/loki/api/v1/query_range" \
     --data-urlencode 'query={environment="production"}' \
     --data-urlencode 'limit=10' | jq
   ```

### Promtail Not Collecting Logs

1. Verify Promtail can access Docker socket:
   ```bash
   docker exec $(docker ps -q -f name=promtail) ls -l /var/run/docker.sock
   ```

2. Check Promtail targets:
   ```bash
   # Promtail exposes metrics at :9080/targets
   docker exec $(docker ps -q -f name=promtail) wget -O- http://localhost:9080/targets
   ```

3. Verify container logs are accessible:
   ```bash
   docker exec $(docker ps -q -f name=promtail) ls -l /var/lib/docker/containers
   ```

4. Check Promtail positions file:
   ```bash
   docker exec $(docker ps -q -f name=promtail) cat /tmp/positions.yaml
   ```

### Logs Not Appearing in Grafana

1. Test Loki datasource in Grafana:
   - Go to Configuration → Data Sources → Loki
   - Click "Test" button (should show "Data source is working")

2. Verify Loki has data:
   ```logql
   # In Grafana Explore, try:
   {job="docker"}
   ```

3. Check label filters:
   - Ensure labels match your query
   - Try broad query first: `{environment="production"}`
   - Then narrow down: `{environment="production", service="ssgg-production_api"}`

4. Check time range:
   - Loki indexes logs by time
   - Ensure selected time range includes log data
   - Try "Last 5 minutes" first

### JSON Logs Not Parsing

1. Verify logs are JSON format:
   ```bash
   docker service logs ssgg-production_api --tail 5 --no-trunc
   ```

2. Test JSON parsing in Loki:
   ```logql
   {environment="production"} | json | level="ERROR"
   ```

3. Check logging configuration in application:
   - Ensure `logging_config.py` is using `CustomJsonFormatter` 
   - Verify environment is 'production' or 'staging'
   - For local dev, JSON formatting is disabled

### Performance Issues

If Prometheus consumes too much memory:

1. Reduce retention time in `docker-stack-monitoring.yml`:
   ```yaml
   - '--storage.tsdb.retention.time=15d'  # Reduce from 30d
   ```

2. Increase scrape interval in `prometheus.yml`:
   ```yaml
   global:
     scrape_interval: 30s  # Increase from 15s
   ```

3. Add resource limits:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 2G
       reservations:
         memory: 1G
   ```

## Maintenance

### Backup Configuration

```bash
# Backup Prometheus data
docker run --rm \
  -v ssgg-monitoring_prometheus-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/prometheus-backup.tar.gz /data

# Backup Grafana data
docker run --rm \
  -v ssgg-monitoring_grafana-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/grafana-backup.tar.gz /data

# Backup Loki data
docker run --rm \
  -v ssgg-monitoring_loki-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/loki-backup.tar.gz /data
```

### Update Monitoring Stack

```bash
# Update configuration
vim prometheus.yml

# Reload Prometheus (no downtime)
curl -X POST https://prometheus.sportingscout.org/-/reload

# Or redeploy stack
docker stack deploy -c docker-stack-monitoring.yml ssgg-monitoring
```

### Clean Up

```bash
# Remove monitoring stack
docker stack rm ssgg-monitoring

# Remove volumes (WARNING: deletes all metrics and logs history)
docker volume rm ssgg-monitoring_prometheus-data
docker volume rm ssgg-monitoring_grafana-data
docker volume rm ssgg-monitoring_loki-data
```

## Security Considerations

1. **Basic Auth**: Prometheus is protected by basic authentication via Traefik
2. **Network Isolation**: Monitoring stack has read-only access to application networks
3. **Grafana Auth**: Change default admin password immediately
4. **Metrics Endpoint**: Consider restricting `/metrics` to internal networks only
5. **Sensitive Data**: Metrics do not include PII or sensitive user data

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)
- [Grafana Dashboard Repository](https://grafana.com/grafana/dashboards/)

## Support

For issues or questions:
1. Check service logs: `docker service logs ssgg-monitoring_<service> -f`
2. Review Prometheus targets: https://prometheus.sportingscout.org/targets
3. Verify network connectivity between services
4. Consult the troubleshooting section above
