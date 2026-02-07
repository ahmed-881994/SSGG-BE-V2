import logging
import json
from datetime import datetime, timezone
from typing import Any, Dict
from pythonjsonlogger import jsonlogger
from app.config.settings import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging with Loki compatibility"""

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Standard fields
        log_record['timestamp'] = record.created
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Add environment label for Loki filtering
        log_record['environment'] = settings.environment
        
        # Add application metadata
        log_record['app'] = 'ssgg-api'
        log_record['version'] = '2.0.0'
        
        # Process ID for multi-replica debugging
        log_record['pid'] = record.process
        log_record['thread'] = record.thread
        
        # Add request context if present
        request_id = getattr(record, 'request_id', None)
        if request_id:
            log_record['request_id'] = request_id
        
        method = getattr(record, 'method', None)
        if method:
            log_record['method'] = method
        
        url = getattr(record, 'url', None)
        if url:
            log_record['url'] = url
        
        endpoint = getattr(record, 'endpoint', None)
        if endpoint:
            log_record['endpoint'] = endpoint
        
        status_code = getattr(record, 'status_code', None)
        if status_code:
            log_record['status_code'] = status_code
        
        process_time = getattr(record, 'process_time', None)
        if process_time:
            log_record['process_time'] = process_time
            log_record['duration'] = process_time  # Alias for compatibility
        
        client_ip = getattr(record, 'client_ip', None)
        if client_ip:
            log_record['client_ip'] = client_ip
        
        user_id = getattr(record, 'user_id', None)
        if user_id:
            log_record['user_id'] = user_id


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

        if extras:
            base_format += f" [{', '.join(extras)}]"

        return base_format


def setup_logging():
    """Setup structured logging with JSON format for Loki compatibility"""
    # Create logger
    logger = logging.getLogger("ssgg")
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Use JSON formatter for production, human-readable for development
    if settings.environment in ['prd', 'production', 'staging']:
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        formatter = StandardFormatter(
            fmt='%(levelname)s: %(asctime)s %(name)s.%(module)s.%(funcName)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.log_level.upper())
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)

    return logger


# Global logger instance
logger = setup_logging()
