import os
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.schema.auth.user import User
from app.util.auth import verify_password
from app.util.database import connect

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(username: str, password: str):
    user = get_user_by_id_db(username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def get_user_by_id_db(user_name: str):
    conn = connect()
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
    SECRET_KEY = os.environ.get("secret_key")
    ALGORITHM = os.environ.get("algorithm")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_name = payload.get("sub")

    if user_name is None:
        raise credentials_exception
    return get_user_by_id_db(user_name)


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.is_active == 0:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
