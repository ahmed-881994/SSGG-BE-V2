import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from pythonjsonlogger import jsonlogger

from app.config.settings import settings
from app.config.version import __version__


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging with Loki compatibility"""
    
    # Fields to extract from log record (high-cardinality, stored as fields not labels)
    CONTEXT_FIELDS = ('request_id', 'method', 'url', 'endpoint', 'status_code', 'client_ip', 'user_id')

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # ISO 8601 timestamp (Loki preferred format)
        log_record['timestamp'] = datetime.fromtimestamp(
            record.created, tz=timezone.utc
        ).isoformat()
        
        # Standard fields - lowercase level for Loki label consistency
        log_record['level'] = record.levelname
        log_record['severity'] = record.levelname  # Original case for compatibility
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Loki labels (low-cardinality for efficient indexing)
        log_record['env'] = settings.environment
        log_record['app'] = 'ssgg-api'
        log_record['job'] = 'ssgg-api'  # Standard Prometheus/Loki convention
        log_record['service'] = settings.otel_service_name
        log_record['version'] = __version__

        otel_trace_id = getattr(record, 'otelTraceID', None)
        if otel_trace_id:
            log_record['trace_id'] = str(otel_trace_id)

        otel_span_id = getattr(record, 'otelSpanID', None)
        if otel_span_id:
            log_record['span_id'] = str(otel_span_id)

        otel_service_name = getattr(record, 'otelServiceName', None)
        if otel_service_name:
            log_record['service'] = str(otel_service_name)
        
        # Process context for multi-replica debugging
        log_record['pid'] = record.process
        log_record['thread'] = record.thread
        
        # Extract request context fields
        for field in self.CONTEXT_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                log_record[field] = value
        
        # Handle process_time with millisecond conversion
        process_time = getattr(record, 'process_time', None)
        if process_time is not None:
            log_record['duration_ms'] = round(process_time * 1000, 2)

    def format(self, record):
        """Ensure message field is always present"""
        if not record.msg:
            record.msg = "log_event"
        return super().format(record)


class StandardFormatter(logging.Formatter):
    """Custom formatter for human-readable logging (fallback)"""

    def format(self, record: logging.LogRecord) -> str:
        # Start with basic format
        base_format = super().format(record)

        # Add extra context if present
        extras = []
        request_id = getattr(record, 'request_id', None)
        if request_id:
            extras.append(f"request_id={request_id}")

        method = getattr(record, 'method', None)
        if method:
            extras.append(f"{method}")

        url = getattr(record, 'url', None)
        if url:
            extras.append(f"{url}")

        status_code = getattr(record, 'status_code', None)
        if status_code:
            extras.append(f"status={status_code}")

        process_time = getattr(record, 'process_time', None)
        if process_time:
            extras.append(f"time={process_time:.3f}s")

        client_ip = getattr(record, 'client_ip', None)
        if client_ip:
            extras.append(f"ip={client_ip}")
            
        version = getattr(record, 'version', None)
        if version:
            extras.append(f"version={version}")
        else:
            extras.append(f"version={__version__}")

        if extras:
            base_format += f" [{', '.join(extras)}]"

        return base_format


def setup_logging():
    """Setup standard logging with default Python format"""
    
    # Create standard formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.log_level.upper())
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level.upper())
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    # Setup app logger
    logger = logging.getLogger("ssgg")
    logger.setLevel(settings.log_level.upper())
    logger.handlers.clear()
    logger.addHandler(console_handler)
    logger.propagate = False
    
    # Configure SQLAlchemy loggers
    for sql_logger_name in ['sqlalchemy.engine.Engine', 'sqlalchemy.engine', 'sqlalchemy']:
        sql_logger = logging.getLogger(sql_logger_name)
        sql_logger.handlers.clear()
        sql_logger.addHandler(console_handler)
        sql_logger.propagate = False
        sql_logger.setLevel(logging.WARNING)
    
    # Configure Uvicorn loggers
    for uvicorn_logger_name in ['uvicorn', 'uvicorn.error', 'uvicorn.access']:
        uvi_logger = logging.getLogger(uvicorn_logger_name)
        uvi_logger.handlers.clear()
        uvi_logger.addHandler(console_handler)
        uvi_logger.propagate = False
    
    return logger


# Global logger instance
logger = setup_logging()
