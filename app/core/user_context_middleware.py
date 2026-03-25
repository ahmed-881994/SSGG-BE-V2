from fastapi import Request

from app.config.logging_config import logger
from app.services.token_service import token_service


class UserContextMiddleware:
    async def __call__(self, request: Request, call_next):
        """
        Middleware to extract user context without enforcing authentication.
        Adds user_id/member_id/permissions/role into request.state for downstream authz.
        """
        # Extract user from token if present (but don't fail if missing)
        request.state.user_id = None
        request.state.member_id = None
        request.state.user_permissions = set()
        request.state.user_role = None

        try:
            logger.debug("Extracting user context from token if present")
            auth_header = request.headers.get("authorization")
            if auth_header:
                logger.debug(f"Authorization header found: {auth_header[:20]}...")  # Log only the beginning for security
                parts = auth_header.split(maxsplit=1)
                if len(parts) == 2:
                    scheme, token = parts
                    if scheme.lower() == "bearer":
                        logger.debug("Bearer token found, verifying token")
                        # decode token and extract user context
                        payload = token_service.verify_token(token)
                        logger.debug(f"Token verified successfully, payload: {payload}")
                        request.state.member_id = payload.get("member_id")
                        request.state.user_id = payload.get("sub")
                        request.state.user_role = payload.get("role")
                        permissions = payload.get("permissions") or []
                        if isinstance(permissions, list):
                            request.state.user_permissions = set(str(p) for p in permissions if p)
                        logger.debug(f"Extracted user context - user_id: {request.state.user_id}, member_id: {request.state.member_id}, role: {request.state.user_role}, permissions: {request.state.user_permissions}")
        except Exception:
            logger.error("Error extracting user context from token", exc_info=True)

        response = await call_next(request)
        return response
    
    
user_context_middleware = UserContextMiddleware()
