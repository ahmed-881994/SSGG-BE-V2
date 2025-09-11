import json
import time
from datetime import datetime
from typing import Optional

from fastapi import Request, Response
from fastapi.concurrency import iterate_in_threadpool
import pytz
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db_session
from app.config.logging_config import logger
from app.models.audit_model import Audit


# Endpoints to exclude from auditing
EXCLUDED_PATHS = {
    "/health",
    "/favicon.ico",
    "/docs",
    "/redoc",
    "/openapi.json"
}

# Methods to exclude from auditing
EXCLUDED_METHODS = {"OPTIONS", "HEAD"}

def get_egypt_time():
    """Get current time in Egypt timezone with DST handling"""
    egypt_tz = pytz.timezone('Africa/Cairo')
    utc_now = datetime.now(pytz.UTC)
    return utc_now.astimezone(egypt_tz)


async def audit_middleware(request: Request, call_next):
    """Middleware for auditing requests and responses"""
    
    # Skip auditing for excluded paths and methods
    if (request.url.path in EXCLUDED_PATHS or 
        request.method in EXCLUDED_METHODS):
        return await call_next(request)
    
    # Extract user ID from request (adjust based on your auth implementation)
    user_id = await get_user_id_from_request(request)
    
    # Skip auditing if no authenticated user (optional)
    # if not user_id:
    #     return await call_next(request)
    
    # Capture request data
    request_data = await capture_request_data(request)
    ip_address = request.client.host if request.client else None
    
    try:
        # Process the request
        response = await call_next(request)
        
        # Capture response data
        response_data = await capture_response_data(response)
        
        # Save audit record asynchronously (fire and forget)
        await save_audit_record(
            user_id=user_id,
            action=f"{request.method} {request.url.path}",
            request_data=request_data,
            response_data=response_data,
            ip_address=ip_address
        )
        
        return response
        
    except Exception as e:
        # Log the error in audit
        await save_audit_record(
            user_id=user_id,
            action=f"{request.method} {request.url.path}",
            request_data=request_data,
            response_data=f"ERROR: {str(e)}",
            ip_address=ip_address
        )
        raise


async def get_user_id_from_request(request: Request) -> Optional[int]:
    """Extract user ID from request - adjust based on your auth implementation"""
    try:
        # This depends on your authentication implementation
        # You might get it from JWT token, session, etc.
        # Example:
        # token = request.headers.get("Authorization")
        # user_id = decode_token(token).get("user_id")
        # return user_id
        return getattr(request.state, 'user_id', None)
    except Exception:
        return None


async def capture_request_data(request: Request) -> str:
    """Capture relevant request data for auditing"""
    try:
        data = {
            "method": request.method,
            "url": str(request.url),
            "ip_address": request.client.host if request.client else None,
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
        }
        
        # Capture body for non-GET requests
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            body = await request.body()
            if body:
                try:
                    # Try to parse as JSON
                    data["body"] = json.loads(body.decode())
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # If not JSON, store as base64 or truncated string
                    data["body"] = body.decode('utf-8', errors='ignore')[:1000]
        
        # Remove sensitive headers
        sensitive_headers = {"authorization", "cookie", "x-api-key"}
        data["headers"] = {
            k: v for k, v in data["headers"].items() 
            if k.lower() not in sensitive_headers
        }
        
        return json.dumps(data, default=str)[:4000]  # Limit size
        
    except Exception as e:
        logger.warning(f"Failed to capture request data: {str(e)}")
        return f"Error capturing request data: {str(e)}"


async def capture_response_data(response: Response) -> str:
    """Capture relevant response data for auditing"""
    try:
        res_body = [section async for section in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(res_body))
        payload_raw = res_body[0].decode() if res_body else None
        
        # Try to parse the payload as JSON to avoid double encoding
        if payload_raw:
            try:
                # Parse the JSON payload
                parsed_payload = json.loads(payload_raw)
                payload_to_store = parsed_payload  # Store as object, not string
            except json.JSONDecodeError:
                # If not valid JSON, store as string
                payload_to_store = payload_raw
        else:
            payload_to_store = None
        
        data = {
            "payload": payload_to_store,  # This will be properly encoded by json.dumps()
            "status_code": response.status_code,
            "headers": dict(response.headers),
        }

        return json.dumps(data, default=str, ensure_ascii=False)  # Added ensure_ascii=False for better Unicode handling

    except Exception as e:
        logger.warning(f"Failed to capture response data: {str(e)}")
        return f"Error capturing response data: {str(e)}"


async def save_audit_record(
    user_id: int,
    action: str,
    request_data: str,
    response_data: str,
    ip_address: Optional[str]
):
    """Save audit record to database"""
    try:
        session_generator = get_async_db_session()
        session = await session_generator.__anext__()
        try:
            audit_record = Audit()
            audit_record.user_id = user_id
            audit_record.action = action
            audit_record.request_data = request_data
            audit_record.response_data = response_data
            audit_record.status_code = json.loads(response_data).get("status_code")  # Could be set if needed
            audit_record.ip_address = ip_address
            audit_record.created_at = get_egypt_time()
            session.add(audit_record)
            await session.commit()
        finally:
            await session.close()
            
    except Exception as e:
        # Log the error but don't fail the request
        logger.error(f"Failed to save audit record: {str(e)}", exc_info=True)