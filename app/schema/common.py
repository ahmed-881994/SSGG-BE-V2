from typing import Optional
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str
    
class SuccessResponse(BaseModel):
    message: str