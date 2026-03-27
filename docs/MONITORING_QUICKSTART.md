# Monitoring Stack - Quick Start Guide

> **Note**: The monitoring stack is manually deployed by the CI/CD pipeline (`deploy_monitoring.yml` workflow). This guide is for manual deployment or troubleshooting purposes.

This guide will help you deploy the Prometheus, Grafana, and Loki monitoring stack for the SSGG application.

## Prerequisites Checklist

- [ ] Docker Swarm initialized
- [ ] Traefik stack deployed and running
- [ ] Staging stack deployed (`ssgg-staging`)
- [ ] Production stack deployed (`ssgg-production`)  
- [ ] DNS A records configured:
  - [ ] `prometheus.sportingscout.org` → Your server IP
  - [ ] `grafana.sportingscout.org` → Your server IP
  - [ ] `loki.sportingscout.org` → Your server IP

## Step 1: Generate Monitoring Credentials

### Generate Basic Auth for Prometheus

```bash
# On Linux/macOS
htpasswd -nb admin your-prometheus-password

# Example output:
# admin:$apr1$H6uskkkW$IgXLP6ewTrSuBkTrqE8wj/
```

**Important**: When adding to `.env`, double all `$` signs:
```
admin:$apr1$xyz → admin:$$apr1$$xyz
```

### Set Grafana Password

Choose a strong password for Grafana admin account.

## Step 2: Configure Environment Variables

Add these to your environment (`.env` file or swarm secrets):

```bash
# Grafana configuration
GRAFANA_ADMIN_USER=admin
GRAFANA_PASSWORD=your-secure-grafana-password

# Prometheus authentication (remember to double the $ signs)
MONITORING_AUTH=admin:$$apr1$$H6uskkkW$$IgXLP6ewTrSuBkTrqE8wj/
```

## Step 3: Verify Network Setup

Ensure the external networks exist:

```bash
# Check if networks exist
docker network ls | grep -E "stg-internal|prd-internal"

# If networks don't exist, they should be created by the staging/production stacks
# Deploy those stacks first:
docker stack deploy -c docker-stack.staging.yml ssgg-staging
docker stack deploy -c docker-stack.production.yml ssgg-production
```

## Step 4: Deploy Monitoring Stack

**Automated Deployment (Recommended)**:

The monitoring stack is automatically deployed when the CI/CD pipeline runs the `deploy_monitoring.yml` workflow. This workflow:
1. Builds and pushes monitoring service images (Prometheus, Grafana, Loki, Promtail)
2. Deploys the `ssgg-monitoring` stack using `docker-stack-monitoring.yml`

**Manual Deployment** (if needed for troubleshooting or custom setup):

```bash
# Deploy the monitoring stack
docker stack deploy -c docker-stack-monitoring.yml ssgg-monitoring

# Wait for services to start (this may take 1-2 minutes)
watch 'docker stack ps ssgg-monitoring'
```

## Step 5: Verify Deployment

### Check Service Status

```bash
# List all services
docker service ls | grep monitoring

# Expected output:
# ssgg-monitoring_grafana         1/1       grafana/grafana:latest
# ssgg-monitoring_loki            1/1       grafana/loki:2.9.3
# ssgg-monitoring_node-exporter   3/3       prom/node-exporter:latest  (global mode)
# ssgg-monitoring_prometheus      1/1       prom/prometheus:latest
# ssgg-monitoring_promtail        3/3       grafana/promtail:2.9.3     (global mode)
```

### Check Service Logs

```bash
# Prometheus logs
docker service logs ssgg-monitoring_prometheus --tail 50

# Grafana logs
docker service logs ssgg-monitoring_grafana --tail 50

# Loki logs
docker service logs ssgg-monitoring_loki --tail 50

# Promtail logs
docker service logs ssgg-monitoring_promtail --tail 50

# Look for:
# ✓ Prometheus: "Server is ready to receive web requests"
# ✓ Grafana: "HTTP Server Listen"
# ✓ Loki: "Loki started"
# ✓ Promtail: "Seeked /var/lib/docker/containers"
```

### Test Prometheus Targets

```bash
# Check if Prometheus is scraping targets
curl -k -u admin:your-prometheus-password https://prometheus.sportingscout.org/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health, instance: .labels.instance}'

# Expected output should show:
# {
#   "job": "ssgg-be-v2-api-staging",
#   "health": "up",
#   "instance": "tasks.ssgg-staging_api:8000"
# }
# {
#   "job": "ssgg-be-v2-api-production",
#   "health": "up",
#   "instance": "tasks.ssgg-production_api:8000"
# }
```

## Step 6: Access Monitoring Interfaces

### Prometheus

1. Navigate to: https://prometheus.sportingscout.org
2. Login with:
   - Username: `admin`
   - Password: (from htpasswd command)
3. Go to **Status** → **Targets** to verify all targets are UP
4. Try a query: `up` (should show all monitored targets)

### Grafana

