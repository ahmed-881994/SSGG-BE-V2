from prometheus_client import Gauge

# ---------- Overall ----------
HEALTH_OVERALL_UP = Gauge(
    "ssgg_health_overall_up",
    "Overall application health (1=healthy, 0.5=warning, 0=unhealthy)",
    ["environment", "version"],
)
HEALTH_CHECK_DURATION_MS = Gauge(
    "ssgg_health_check_duration_ms",
    "Duration of the last full health check run in milliseconds",
    ["environment", "version"],
)
HEALTH_SERVICES_HEALTHY = Gauge(
    "ssgg_health_services_healthy_total",
    "Number of services currently in a healthy state",
    ["environment", "version"],
)
HEALTH_SERVICES_WARNING = Gauge(
    "ssgg_health_services_warning_total",
    "Number of services currently in a warning state",
    ["environment", "version"],
)
HEALTH_SERVICES_UNHEALTHY = Gauge(
    "ssgg_health_services_unhealthy_total",
    "Number of services currently in an unhealthy state",
    ["environment", "version"],
)

# ---------- Database connectivity ----------
HEALTH_DB_UP = Gauge(
    "ssgg_health_database_up",
    "Database connectivity status (1=healthy, 0.5=warning, 0=unhealthy)",
    ["environment", "version"],
)
HEALTH_DB_RESPONSE_MS = Gauge(
    "ssgg_health_database_response_time_ms",
    "Database test query response time in milliseconds",
    ["environment", "version"],
)

# ---------- Connection pool ----------
HEALTH_POOL_UP = Gauge(
    "ssgg_health_connection_pool_up",
    "Connection pool status (1=healthy, 0.5=warning, 0=unhealthy)",
    ["environment", "version"],
)
HEALTH_POOL_SIZE = Gauge(
    "ssgg_health_connection_pool_size",
    "Configured maximum size of the database connection pool",
    ["environment", "version"],
)
HEALTH_POOL_ACTIVE = Gauge(
    "ssgg_health_connection_pool_active_connections",
    "Number of currently checked-out (active) database connections",
    ["environment", "version"],
)
HEALTH_POOL_AVAILABLE = Gauge(
    "ssgg_health_connection_pool_available_connections",
    "Number of idle connections available in the pool",
    ["environment", "version"],
)
HEALTH_POOL_OVERFLOW = Gauge(
    "ssgg_health_connection_pool_overflow_connections",
    "Number of open overflow connections beyond the pool limit",
    ["environment", "version"],
)
HEALTH_POOL_UTILIZATION = Gauge(
    "ssgg_health_connection_pool_utilization_percent",
    "Percentage of the connection pool currently in use",
    ["environment", "version"],
)
HEALTH_POOL_RESPONSE_MS = Gauge(
    "ssgg_health_connection_pool_response_time_ms",
    "Connection pool inspection response time in milliseconds",
    ["environment", "version"],
)

# ---------- Database schema ----------
HEALTH_SCHEMA_UP = Gauge(
    "ssgg_health_db_schema_up",
    "Database schema health status (1=healthy, 0=unhealthy)",
    ["environment", "version"],
)
HEALTH_SCHEMA_REQUIRED_TABLES = Gauge(
    "ssgg_health_db_schema_required_tables_total",
    "Total number of required database tables",
    ["environment", "version"],
)
HEALTH_SCHEMA_EXISTING_TABLES = Gauge(
    "ssgg_health_db_schema_existing_tables_total",
    "Total number of tables currently present in the database",
    ["environment", "version"],
)
HEALTH_SCHEMA_MISSING_TABLES = Gauge(
    "ssgg_health_db_schema_missing_tables_total",
    "Number of required tables missing from the database",
    ["environment", "version"],
)
HEALTH_SCHEMA_RESPONSE_MS = Gauge(
    "ssgg_health_db_schema_response_time_ms",
    "Database schema inspection response time in milliseconds",
    ["environment", "version"],
)

# ---------- Environment ----------
HEALTH_ENV_UP = Gauge(
    "ssgg_health_environment_up",
    "Environment configuration health status (1=healthy, 0=unhealthy)",
    ["environment", "version"],
)
HEALTH_ENV_RESPONSE_MS = Gauge(
    "ssgg_health_environment_response_time_ms",
    "Environment configuration check response time in milliseconds",
    ["environment", "version"],
)

