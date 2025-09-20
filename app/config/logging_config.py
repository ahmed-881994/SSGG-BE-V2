import logging
import json
from datetime import datetime, timezone
# import os
from typing import Any, Dict
from app.config.settings import settings

# os.makedirs("logs", exist_ok=True)


class StandardFormatter(logging.Formatter):
    """Custom formatter for structured logging"""

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
    """Setup structured logging"""
    # Create logger
    logger = logging.getLogger("ssgg")
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Create formatter with standard format
    formatter = StandardFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s.%(module)s.%(funcName)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.log_level.upper())
    console_handler.setFormatter(formatter)

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
