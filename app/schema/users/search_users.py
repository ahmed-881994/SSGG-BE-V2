from typing import List

from pydantic import BaseModel, Field


class SearchUsersResponse(BaseModel):
    class User(BaseModel):
        user_id: str = Field(alias="UserID", description="The unique identifier of the user.")
        user_name: str = Field(alias="UserName", description="The name of the user.")
        is_active: int = Field(alias="IsActive", description="Indicates if the user is active.")
        password_reset: int = Field(alias="PasswordReset", description="Indicates if the user has reset their password.")
        user_type: int = Field(alias="UserType", description="The type of the user.")
    users: List[User] = Field(alias="Users", description="A list of users matching the search criteria.")