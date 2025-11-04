from fastapi import Request

from app.config.logging_config import logger
from app.services.token_service import token_service


class UserContextMiddleware:
    async def __call__(self, request: Request, call_next):
        """Middleware to extract user context without enforcing authentication"""
        # Extract user from token if present (but don't fail if missing)
        user_id = None
        member_id = None

        try:
            auth_header = request.headers.get("authorization")
            if auth_header:
                scheme, token = auth_header.split()
                if scheme.lower() == "bearer":
                    # Decode token without verification for context only
                    # Your existing auth routes will still do full validation
                    payload = token_service.verify_token(token)
                    member_id = payload.get("member_id")
                    user_id = payload.get("sub")
                    # Attach user context to request state (even if None)
                    request.state.user_id = user_id
                    request.state.member_id = member_id
        except Exception:
            logger.error("Error extracting user context from token", exc_info=True)

        response = await call_next(request)
        return response
    
    
user_context_middleware = UserContextMiddleware()
