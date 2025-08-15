

from typing import Literal
from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    user_id: str = Field(..., alias="UserID", description="The ID of the user.")
    user_name: str = Field(..., alias="UserName", description="The username of the user.")
    user_type: Literal[1, 2, 3, 4, 5, 6, 7] = Field(..., alias="UserType", description="The type of the user. 1= Super user, 2= General Leader, 3= ")
    password: str = Field(..., alias="Password", description="The password for the user.")
