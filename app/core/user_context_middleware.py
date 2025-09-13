from fastapi import Request
from typing import Optional
import jwt

from app.config.logging_config import logger
from app.config.settings import settings


async def user_context_middleware(request: Request, call_next):
    """Middleware to extract user context without enforcing authentication"""
    
    # Extract user from token if present (but don't fail if missing)
    user_id = None
    member_id = None
    
    try:
        auth_header = request.headers.get("authorization")
        if auth_header:
            try:
                scheme, token = auth_header.split()
                if scheme.lower() == "bearer":
                    # Decode token without verification for context only
                    # Your existing auth routes will still do full validation
                    payload = jwt.decode(
                        token, 
                        settings.secret_key, 
                        algorithms=settings.algorithm,
                        options={"verify_exp": True}  # Don't fail on expired tokens
                    )
                    member_id = payload.get("member_id")
                    user_id = payload.get("sub")
            except jwt.InvalidTokenError:
                pass  # Invalid token, continue without user context
    except Exception:
        pass  # Any error, continue without user context
    
    # Attach user context to request state (even if None)
    request.state.user_id = user_id
    request.state.member_id = member_id

    response = await call_next(request)
    return response