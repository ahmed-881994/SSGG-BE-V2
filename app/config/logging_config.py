import logging
import json
from datetime import datetime, timezone
# import os
from typing import Any, Dict
from app.config.settings import settings

# os.makedirs("logs", exist_ok=True)

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if hasattr(record, 'client_ip'):
            log_entry['client_ip'] = record.client_ip  # type: ignore[attr-defined]
        if hasattr(record, 'user_agent'):
            log_entry['user_agent'] = record.user_agent  # type: ignore[attr-defined]
        if hasattr(record, 'method'):
            log_entry['method'] = record.method  # type: ignore[attr-defined]
        if hasattr(record, 'url'):
            log_entry['url'] = record.url  # type: ignore[attr-defined]
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code  # type: ignore[attr-defined]
        if hasattr(record, 'process_time'):
            log_entry['process_time'] = record.process_time  # type: ignore[attr-defined]
        
        # Add extra fields if present
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id  # type: ignore[attr-defined]
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id  # type: ignore[attr-defined]
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint  # type: ignore[attr-defined]
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

def setup_logging():
    """Setup structured logging"""
    # Create logger
    logger = logging.getLogger("ssgg")
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(StructuredFormatter())
    
    # Create file handler
    # file_handler = logging.FileHandler("logs/ssgg.log")
    # file_handler.setLevel(logging.DEBUG)
    # file_handler.setFormatter(StructuredFormatter())
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    # logger.addHandler(file_handler)
    
    return logger

# Global logger instance
logger = setup_logging()