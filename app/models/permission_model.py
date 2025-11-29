from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

# from app.models.rbac_models import RoutePattern
# from app.models.role_model import Role

from .base_model import Base


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role", 
        secondary="role_permissions", 
        back_populates="permissions",
        lazy='select'
    )
    
    route_patterns: Mapped[List["RoutePattern"]] = relationship(
        "RoutePattern", 
        secondary="route_permissions", 
        back_populates="permissions"
    )
    
    # Add this new relationship to access the association table
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan"
    )