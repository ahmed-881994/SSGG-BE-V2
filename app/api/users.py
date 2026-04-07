from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import get_user_in_token
from app.core.exceptions import (AuthorizationError, EntityAlreadyExistsError,
                                 EntityDoesNotExistError, ServiceError)
from app.schemas.common_schema import SuccessResponse
from app.schemas.users_schema import (UserCreate, UserResponse,
                                      UserSearchResponse, UserUpdate,
                                      UserUpdatePassword)
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


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user: UserUpdate, db: Session = Depends(get_db_session)):
    """Update an existing user."""
    try:
        user_service = UserService(db)
        return user_service.update_user(user_id=user_id, **user.model_dump(exclude_none=True))
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db_session)):
    """Delete an existing user."""
    try:
        user_service = UserService(db)
        return user_service.delete_user(user_id=user_id)
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db_session)):
    """Get details of an existing user."""
    try:
        user_service = UserService(db)
        return user_service.get_user_by_user_id(user_id)
        
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@router.patch("/{user_id}/password", response_model=SuccessResponse)
def update_user_password(request: Request, user_id: str, password_data: UserUpdatePassword, db: Session = Depends(get_db_session)):
    """Update a user's password."""
    try:
        if request.state.member_id != user_id:
            raise AuthorizationError("You can only update your own password")
        user_service = UserService(db)
        user_service.update_user_password(user_id=user_id, **password_data.model_dump())
        return {"message": "Password updated successfully"}
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AuthorizationError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/{user_id}/reset-password", response_model=SuccessResponse)
def reset_user_password(user_id: str, db: Session = Depends(get_db_session)):
    """Reset a user's password."""
    try:
        user_service = UserService(db)
        user_service.reset_user_password(user_id=user_id)
        return {"message": "Password reset email sent"}
    except EntityDoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
