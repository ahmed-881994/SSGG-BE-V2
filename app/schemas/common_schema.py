from app.schemas.base_schema import BaseSchema


class SuccessResponse(BaseSchema):
    message: str

class ErrorResponse(BaseSchema):
    detail: str