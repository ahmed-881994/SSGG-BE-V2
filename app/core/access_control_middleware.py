from fastapi import Request, status
from fastapi.responses import JSONResponse
import ipaddress

from app.config.logging_config import logger
from app.core.database import get_db_session
from app.services.access_control_service import AccessControlService

#TODO: #18 The method fetches the user from the database every time permissions are checked, even though the user is already authenticated and their permissions could be cached in the request context. Consider using permissions from the JWT token (which are already included in the token payload) to avoid this database query on every request.

# Docker overlay network ranges (internal only)
INTERNAL_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
]

def _is_internal_ip(ip_str: str) -> bool:
    """Check if IP is from internal Docker networks."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return any(ip in network for network in INTERNAL_NETWORKS)
    except ValueError:
        return False

def _get_client_ip(request: Request) -> str:
    """Get real client IP, accounting for reverse proxy headers."""
    # Trust X-Forwarded-For from Traefik
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # First IP is the original client
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""

def _is_internal_request(request: Request) -> bool:
    """
    Check if request is internal (from Docker overlay network).
    
    Logic:
    - If no X-Forwarded-For header, it's a direct internal call (not through Traefik)
    - If X-Forwarded-For exists, check if the original client IP is internal
    """
    forwarded = request.headers.get("x-forwarded-for")
    
    # No X-Forwarded-For means direct call within Docker network (e.g., Prometheus)
    # External requests always go through Traefik which adds this header
    if not forwarded:
        client_ip = request.client.host if request.client else ""
        logger.debug(f"/metrics request from direct connection, client IP: {client_ip}")
        return True  # Direct internal call
    
    # Has X-Forwarded-For, check if original client is internal
    client_ip = forwarded.split(",")[0].strip()
    is_internal = _is_internal_ip(client_ip)
    logger.debug(f"/metrics request via proxy, X-Forwarded-For: {forwarded}, is_internal: {is_internal}")
    return is_internal

class AccessControlMiddleware:

    async def __call__(self, request: Request, call_next):
        try:
            # Check if the route is public
            path = request.url.path
            method = request.method
            

            # Allow /metrics only from internal networks (Prometheus)
            if path == "/metrics":
                if _is_internal_request(request):
                    return await call_next(request)
                else:
                    client_ip = _get_client_ip(request)
                    logger.warning(f"Blocked /metrics access from external IP: {client_ip}")
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "Metrics endpoint is internal only"}
                    )

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
            token_permissions = getattr(request.state, "user_permissions", None)
            if isinstance(token_permissions, set) and token_permissions:
                has_access = access_service.user_has_permission(
                    user_id=str(user_id),
                    required_permissions=required_permissions,
                    user_permissions=token_permissions,
                )
            else:
                has_access = access_service.user_has_permission(
                    user_id=str(user_id),
                    required_permissions=required_permissions,
                    user_permissions=None,
                )

            if not has_access:
                logger.warning(
                    f"Access denied: user={user_id}, route={method}:{path}, required_permissions={required_permissions}"
                )
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "detail": "Insufficient permissions",
                        "required_permissions": required_permissions,
                    },
                )
            # if not access_service.user_has_permission(user_id, required_permissions):
            #     logger.warning(
            #         f"Access denied: user={user_id}, route={method}:{path}, "
            #         f"required_permissions={required_permissions}"
            #     )
            #     return JSONResponse(
            #         status_code=status.HTTP_403_FORBIDDEN,
            #         content={
            #             "detail": "Insufficient permissions",
            #             "required_permissions": required_permissions
            #         }
            #     )

            return await call_next(request)
        except Exception as e:
            logger.error(f"Access control error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )
        finally:
            if 'db' in locals():
                db.close()

access_control_middleware = AccessControlMiddleware()
