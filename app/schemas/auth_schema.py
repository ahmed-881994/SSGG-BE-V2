from typing import Optional

from app.schemas.base_schema import BaseSchema


class Token(BaseSchema):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None
    password_reset_required: Optional[bool] = None