1. Navigate to: https://grafana.sportingscout.org
2. Login with:
   - Username: `admin`
   - Password: (from `GRAFANA_PASSWORD`)
3. Verify Prometheus data source:
   - Go to **Configuration** → **Data Sources**
   - Click **Prometheus**
   - Click **Test** button (should show "Data source is working")

## Step 7: Import Dashboards

### Import Pre-built Dashboards

1. In Grafana, click **Dashboards** (four squares icon) → **Import**
2. Import these recommended dashboards:

**Dashboard 1: FastAPI Observability**
- Dashboard ID: `16110`
- Click **Load** → Select **Prometheus** → Click **Import**
- Shows: API metrics, request rates, latencies, errors

**Dashboard 2: Node Exporter Full**
- Dashboard ID: `1860`
- Click **Load** → Select **Prometheus** → Click **Import**
- Shows: System metrics (CPU, RAM, Disk, Network)

**Dashboard 3: Docker Swarm**
- Dashboard ID: `9792`
- Click **Load** → Select **Prometheus** → Click **Import**
- Shows: Container and service metrics

## Step 8: Verify Metrics Collection

### Test API Metrics Endpoint

```bash
# Check staging API metrics
curl http://api.stg.sportingscout.org/metrics | head -20

# Check production API metrics (via any replica)
curl http://api.sportingscout.org/metrics | head -20

# You should see metrics like:
# fastapi_requests_total{...}
# fastapi_responses_total{...}
# fastapi_requests_duration_seconds_bucket{...}
# ssgg_health_overall_up{...}
# ssgg_health_database_up{...}
# ssgg_health_redis_up{...}
# ssgg_health_connection_pool_utilization_percent{...}
```

### Run Sample Queries in Prometheus

Go to Prometheus → **Graph** and try these queries:

```promql
# Check if all API instances are being scraped
up{job=~"ssgg-be-v2-api.*"}

# View database health
ssgg_health_database_up

# View overall application health
ssgg_health_overall_up

# View request rate (production)
rate(fastapi_requests_total{job="ssgg-be-v2-api-production"}[5m])

# View 95th percentile API latency
histogram_quantile(0.95, rate(fastapi_requests_duration_seconds_bucket[5m]))

# Connection pool utilization
ssgg_health_connection_pool_utilization_percent
```

### View Data in Grafana

1. Go to the **FastAPI Observability** dashboard
2. Select time range: **Last 5 minutes**
3. Use the **environment** filter to switch between staging and production
4. Verify you see:
   - Request rates
   - Response times
   - Error rates

## Step 9: Verify Log Collection (Loki)

### Test Loki Datasource

1. In Grafana, go to **Configuration** → **Data Sources**
2. Click **Loki**
3. Click **Test** button (should show "Data source is working")

### Check if Logs are Being Collected

1. In Grafana, go to **Explore** (compass icon)
2. Select **Loki** from the datasource dropdown
3. Try these queries:

```logql
# All logs from production
{environment="production"}

# All logs from staging
{environment="staging"}

# Recent error logs
{environment="production", level="ERROR"}

# Logs from specific service
{service="ssgg-production_api"}
```

### Verify JSON Log Parsing

1. Run this query in Grafana Explore:
```logql
{environment="production"} | json
```

2. Expand a log entry - you should see parsed JSON fields:
   - `timestamp`
   - `level`
   - `message`
   - `module`
   - `request_id` (if from HTTP request)
   - `endpoint` (if from HTTP request)
   - `status_code` (if from HTTP request)

### Test Log Volume

Check if logs are flowing:
```logql
# Count logs per minute
sum(count_over_time({environment="production"}[1m]))
```

You should see non-zero values if logs are being collected.

## Troubleshooting

### Issue: Targets are DOWN in Prometheus

**Check DNS resolution:**
```bash
docker exec $(docker ps -q -f name=prometheus) nslookup tasks.ssgg-staging_api
docker exec $(docker ps -q -f name=prometheus) nslookup tasks.ssgg-production_api
```

**Check network connectivity:**
```bash
# Verify Prometheus can reach API
docker exec $(docker ps -q -f name=prometheus) wget -O- http://tasks.ssgg-staging_api:8000/metrics
```

**Solution**: Ensure Prometheus container is connected to both `stg-internal` and `prd-internal` networks.

### Issue: No metrics showing in Grafana

**Verify Prometheus data source:**
```bash
# Test from Grafana container
docker exec $(docker ps -q -f name=grafana) wget -O- http://prometheus:9090/-/healthy
```

**Check if metrics exist in Prometheus:**
```promql
# In Prometheus, query:
{__name__=~"ssgg.*"}
```

**Solution**: Wait 1-2 minutes for first scrape, then refresh Grafana.

### Issue: Can't access Prometheus/Grafana URLs

**Check Traefik routes:**
```bash
docker service logs traefik_traefik | grep -E "prometheus|grafana"
```

