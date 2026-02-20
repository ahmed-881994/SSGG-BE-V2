import time
import uuid

from fastapi import Request

from app.config.logging_config import logger

# Endpoints to exclude from logging
EXCLUDED_PATHS = {
    "/health",
    "/metrics",
    "/favicon.ico",
    "/docs",
    "/redoc",
    "/openapi.json"
}

# Methods to exclude from logging
EXCLUDED_METHODS = {"OPTIONS", "HEAD"}

async def logging_middleware(request: Request, call_next):
    """Middleware for request/response logging"""
    # Generate request ID
    request_id = request.state.request_id if hasattr(request.state, 'request_id') else str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Skip logging for excluded paths and methods
    if request.url.path in EXCLUDED_PATHS or request.method in EXCLUDED_METHODS:
        return await call_next(request)
    
    # Log request
    start_time = time.time()
    logger.info(
        "Request started " + " " + str(request.method) + " " + str(request.url.path) + " " + str(request_id),
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url.path),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
    )
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            "Request completed " + str(request_id) + " " + str(response.status_code),
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": process_time,
            }
        )
        
        # Add request ID to response headers
        response.headers["x-request-id"] = request_id
        response.headers["x-process-time"] = str(process_time)
        
        return response
        
    except Exception as e:
        # Log error
        logger.error(
            "Request failed",
            extra={
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True
        )
        raise