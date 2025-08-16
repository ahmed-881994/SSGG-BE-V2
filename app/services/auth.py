"""
Authentication services for user login, validation, and token management
"""
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from pymysql import MySQLError
from pydantic import BaseModel

from app.core.config import settings, logger
from app.core.database import get_connection
from app.core.exceptions import AuthenticationFailed, ServiceError
from app.core.database_connection_pool import db_pool
from app.util.token_blacklist import token_blacklist
from app.util.password import verify_password


class AuthUser(BaseModel):
    """User model for authentication with password hash"""
    user_id: str
    user_name: str
    password_hash: str
    salt: str
    is_active: bool
    user_type: str


class AuthService:
    """Authentication service for user authentication and validation"""
    
    def authenticate_user(self, username: str, password: str) -> Optional[AuthUser]:
        """
        Authenticate user with username and password
        
        Args:
            username: User's username or email
            password: Plain text password
            
        Returns:
            AuthUser object if authentication successful, None otherwise
            
        Raises:
            AuthenticationFailed: If authentication fails
            ServiceError: If database error occurs
        """
        try:
            # Get user from database
            user = self._get_user_by_username(username)
            if not user:
                logger.warning(f"Authentication failed: User '{username}' not found")
                raise AuthenticationFailed("Invalid username or password")
            
            # Verify password using our custom password verification
            if not verify_password(password, user.password_hash, user.salt):
                logger.warning(f"Authentication failed: Invalid password for user '{username}'")
                raise AuthenticationFailed("Invalid username or password")
            
            logger.info(f"User '{username}' authenticated successfully")
            return user
            
        except MySQLError as e:
            logger.error(f"Database error during authentication for user '{username}': {e}")
            raise ServiceError("Database error during authentication", "DatabaseError")
        except Exception as e:
            logger.error(f"Unexpected error during authentication for user '{username}': {e}")
            raise AuthenticationFailed("Authentication failed")
    
    def validate_user_active(self, user: AuthUser) -> None:
        """
        Validate that user account is active
        
        Args:
            user: AuthUser object to validate
            
        Raises:
            AuthenticationFailed: If user is inactive
        """
        if not user.is_active:
            logger.warning(f"Authentication failed: User '{user.user_name}' is inactive")
            raise AuthenticationFailed("User account is inactive")
    
    def _get_user_by_username(self, username: str) -> Optional[AuthUser]:
        """Get user from database by username or email"""
        conn = db_pool.get_connection()
        
        try:
            with conn.cursor() as cursor:
                # Try to find user by username or email
                query = """
                SELECT user_id, user_name, password_hash, salt, is_active, user_type
                FROM users
                WHERE user_name = %s OR user_id = %s
                """
                cursor.execute(query, (username, username))
                result = cursor.fetchone()
                
                if result:
                    return AuthUser(
                        user_id=result['user_id'],
                        user_name=result['user_name'],
                        password_hash=result['password_hash'],
                        salt=result['salt'],
                        is_active=bool(result['is_active']),
                        user_type=result['user_type'],
                    )
                
                return None
                
        finally:
            db_pool.return_connection(conn)


class TokenService:
    """Token service for JWT token management"""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expires_minutes
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token
        
        Args:
            data: Token payload data
            expires_delta: Token expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow()
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        logger.debug(f"Created access token for user: {data.get('sub')}")
        
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT refresh token
        
        Args:
            data: Token payload data
            expires_delta: Token expiration time
            
        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow()
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        logger.debug(f"Created refresh token for user: {data.get('sub')}")
        
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            token_type: Expected token type ('access' or 'refresh')
            
        Returns:
            Decoded token payload
            
        Raises:
            jwt.InvalidTokenError: If token is invalid
        """
        try:
            # Check if token is blacklisted
            if token_blacklist.is_blacklisted(token):
                logger.warning("Token verification failed: Token is blacklisted")
                raise jwt.InvalidTokenError("Token is blacklisted")
            
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != token_type:
                logger.warning(f"Token verification failed: Expected {token_type} token, got {payload.get('type')}")
                raise jwt.InvalidTokenError(f"Invalid token type")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token verification failed: Token has expired")
            raise jwt.InvalidTokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {str(e)}")
            raise jwt.InvalidTokenError("Token verification failed")
    
    def blacklist_token(self, token: str) -> bool:
        """
        Add token to blacklist
        
        Args:
            token: JWT token to blacklist
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify token format and get expiration
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            exp = payload.get("exp")
            
            if exp:
                # Add to blacklist with expiration time
                exp_datetime = datetime.fromtimestamp(exp)
                token_blacklist.add_to_blacklist(token, exp_datetime)
                logger.info("Token successfully blacklisted")
                return True
            else:
                logger.warning("Cannot blacklist token: No expiration time found")
                return False
                
        except jwt.InvalidTokenError:
            logger.warning("Cannot blacklist invalid token")
            return False
        except Exception as e:
            logger.error(f"Error blacklisting token: {str(e)}")
            return False


# Global service instances
auth_service = AuthService()
token_service = TokenService()