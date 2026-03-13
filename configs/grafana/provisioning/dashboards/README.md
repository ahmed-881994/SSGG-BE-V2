# Grafana Dashboards

This directory contains Grafana dashboard configurations for the SSGG application.

## Pre-built Dashboards

You can import the following community dashboards directly in Grafana:

### FastAPI Application Metrics
- **Dashboard ID**: 16110
- **Name**: FastAPI Observability
- **Description**: Comprehensive FastAPI application monitoring
- **How to import**: 
  1. Go to Grafana → Dashboards → Import
  2. Enter dashboard ID: `16110`
  3. Select "Prometheus" as the data source
  4. Click "Import"

### System Metrics (Node Exporter)
- **Dashboard ID**: 1860
- **Name**: Node Exporter Full
- **Description**: Complete system monitoring dashboard
- **How to import**: 
  1. Go to Grafana → Dashboards → Import
  2. Enter dashboard ID: `1860`
  3. Select "Prometheus" as the data source
  4. Click "Import"

### Docker Swarm Monitoring
- **Dashboard ID**: 9792
- **Name**: Docker Swarm Dashboard
- **Description**: Monitor Docker Swarm cluster metrics
- **How to import**: 
  1. Go to Grafana → Dashboards → Import
  2. Enter dashboard ID: `9792`
  3. Select "Prometheus" as the data source
  4. Click "Import"

## Custom Dashboard Configuration

To add custom dashboards:

1. Create a JSON file in this directory (e.g., `ssgg-custom.json`)
2. The dashboard will be automatically loaded on Grafana startup
3. Changes to the JSON file will be reflected after ~10 seconds

## Key Metrics to Monitor

### API Performance Metrics
- `http_requests_total` - Total HTTP requests by method and endpoint
- `http_request_duration_seconds` - Request duration percentiles
- `ssgg_db_health_status` - Database health (1=healthy, 0=unhealthy)
- `ssgg_redis_health_status` - Redis health (1=healthy, 0=unhealthy)

### Database Metrics
- `ssgg_db_connection_pool_size` - Total connection pool size
- `ssgg_db_active_connections` - Currently active connections
- `ssgg_db_response_time_ms` - Database query response time

### Redis Metrics
- `ssgg_redis_response_time_ms` - Redis operation response time
- `ssgg_redis_operations_total` - Total Redis operations by type

### System Metrics (Node Exporter)
- `node_cpu_seconds_total` - CPU usage
- `node_memory_MemAvailable_bytes` - Available memory
- `node_disk_io_time_seconds_total` - Disk I/O
- `node_network_receive_bytes_total` - Network traffic

## Environment Labels

All API metrics are tagged with `environment` label:
- `environment="production"` - Production API (5 replicas)
- `environment="staging"` - Staging API (1 replica)

Use these labels in your queries to filter by environment:
```promql
# Production API request rate
rate(http_requests_total{environment="production"}[5m])

# Staging database health
ssgg_db_health_status{environment="staging"}
```
