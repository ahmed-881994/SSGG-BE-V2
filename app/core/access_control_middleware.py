import re
from typing import Dict, Optional

from fastapi import Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.core.database import get_db_session
from app.services.user_service import UserService


class AccessControlMiddleware:
    
    def __init__(self):
        # Define route patterns and their required permissions
        self.route_permissions = self._build_route_permissions()
        
        # Routes that don't require authentication
        self.public_routes = {
            "/docs", "/redoc", "/openapi.json", "/favicon.ico",
            "/health", "/health/", "/token", "/refresh"
        }
        
        # Route patterns that don't require authentication (regex)
        self.public_route_patterns = [
            r"^/docs.*",
            r"^/redoc.*", 
            r"^/openapi\.json.*",
            r"^/health/?$",
            r"^/auth/.*",
            r"^/static/.*"
        ]

    def _build_route_permissions(self) -> Dict[str, str]:
        """Build mapping of route patterns to required permissions"""
        return {
            # User Management Routes
            "GET:/users": "read_user",
            "POST:/users": "create_user", 
            "GET:/users/{user_id}": "read_user",
            "PATCH:/users/{user_id}": "update_user",
            "DELETE:/users/{user_id}": "delete_user",
            "POST:/users/{user_id}/reset-password": "reset_password",
            "PATCH:/users/{user_id}/password": "update_password",
            
            # Member Management Routes
            "GET:/members": "read_member",
            "POST:/members": "create_member",
            "GET:/members/{member_id}": "read_member",
            "PUT:/members/{member_id}": "update_member",
            "DELETE:/members/{member_id}": "delete_member",
            "GET:/members/{member_id}/attendance": "read_member_attendance",
            
            # Entity Management Routes
            "GET:/entities": "read_entity",
            "POST:/entities": "create_entity",
            "GET:/entities/{entity_id}": "read_entity",
            "PUT:/entities/{entity_id}": "update_entity",
            "DELETE:/entities/{entity_id}": "delete_entity",
            "POST:/entities/{entity_id}/members": "assign_entity_members",
            "DELETE:/entities/{entity_id}/members/{member_id}": "assign_entity_members",
            "POST:/entities/{entity_id}/members/roles": "update_entity_members_roles",
            "POST:/entities/transfer": "transfer_members",
            
            # Event Management Routes
            "GET:/events": "read_event",
            "POST:/events": "create_event",
            "GET:/events/{event_id}": "read_event", 
            "PUT:/events/{event_id}": "update_event",
            "DELETE:/events/{event_id}": "delete_event",
            "PUT:/events/{event_id}/attendance": "update_event_attendance",
            "GET:/events/{event_id}/attendance": "read_event_attendance",

            # Lookup Routes
            "GET:/lookups": "read_lookups",
            # "POST:/lookups": "manage_lookups",
            # "PUT:/lookups/{lookup_id}": "manage_lookups",
            # "DELETE:/lookups/{lookup_id}": "manage_lookups",
            
            # Health Check Routes
            "GET:/health/report": "read_health_report",
            
            # ABAC Management Routes
            # "GET:/abac/policies": "manage_abac_policies",
            # "POST:/abac/policies": "manage_abac_policies",
            # "PUT:/abac/policies/{policy_id}": "manage_abac_policies",
            # "DELETE:/abac/policies/{policy_id}": "manage_abac_policies",
            # "POST:/abac/users/{user_id}/attributes": "manage_user_attributes",
            # "GET:/abac/users/{user_id}/effective-permissions": "view_user_permissions",
            
            # # Permission Routes
            # "GET:/permissions/me": "read_user",  # Users can see their own permissions
        }

    def _is_public_route(self, path: str) -> bool:
        """Check if route is public (doesn't require authentication)"""
        # Check exact matches
        if path in self.public_routes:
            return True
            
        # Check pattern matches
        for pattern in self.public_route_patterns:
            if re.match(pattern, path):
                return True
                
        return False
    
    def _extract_route_key(self, method: str, path: str) -> Optional[str]:
        """Extract route key for permission lookup, handling path parameters"""
        # First try exact match
        route_key = f"{method}:{path}"
        if route_key in self.route_permissions:
            return route_key
            
        # Try with path parameter patterns
        for pattern_key in self.route_permissions.keys():
            pattern_method, pattern_path = pattern_key.split(":", 1)
            
            if method != pattern_method:
                continue
                
            # Convert route pattern to regex
            # Replace {param} with regex pattern
            regex_pattern = re.sub(r'\{[^}]+\}', r'[^/]+', pattern_path)
            regex_pattern = f"^{regex_pattern}$"
            
            if re.match(regex_pattern, path):
                return pattern_key
                
        return None
    
    def _has_permission(self, user_id: str, route_key: str) -> bool:
        """Check if user has the required permission for the route"""
        db = next(get_db_session())
        user_service = UserService(db)
        user = user_service.get_user_by_id(int(user_id))
        if not user:
            return False
        user_permissions = user.role.permissions if user.role else []
        required_permission = self.route_permissions.get(route_key)
        
        if not user.role or required_permission not in user_permissions:
            logger.warning(f"User {user_id} lacks permission '{required_permission}' for route '{route_key}'")
            return False
        return True
    
    async def __call__(self, request: Request, call_next):
        try:
            # Check if the route is public
            path = request.url.path
            method = request.method
            
            # Skip public routes
            if self._is_public_route(path):
                return await call_next(request)
            
            user_id = getattr(request.state, 'user_id', None)
            
            if not user_id:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication required"}
                )

            # Extract the route key for permission lookup
            route_key = self._extract_route_key(method, path)
            
            if not route_key:
                logger.warning(f"Route not found in RBAC config: {method}:{path}")
                return await call_next(request)

            # Check permissions
            if not self._has_permission(user_id, route_key):
                return JSONResponse(status_code=403, content={"detail": "Forbidden"})

            return await call_next(request)
        except Exception as e:
            logger.error(f"Access control error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )
            
access_control_middleware = AccessControlMiddleware()