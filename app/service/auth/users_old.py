"""
User Authentication Service Module - DEPRECATED

This module is deprecated. Use the new modular auth services:
- app.service.auth.auth_service for user authentication
- app.service.auth.token_service for token operations
- app.service.auth.dependencies for FastAPI dependencies

This file is kept for backward compatibility and will be removed in future versions.
"""

# Import new services for backward compatibility
from app.service.auth.auth_service import auth_service
from app.service.auth.token_service import token_service
from app.service.auth.dependencies import get_current_user, get_active_user, oauth2_scheme

# Deprecated function aliases - use new services instead
def authenticate_user(username: str, password: str):
    """DEPRECATED: Use auth_service.authenticate_user instead"""
    return auth_service.authenticate_user(username, password)

def get_user_by_id_db(user_name: str):
    """DEPRECATED: Use auth_service.get_user_by_username instead"""
    return auth_service.get_user_by_username(user_name)

async def login_user(current_user):
    """DEPRECATED: Use get_active_user dependency instead"""
    auth_service.validate_user_active(current_user)
    return current_user

def logout_user(token: str) -> bool:
    """DEPRECATED: Use token_service.blacklist_token instead"""
    return token_service.blacklist_token(token)
