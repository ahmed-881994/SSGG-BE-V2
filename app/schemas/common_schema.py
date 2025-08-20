from typing import Optional

from pydantic import Field
from app.schemas.base_schema import BaseSchema


class SuccessResponse(BaseSchema):
    message: str

class ErrorResponse(BaseSchema):
    detail: str

class NameObject(BaseSchema):
    en: Optional[str] = Field(alias='EN', default=None)
    ar: Optional[str] = Field(alias='AR', default=None)