import re
import time
from typing import Dict, List, Pattern, Set, Tuple

from sqlalchemy.orm import Session, joinedload

from app.config.logging_config import logger
from app.models.rbac_models import PublicRoute, RoutePattern
from app.services.user_service import UserService


class AccessControlService:
    
    CACHE_TTL_SECONDS = 86400  # 1day
    
    _public_routes_cache: Set[str] = set()
    _public_routes_cache_expires_at: float = 0.0

    _route_patterns_cache: Dict[str, List[Tuple[Pattern[str], List[str]]]] = {}
    _route_patterns_cache_expires_at: float = 0.0
    
    def __init__(self, db: Session):
        self.db = db
        
    @classmethod
    def invalidate_cache(cls) -> None:
        logger.debug("Invalidating access control caches")
        cls._public_routes_cache = set()
        cls._public_routes_cache_expires_at = 0.0
        cls._route_patterns_cache = {}
        cls._route_patterns_cache_expires_at = 0.0
        
    def _refresh_public_routes_cache_if_needed(self) -> None:
        logger.debug("Checking if public routes cache needs refresh")
        now = time.time()
        if now < self._public_routes_cache_expires_at and self._public_routes_cache:
            return

        public_routes = (
            self.db.query(PublicRoute)
            .filter(PublicRoute.is_active == True)
            .all()
        )
        self.__class__._public_routes_cache = {
            pr.path_pattern for pr in public_routes if pr.path_pattern
        }
        self.__class__._public_routes_cache_expires_at = now + self.CACHE_TTL_SECONDS
        logger.debug(f"Public routes cache refreshed with {len(self._public_routes_cache)} routes")

    def _refresh_route_patterns_cache_if_needed(self) -> None:
        logger.debug("Checking if route patterns cache needs refresh")
        now = time.time()
        if now < self._route_patterns_cache_expires_at and self._route_patterns_cache:
            return

        rows = (
            self.db.query(RoutePattern)
            .options(joinedload(RoutePattern.permissions))
            .filter(RoutePattern.is_active == True)
            .all()
        )

        compiled: Dict[str, List[Tuple[Pattern[str], List[str]]]] = {}
        for rp in rows:
            method = (rp.method or "").upper()
            if not method or not rp.path_pattern:
                continue

            regex_pattern = re.sub(r"\{[^}]+\}", r"[^/]+", rp.path_pattern)
            regex_pattern = f"^{regex_pattern}$"

            try:
                pattern = re.compile(regex_pattern)
            except re.error:
                logger.warning(f"Invalid route pattern skipped: {rp.path_pattern}")
                continue

            perms = [p.name for p in (rp.permissions or []) if p and p.name]
            compiled.setdefault(method, []).append((pattern, perms))

        self.__class__._route_patterns_cache = compiled
        self.__class__._route_patterns_cache_expires_at = now + self.CACHE_TTL_SECONDS
        logger.debug(f"Route patterns cache refreshed with {sum(len(v) for v in compiled.values())} patterns")
    
    def is_public_route(self, path: str) -> bool:
        self._refresh_public_routes_cache_if_needed()
        logger.debug(f"Checking if path is public: {path}")
        return path in self._public_routes_cache

    # def is_public_route(self, path: str) -> bool:
    #     # Get all active public routes
    #     public_routes = self.db.query(PublicRoute).filter(
    #         PublicRoute.is_active == True
    #     ).all()
        
    #     public_route_paths = [public_route.path_pattern for public_route in public_routes]
    #     return path in public_route_paths

    
    def get_route_permission(self, method: str, path: str) -> List[str]:
        self._refresh_route_patterns_cache_if_needed()
        logger.debug(f"Getting route permissions for method={method}, path={path}")
        method = method.upper()

        for pattern, perms in self._route_patterns_cache.get(method, []):
            if pattern.match(path):
                logger.debug(f"Route matched: method={method}, path={path}, permissions={perms}")
                return perms

        logger.debug(f"No route matched: method={method}, path={path}")
        return []
    # def get_route_permission(self, method: str, path: str) -> List[str]:
    #     # Logic to fetch required permission for a given route
    #     permissions = []
        
    #     # First try exact match
    #     route_pattern = self.db.query(RoutePattern).filter(
    #         RoutePattern.method == method.upper(),
    #         RoutePattern.path_pattern == path,
    #         RoutePattern.is_active == True
    #     ).first()
        
    #     if not route_pattern:
    #         # Try pattern matching for parameterized routes
    #         route_patterns = self.db.query(RoutePattern).filter(
    #             RoutePattern.method == method.upper(),
    #             RoutePattern.is_active == True
    #         ).all()

    #         for pattern in route_patterns:
    #             # Convert route pattern to regex
    #             regex_pattern = re.sub(r'\{[^}]+\}', r'[^/]+', pattern.path_pattern)
    #             regex_pattern = f"^{regex_pattern}$"
                
    #             try:
    #                 if re.match(regex_pattern, path):
    #                     route_pattern = pattern
    #                     break
    #             except re.error:
    #                 logger.warning(f"Invalid route pattern: {pattern.path_pattern}")
    #                 continue
    #     if route_pattern:
    #         permissions = [ permission.name for permission in route_pattern.permissions ] if route_pattern.permissions else []
    #     return permissions


    def user_has_permission(self,user_id: str,required_permissions: List[str],user_permissions: Set[str] | None = None) -> bool:
        logger.debug(f"Checking permissions for user_id={user_id}, required_permissions={required_permissions}, user_permissions={user_permissions}")
        
        if not required_permissions:
            logger.debug("No required permissions specified, denying access")
            return False

        if user_permissions is not None:
            logger.debug(f"Using permissions from token for user_id={user_id}")
            return all(rp in user_permissions for rp in required_permissions)

        user_service = UserService(self.db)
        user = user_service.get_user_by_id(int(user_id))
        if not user:
            logger.debug(f"User not found: user_id={user_id}")
            return False

        db_permissions = {perm.name for perm in user.role.permissions} if user.role else set()
        logger.debug(f"User permissions from DB for user_id={user_id}: {db_permissions}")
        return all(rp in db_permissions for rp in required_permissions)
    
    # def user_has_permission(self, user_id: str, required_permissions: List[str]) -> bool:
    #     user_service = UserService(self.db)
    #     user = user_service.get_user_by_id(int(user_id))
    #     if not user:
    #         return False
    #     user_permissions = {perm.name for perm in user.role.permissions} if user.role else set()
        
    #     for req_perm in required_permissions:
    #         if req_perm not in user_permissions:
    #             logger.warning(f"User {user_id} lacks permission '{req_perm}'")
    #             return False
    #     return True