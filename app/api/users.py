from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pymysql import MySQLError
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import get_user_in_token
from app.core.exceptions import (EntityAlreadyExistsError,
                                 EntityDoesNotExistError, ServiceError)
from app.schemas.common_schema import SuccessResponse
from app.schemas.users_schema import UserCreate, UserResponse, UserSearchResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users", tags=["Users"], dependencies=[Depends(get_user_in_token)])


@router.get("", response_model=UserSearchResponse)
def search_users(userName: Optional[str] = None, userID: Optional[str] = None, db: Session = Depends(get_db_session)):
    """Search for users by Name or ID.
    Note: Not sending any of the criteria returns all users.
    """
    try:
        user_service = UserService(db)
        return user_service.search_users(user_name=userName, user_id=userID)

    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("", status_code=201, response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db_session)):
    """Create a new user."""
    try:
        user_service = UserService(db)
        return user_service.create_user(user_data=user.model_dump())
    except EntityAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.patch("/{id}")
def update_user(id: int, user: UserUpdate, db: Session = Depends(get_db_session)):
    """Update an existing user."""
    try:
        user_service = UserService(db)
        return user_service.update_user(id=id, **user.model_dump())
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.delete("/{id}")
def delete_user(id: int, db: Session = Depends(get_db_session)):
    """Delete an existing user."""
    try:
        user_service = UserService(db)
        return user_service.delete_user(id=id)
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/{id}")
def get_user(id: int, db: Session = Depends(get_db_session)):
    """Get details of an existing user."""
    try:
        user_service = UserService(db)
        return user_service.get_user_by_id(id)
        
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
