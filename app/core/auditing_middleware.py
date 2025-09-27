import json
import re
import uuid
from typing import Optional

from fastapi import Request, Response
from fastapi.concurrency import iterate_in_threadpool

from app.config.logging_config import logger
from app.core.database import AsyncSessionLocal
from app.models.audit_model import Audit
from app.util.egy_time import get_egypt_time

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


async def audit_middleware(request: Request, call_next):
    """Middleware for auditing requests and responses"""
    # Generate request ID
    request_id = request.state.request_id if hasattr(request.state, 'request_id') else str(uuid.uuid4())
    request.state.request_id = request_id
    # Skip auditing for excluded paths and methods
    if (request.url.path in EXCLUDED_PATHS or 
        request.method in EXCLUDED_METHODS):
        return await call_next(request)
    
    # Extract user ID from request (adjust based on your auth implementation)
    user_id, member_id = await get_user_id_from_request(request)

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
            member_id=member_id,
            action=f"{request.method} {request.url.path}",
            request_data=request_data,
            response_data=response_data,
            ip_address=ip_address,
            request_id=request_id
        )
        response.headers["x-request-id"] = request_id
        return response
        
    except Exception as e:
        # Log the error in audit
        await save_audit_record(
            user_id=user_id,
            member_id=member_id,
            action=f"{request.method} {request.url.path}",
            request_data=request_data,
            response_data=f"ERROR: {str(e)}",
            ip_address=ip_address,
            request_id=request_id
        )
        raise


async def get_user_id_from_request(request: Request) -> tuple[Optional[int], Optional[str]]:
    """Extract user ID from request - adjust based on your auth implementation"""
    try:
        return getattr(request.state, 'user_id', None), getattr(request.state, 'member_id', None)
    except Exception:
        return None, None


async def capture_request_data(request: Request) -> str:
    """Capture relevant request data for auditing with sensitive data masking"""
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
                    # Try to parse as JSON first
                    parsed_body = json.loads(body.decode())
                    # Mask sensitive fields in JSON
                    parsed_body = mask_sensitive_json_data(parsed_body)
                    data["body"] = parsed_body
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Handle multipart/form-data and other formats
                    body_str = body.decode('utf-8', errors='ignore')
                    # Mask sensitive data in raw body
                    body_str = mask_sensitive_form_data(body_str)
                    data["body"] = body_str
                
                # Store body for endpoint to use
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive
        
        # Remove/mask sensitive headers
        sensitive_headers = {"authorization", "cookie", "x-api-key", "x-auth-token"}
        data["headers"] = {
            k: "***MASKED***" if k.lower() in sensitive_headers else v
            for k, v in data["headers"].items()
        }
        
        return json.dumps(data, default=str)
        
    except Exception as e:
        logger.warning(f"Failed to capture request data: {str(e)}")
        return f"Error capturing request data: {str(e)}"


async def capture_response_data(response: Response) -> str:
    """Capture relevant response data for auditing with sensitive data masking"""
    try:
        res_body = [section async for section in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(res_body))
        payload_raw = res_body[0].decode() if res_body else None
        
        # Try to parse the payload as JSON to avoid double encoding
        if payload_raw:
            try:
                # Parse the JSON payload
                parsed_payload = json.loads(payload_raw)
                # Mask sensitive data in response
                parsed_payload = mask_sensitive_response_data(parsed_payload)
                payload_to_store = parsed_payload
            except json.JSONDecodeError:
                # If not valid JSON, check for sensitive data in raw text
                payload_to_store = mask_sensitive_text(payload_raw)
        else:
            payload_to_store = None
        
        data = {
            "payload": payload_to_store,
            "status_code": response.status_code,
            "headers": dict(response.headers),
        }

        return json.dumps(data, default=str, ensure_ascii=False)  # Added ensure_ascii=False for better Unicode handling

    except Exception as e:
        logger.warning(f"Failed to capture response data: {str(e)}")
        return f"Error capturing response data: {str(e)}"


def mask_sensitive_json_data(data):
    """Mask sensitive fields in JSON data"""
    if isinstance(data, dict):
        masked_data = {}
        for key, value in data.items():
            if key.lower() in ['password', 'passwd', 'pwd', 'oldpassword', 'newpassword', 'secret', 'token', 'key', 'auth']:
                masked_data[key] = "***MASKED***"
            elif isinstance(value, (dict, list)):
                masked_data[key] = mask_sensitive_json_data(value)
            else:
                masked_data[key] = value
        return masked_data
    elif isinstance(data, list):
        return [mask_sensitive_json_data(item) for item in data]
    else:
        return data


def mask_sensitive_form_data(body_str: str) -> str:
    """Mask sensitive data in multipart form data"""
    # Pattern to match form fields with sensitive names
    sensitive_patterns = [
        r'(name="password"[^-]*?\r?\n\r?\n)([^-\r\n]+)',
        r'(name="passwd"[^-]*?\r?\n\r?\n)([^-\r\n]+)',
        r'(name="pwd"[^-]*?\r?\n\r?\n)([^-\r\n]+)',
        r'(name="secret"[^-]*?\r?\n\r?\n)([^-\r\n]+)',
        r'(name="token"[^-]*?\r?\n\r?\n)([^-\r\n]+)',
        r'(name="key"[^-]*?\r?\n\r?\n)([^-\r\n]+)',
    ]
    
    masked_body = body_str
    for pattern in sensitive_patterns:
        masked_body = re.sub(pattern, r'\1***MASKED***', masked_body, flags=re.IGNORECASE)
    
    return masked_body

def mask_sensitive_response_data(data):
    """Mask sensitive fields in response data"""
    if isinstance(data, dict):
        masked_data = {}
        for key, value in data.items():
            # Mask tokens and sensitive response fields
            if key.lower() in ['access_token', 'refresh_token', 'token', 'password', 'secret', 'key']:
                masked_data[key] = "***MASKED***"
            elif isinstance(value, (dict, list)):
                masked_data[key] = mask_sensitive_response_data(value)
            else:
                masked_data[key] = value
        return masked_data
    elif isinstance(data, list):
        return [mask_sensitive_response_data(item) for item in data]
    else:
        return data


def mask_sensitive_text(text: str) -> str:
    """Mask sensitive data in plain text"""
    # This is a fallback for non-JSON responses
    sensitive_keywords = ['password', 'token', 'secret', 'key', 'auth']
    
    for keyword in sensitive_keywords:
        # Simple pattern to mask values after sensitive keywords
        pattern = rf'({keyword}["\']?\s*[:=]\s*["\']?)([^"\',\s\n\r]+)'
        text = re.sub(pattern, r'\1***MASKED***', text, flags=re.IGNORECASE)
    
    return text

async def save_audit_record(
    user_id: Optional[int],
    member_id: Optional[str],
    action: str,
    request_data: str,
    response_data: str,
    ip_address: Optional[str],
    request_id: str
):
    """Save audit record to database"""
    try:
        async with AsyncSessionLocal() as session:
            audit_record = Audit() 
            audit_record.user_id = user_id
            audit_record.member_id = member_id
            audit_record.action = action
            audit_record.request_data = request_data
            audit_record.response_data = response_data
            try:
                response_json = json.loads(response_data)
                audit_record.status_code = response_json.get("status_code")
            except (json.JSONDecodeError, AttributeError):
                audit_record.status_code = None
            audit_record.ip_address = ip_address
            audit_record.request_id = request_id
            audit_record.created_at = get_egypt_time()
            session.add(audit_record)
            await session.commit()
    except Exception as e:
        logger.error(f"Failed to save audit record: {str(e)}", exc_info=True)
        await session.rollback()
        raise
    finally:
        await session.close()