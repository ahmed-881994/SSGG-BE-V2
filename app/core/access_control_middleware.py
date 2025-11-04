from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.config.logging_config import logger
from app.core.database import get_db_session
from app.services.access_control_service import AccessControlService

#TODO: #18 The method fetches the user from the database every time permissions are checked, even though the user is already authenticated and their permissions could be cached in the request context. Consider using permissions from the JWT token (which are already included in the token payload) to avoid this database query on every request.

class AccessControlMiddleware:

    async def __call__(self, request: Request, call_next):
        try:
            # Check if the route is public
            path = request.url.path
            method = request.method

            # Get database session
            db = next(get_db_session())

            # Initialize access control service
            access_service = AccessControlService(db)
            # Skip public routes
            if access_service.is_public_route(path):
                return await call_next(request)

            user_id = getattr(request.state, 'user_id', None)

            if not user_id:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication required"}
                )

            # Get required permissions for this route
            required_permissions = access_service.get_route_permission(
                method, path)

            if not required_permissions:
                logger.warning(f"No permissions defined for route: {method}:{path}")
                # For security, deny access to undefined routes
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "detail": "Route not configured in access control system",
                        "route": f"{method}:{path}"
                    }
                )
            
            # Check if user has required permissions
            if not access_service.user_has_permission(user_id, required_permissions):
                logger.warning(
                    f"Access denied: user={user_id}, route={method}:{path}, "
                    f"required_permissions={required_permissions}"
                )
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "detail": "Insufficient permissions",
                        "required_permissions": required_permissions
                    }
                )

            return await call_next(request)
        except Exception as e:
            logger.error(f"Access control error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )
        finally:
            db.close()

access_control_middleware = AccessControlMiddleware()
