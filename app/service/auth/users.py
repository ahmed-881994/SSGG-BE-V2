from datetime import datetime, timezone
import os
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.config.settings import settings
from app.exceptions.exceptions import AuthenticationFailed, InvalidTokenError
from app.schema.users.user import User
from app.util.token import verify_password
from app.util.database import get_connection
from app.util.token_blacklist import token_blacklist

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(username: str, password: str):
    user = get_user_by_id_db(username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def get_user_by_id_db(user_name: str):
    conn = get_connection()
    if conn is not None:
        with conn as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE user_name = %s", (user_name,))
            user_data = cursor.fetchone()
            user = User(**user_data) if user_data else None
            if user is None:
                return None
            return user


def get_current_user(token: str = Depends(oauth2_scheme)):
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm

    try:
        # Check if token is blacklisted
        if token_blacklist.is_blacklisted(token):
            raise InvalidTokenError(message="Token has been revoked", name=None)
        
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.now(timezone.utc).timestamp() > exp:
            raise InvalidTokenError(message="Token has expired", name=None)
        
        user_name = payload.get("sub")
        if user_name is None:
            raise AuthenticationFailed(message="Invalid credentials", name=None)
        
        return get_user_by_id_db(user_name)
    except jwt.PyJWTError:
        raise InvalidTokenError(message="Invalid token", name=None)
    # try:
    #     # Decode the JWT token
    #     payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # except jwt.PyJWTError:
    #     raise InvalidTokenError(message= "Invalid token", name=None)
    # # payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # user_name = payload.get("sub")

    # if user_name is None:
    #     raise AuthenticationFailed(message="Invalid credentials", name=None)
    # return get_user_by_id_db(user_name)


async def login_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.is_active == 0:
        # raise HTTPException(status_code=400, detail="Inactive user")
        raise AuthenticationFailed(message="User is not active", name=None)
    return current_user

def logout_user(token: str) -> bool:
    """
    Blacklist the given JWT token until its expiration.
    Returns True if successful, False if the token is invalid.
    """
    try:
        # Decode the token to get its expiration
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        exp_timestamp = payload.get("exp")
        if not exp_timestamp:
            return False
        expires_at = datetime.fromtimestamp(exp_timestamp, timezone.utc)
        token_blacklist.add_to_blacklist(token, expires_at)
        return True
    except jwt.PyJWTError:
        return False