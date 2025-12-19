
from typing import Optional

from pydantic import Field

from app.schemas.base_schema import BaseSchema


# Requests
class UserCreate(BaseSchema):
    user_name: str = Field(alias="UserName")
    user_id: str = Field(alias="UserID")
    role_id: int = Field(alias="RoleID")
    password: str = Field(alias="Password")
    is_active: bool = Field(alias="IsActive", default=True)
    password_reset: bool = Field(alias="PasswordReset", default=False)

class UserUpdate(BaseSchema):
    user_name: Optional[str] = Field(alias="UserName", default=None)
    role_id: Optional[int] = Field(alias="RoleID", default=0)
    is_active: Optional[bool] = Field(alias="IsActive", default=True)
    password_reset: Optional[bool] = Field(alias="PasswordReset", default=False)
    
class UserUpdatePassword(BaseSchema):
    old_password: str = Field(alias="OldPassword")
    new_password: str = Field(alias="NewPassword")

# Responses

class UserResponse(BaseSchema):
    user_name: str = Field(alias="UserName")
    user_id: str = Field(alias="UserID")
    role_id: int = Field(alias="RoleID")
    is_active: bool = Field(alias="IsActive")
    password_reset: bool = Field(alias="PasswordReset")
    
    
class UserSearchResponse(BaseSchema):
    users: list[UserResponse] = Field(alias="Users")
