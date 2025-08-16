"""
Authentication Service Module

Centralized authentication service handling user authentication,
user retrieval, and validation operations.
"""

import time
from typing import Optional

from app.config.logging_config import logger
from app.exceptions.exceptions import AuthenticationFailed
from app.schema.users.user import User
from app.util.password import verify_password
from app.util.pymysql_pool import db_pool


class AuthService:
    """Centralized authentication service"""
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password
        
        Args:
            username: The username to authenticate
            password: The plain text password to verify
            
        Returns:
            Optional[User]: User object if authentication successful, None otherwise
        """
        logger.info(f"Attempting authentication for user: {username}")
        start_time = time.time()
        
        try:
            user = self.get_user_by_username(username)
            if not user:
                logger.warning(f"Authentication failed: User '{username}' not found")
                return None
                
            if not verify_password(password, user.password_hash, user.salt):
                logger.warning(f"Authentication failed: Invalid password for user '{username}'")
                return None
                
            auth_time = round((time.time() - start_time) * 1000, 2)
            logger.info(f"Authentication successful for user '{username}' in {auth_time}ms")
            return user
            
        except Exception as e:
            auth_time = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Authentication error for user '{username}' after {auth_time}ms: {str(e)}", exc_info=True)
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve user from database by username
        
        Args:
            username: The username to search for
            
        Returns:
            Optional[User]: User object if found, None otherwise
        """
        logger.debug(f"Retrieving user from database: {username}")
        start_time = time.time()
        
        conn = None
        try:
            conn = db_pool.get_connection()
            if conn is None:
                logger.error("Failed to get database connection for user retrieval")
                return None
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE user_name = %s", (username,))
                user_data = cursor.fetchone()
            
            query_time = round((time.time() - start_time) * 1000, 2)
            
            if user_data:
                user = User(**user_data)
                logger.debug(f"User '{username}' retrieved successfully in {query_time}ms")
                return user
            else:
                logger.debug(f"User '{username}' not found in database (query took {query_time}ms)")
                return None
                
        except Exception as e:
            query_time = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Database error retrieving user '{username}' after {query_time}ms: {str(e)}", exc_info=True)
            return None
        finally:
            if conn:
                db_pool.return_connection(conn)
    
    def validate_user_active(self, user: User) -> None:
        """
        Validate that user is active
        
        Args:
            user: User object to validate
            
        Raises:
            AuthenticationFailed: If user is inactive
        """
        if user.is_active == 0:
            logger.warning(f"User '{user.user_name}' is inactive")
            raise AuthenticationFailed(message="User is not active", name=None)
        
        logger.debug(f"User '{user.user_name}' is active")


# Global auth service instance
auth_service = AuthService()
