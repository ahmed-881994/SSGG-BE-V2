
from typing import Optional

from pydantic import Field

from app.schemas.base_schema import BaseSchema


# Requests
class UserCreate(BaseSchema):
    user_name: str = Field(alias="UserName")
    user_id: str = Field(alias="UserID")
    # user_type: int = Field(alias="UserType", ge=1, le=3)
    password: str = Field(alias="Password")
    is_active: bool = Field(alias="IsActive", default=True)
    password_reset: bool = Field(alias="PasswordReset", default=False)

class UserUpdate(BaseSchema):
    user_name: Optional[str] = Field(alias="UserName")
    # user_type: int = Field(alias="UserType", ge=1, le=3)
    is_active: Optional[bool] = Field(alias="IsActive", default=True)
    password_reset: Optional[bool] = Field(alias="PasswordReset", default=False)
    
class UserUpdatePassword(BaseSchema):
    old_password: str = Field(alias="OldPassword")
    new_password: str = Field(alias="NewPassword")

# Responses

class UserResponse(BaseSchema):
    user_name: str = Field(alias="UserName")
    user_id: str = Field(alias="UserID")
    # user_type: int = Field(alias="UserType")
    is_active: bool = Field(alias="IsActive")
    password_reset: bool = Field(alias="PasswordReset")
    
    
class UserSearchResponse(BaseSchema):
    users: list[UserResponse] = Field(alias="Users")