**Verify labels are applied:**
```bash
docker service inspect ssgg-monitoring_prometheus --format='{{json .Spec.Labels}}' | jq
docker service inspect ssgg-monitoring_grafana --format='{{json .Spec.Labels}}' | jq
```

**Check DNS:**
```bash
nslookup prometheus.sportingscout.org
nslookup grafana.sportingscout.org
nslookup loki.sportingscout.org
```

**Solution**: Ensure DNS points to your server and Traefik is running.

### Issue: No logs appearing in Loki/Grafana

**Check if Loki is running:**
```bash
docker service ps ssgg-monitoring_loki
docker service logs ssgg-monitoring_loki --tail 50
```

**Check if Promtail is collecting:**
```bash
docker service logs ssgg-monitoring_promtail --tail 100 | grep -i "scraped\|pushed"
```

**Verify Promtail can reach Loki:**
```bash
docker exec $(docker ps -q -f name=promtail) wget -O- http://loki:3100/ready
```

**Test if logs are in containers:**
```bash
# Check if API containers are producing logs
docker service logs ssgg-production_api --tail 20
```

**Solution**: 
1. Ensure applications are running and producing logs
2. Wait 30-60 seconds for Promtail to scrape and push logs
3. Check Loki is accessible: `curl http://loki:3100/ready`

### Issue: Logs not JSON formatted

**Check application environment:**
```bash
# Verify environment variable
docker service inspect ssgg-production_api --format='{{json .Spec.TaskTemplate.ContainerSpec.Env}}' | jq '.[] | select(contains("environment"))'
```

**Solution**: 
- JSON formatting only enabled for `production`, `prd`, and `staging` environments
- For local development, logs use human-readable format
- Check `app/config/logging_config.py` - CustomJsonFormatter should be active

### Issue: Parsed JSON fields not appearing as labels

**Check Promtail configuration:**
```bash
# Verify promtail-config.yml has json pipeline stage
docker exec $(docker ps -q -f name=promtail) cat /etc/promtail/config.yml | grep -A 5 "json:"
```

**Test label extraction:**
```logql
# In Grafana Explore, check available labels:
{environment="production"}
```

Click on a log line and check if fields like `level`, `module`, `endpoint` appear as labels.

**Solution**: Ensure `promtail-config.yml` has proper JSON parsing pipeline stages.

## Next Steps

1. **Set up alerting**: Configure alert rules in `prometheus-alerts.yml`
2. **Create custom dashboards**: Build dashboards for business metrics
3. **Configure retention**: Adjust retention period based on disk space
4. **Set up backups**: Schedule regular backups of Grafana dashboards and Prometheus data
5. **Review security**: Implement additional authentication if needed

## Useful Commands

```bash
# View all monitoring services
docker stack ps ssgg-monitoring

# Update configuration (reload without downtime)
docker stack deploy -c docker-stack-monitoring.yml ssgg-monitoring

# View real-time logs
docker service logs -f ssgg-monitoring_prometheus
docker service logs -f ssgg-monitoring_grafana
docker service logs -f ssgg-monitoring_loki
docker service logs -f ssgg-monitoring_promtail

# Scale node-exporter (if needed, though it's global)
docker service scale ssgg-monitoring_node-exporter=3

# Remove monitoring stack
docker stack rm ssgg-monitoring

# Restart a specific service
docker service update --force ssgg-monitoring_prometheus
docker service update --force ssgg-monitoring_loki
```

## Support Resources

- **Documentation**: See [MONITORING.md](MONITORING.md) for detailed information
- **Prometheus Docs**: https://prometheus.io/docs/
- **Grafana Docs**: https://grafana.com/docs/
- **Loki Docs**: https://grafana.com/docs/loki/
- **LogQL Reference**: https://grafana.com/docs/loki/latest/logql/
- **Dashboard Gallery**: https://grafana.com/grafana/dashboards/

## Success Checklist

After completing this guide, verify:

- [ ] Prometheus is accessible and shows all targets as UP
- [ ] Grafana is accessible and data sources work (Prometheus + Loki)
- [ ] Loki is accessible and receiving logs
- [ ] At least 2 dashboards are imported and showing data
- [ ] API metrics are being collected (check `/metrics` endpoint)
- [ ] Logs are being collected (check Grafana Explore with Loki)
- [ ] JSON logs are properly parsed (fields appear as labels)
- [ ] Both staging and production environments are monitored
- [ ] Health metrics are visible in Prometheus (`ssgg_health_overall_up`, `ssgg_health_database_up`, `ssgg_health_redis_up`)
- [ ] Health background loop is running (check `ssgg_health_check_duration_ms` updates every ~30s)
- [ ] Connection pool metrics visible (`ssgg_health_connection_pool_utilization_percent`)
- [ ] System metrics are visible (CPU, memory, disk from node-exporter)
- [ ] Environment labels are working (can filter by staging/production)
- [ ] Log queries work (`{environment="production"}` returns results)

Congratulations! Your complete monitoring stack (metrics + logs) is now operational. 🎉
