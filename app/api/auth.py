import os
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymysql import MySQLError

from app.exceptions.exceptions import ServiceError
from app.middleware.rate_limitting import rate_limit
from app.schema.auth.Token import Token
from app.service.auth.users import authenticate_user
from app.util.token import (create_access_token, create_refresh_token,
                           verify_refresh_token)

router = APIRouter(tags=["Authentication"])

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("access_token_expires_minutes", 30))


@router.post("/token", response_model=Token)
@rate_limit("10/minute")
def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=7)
        access_token = create_access_token(
            data={"sub": user.user_name, "user_type": user.user_type}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": user.user_name, "user_type": user.user_type}, expires_delta=refresh_token_expires
        )
        return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)
    except MySQLError as error:
        # raise HTTPException(status_code=500, detail=error.args)
        raise ServiceError(message=error.args[1], name="Database Error" )

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str):
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_name = payload.get("sub")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_name}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }