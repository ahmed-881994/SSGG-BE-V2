import re
from typing import List

from sqlalchemy.orm import Session

from app.config.logging_config import logger
from app.models.rbac_models import PublicRoute, RoutePattern
from app.services.user_service import UserService


class AccessControlService:
    def __init__(self, db: Session):
        self.db = db

    def is_public_route(self, path: str) -> bool:
        # Get all active public routes
        public_routes = self.db.query(PublicRoute).filter(
            PublicRoute.is_active == True
        ).all()
        
        public_route_paths = [public_route.path_pattern for public_route in public_routes]
        return path in public_route_paths

    def get_route_permission(self, method: str, path: str) -> List[str]:
        # Logic to fetch required permission for a given route
        permissions = []
        
        # First try exact match
        route_pattern = self.db.query(RoutePattern).filter(
            RoutePattern.method == method.upper(),
            RoutePattern.path_pattern == path,
            RoutePattern.is_active == True
        ).first()
        
        if not route_pattern:
            # Try pattern matching for parameterized routes
            route_patterns = self.db.query(RoutePattern).filter(
                RoutePattern.method == method.upper(),
                RoutePattern.is_active == True
            ).all()

            for pattern in route_patterns:
                # Convert route pattern to regex
                regex_pattern = re.sub(r'\{[^}]+\}', r'[^/]+', pattern.path_pattern)
                regex_pattern = f"^{regex_pattern}$"
                
                try:
                    if re.match(regex_pattern, path):
                        route_pattern = pattern
                        break
                except re.error:
                    logger.warning(f"Invalid route pattern: {pattern.path_pattern}")
                    continue
        if route_pattern:
            permissions = [ permission.name for permission in route_pattern.permissions ] if route_pattern.permissions else []
        return permissions


    def user_has_permission(self, user_id: str, required_permissions: List[str]) -> bool:
        user_service = UserService(self.db)
        user = user_service.get_user_by_id(int(user_id))
        if not user:
            return False
        user_permissions = {perm.name for perm in user.role.permissions} if user.role else set()
        
        for req_perm in required_permissions:
            if req_perm not in user_permissions:
                logger.warning(f"User {user_id} lacks permission '{req_perm}'")
                return False
        return True