# ---------- Redis ----------
HEALTH_REDIS_UP = Gauge(
    "ssgg_health_redis_up",
    "Redis connectivity status (1=healthy, 0.5=warning, 0=unhealthy)",
    ["environment", "version"],
)
HEALTH_REDIS_RESPONSE_MS = Gauge(
    "ssgg_health_redis_response_time_ms",
    "Redis connectivity check response time in milliseconds",
    ["environment", "version"],
)
HEALTH_REDIS_CONNECTED_CLIENTS = Gauge(
    "ssgg_health_redis_connected_clients",
    "Number of clients currently connected to Redis",
    ["environment", "version"],
)
HEALTH_REDIS_KEYSPACE_HITS = Gauge(
    "ssgg_health_redis_keyspace_hits_total",
    "Cumulative Redis keyspace hits (snapshot at last check)",
    ["environment", "version"],
)
HEALTH_REDIS_KEYSPACE_MISSES = Gauge(
    "ssgg_health_redis_keyspace_misses_total",
    "Cumulative Redis keyspace misses (snapshot at last check)",
    ["environment", "version"],
)

_STATUS_VALUE = {"healthy": 1.0, "warning": 0.5, "unhealthy": 0.0}


def _status(value: str) -> float:
    return _STATUS_VALUE.get(value, 0.0)


def update_health_metrics(report: dict) -> None:
    """Push every field from the full check_health() report into Prometheus Gauges."""

    environment = report.get("environment", "unknown")
    version = report.get("version", "unknown")

    # Bind label values once and reuse metric handles for every update.
    labeled = lambda metric: metric.labels(environment=environment, version=version)

    # Overall
    labeled(HEALTH_OVERALL_UP).set(_status(report.get("status", "unhealthy")))
    labeled(HEALTH_CHECK_DURATION_MS).set(report.get("response_time_ms", 0))
    summary = report.get("summary", {})
    labeled(HEALTH_SERVICES_HEALTHY).set(summary.get("healthy_services", 0))
    labeled(HEALTH_SERVICES_WARNING).set(summary.get("warning_services", 0))
    labeled(HEALTH_SERVICES_UNHEALTHY).set(summary.get("unhealthy_services", 0))

    services = report.get("services", {})

    # Database connectivity
    db = services.get("database_connectivity", {})
    if db:
        labeled(HEALTH_DB_UP).set(_status(db.get("status", "unhealthy")))
        labeled(HEALTH_DB_RESPONSE_MS).set(db.get("performance", {}).get("response_time_ms", 0))

    # Connection pool
    pool = services.get("connection_pool", {})
    if pool:
        labeled(HEALTH_POOL_UP).set(_status(pool.get("status", "unhealthy")))
        labeled(HEALTH_POOL_RESPONSE_MS).set(pool.get("response_time_ms", 0))
        pool_cfg = pool.get("pool_configuration", {})
        pool_cur = pool.get("current_metrics", {})
        labeled(HEALTH_POOL_SIZE).set(pool_cfg.get("max_pool_size", 0))
        labeled(HEALTH_POOL_ACTIVE).set(pool_cur.get("active_connections", 0))
        labeled(HEALTH_POOL_AVAILABLE).set(pool_cur.get("available_connections", 0))
        labeled(HEALTH_POOL_OVERFLOW).set(pool_cur.get("overflow_connections", 0))
        labeled(HEALTH_POOL_UTILIZATION).set(pool_cur.get("utilization_percentage", 0))

    # Database schema
    schema = services.get("database_schema", {})
    if schema:
        labeled(HEALTH_SCHEMA_UP).set(_status(schema.get("status", "unhealthy")))
        labeled(HEALTH_SCHEMA_RESPONSE_MS).set(schema.get("response_time_ms", 0))
        labeled(HEALTH_SCHEMA_REQUIRED_TABLES).set(schema.get("required_tables_count", 0))
        labeled(HEALTH_SCHEMA_EXISTING_TABLES).set(schema.get("existing_table_count", 0))
        missing = schema.get("missing_tables", [])
        labeled(HEALTH_SCHEMA_MISSING_TABLES).set(len(missing) if isinstance(missing, list) else 0)

    # Environment
    env = services.get("environment", {})
    if env:
        labeled(HEALTH_ENV_UP).set(_status(env.get("status", "unhealthy")))
        labeled(HEALTH_ENV_RESPONSE_MS).set(env.get("response_time_ms", 0))

    # Redis
    redis_data = services.get("redis_token_blacklist", {})
    if redis_data:
        labeled(HEALTH_REDIS_UP).set(_status(redis_data.get("status", "unhealthy")))
        labeled(HEALTH_REDIS_RESPONSE_MS).set(redis_data.get("response_time_ms", 0))
        perf = redis_data.get("performance_metrics", {})
        labeled(HEALTH_REDIS_CONNECTED_CLIENTS).set(perf.get("connected_clients", 0))
        labeled(HEALTH_REDIS_KEYSPACE_HITS).set(perf.get("keyspace_hits", 0))
        labeled(HEALTH_REDIS_KEYSPACE_MISSES).set(perf.get("keyspace_misses", 0))
