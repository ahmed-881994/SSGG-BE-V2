from pydantic import BaseModel


class User(BaseModel):
    user_name: str
    password_hash: str
    is_active: int
    password_reset:int