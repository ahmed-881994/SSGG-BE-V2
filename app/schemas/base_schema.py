from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database operations."""
        return self.model_dump(by_alias=False, exclude_none=True)
    
    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses using aliases."""
        return self.model_dump(by_alias=True, exclude_none=True)


class AuditableSchema(BaseSchema):
    """Base schema with timestamp and audit fields."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None