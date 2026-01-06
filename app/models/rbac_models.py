from datetime import datetime
from typing import List, Optional

from sqlalchemy import (Boolean, DateTime, ForeignKey, String, Text,
                        UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base


class RoutePattern(Base):
    __tablename__ = "route_patterns"

    id: Mapped[int] = mapped_column(primary_key=True)
    route_pattern_id: Mapped[int] = mapped_column(nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    path_pattern: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission", 
        secondary="route_permissions", 
        back_populates="route_patterns",
        lazy="select"
    )

class RoutePermission(Base):
    __tablename__ = "route_permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    route_pattern_id: Mapped[int] = mapped_column(ForeignKey("route_patterns.route_pattern_id", ondelete="CASCADE"))
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.permission_id", ondelete="CASCADE"))
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint('route_pattern_id', 'permission_id'),)

    # Relationships
    # route_patterns: Mapped["RoutePattern"] = relationship("RoutePattern", back_populates="permissions")
    # permission: Mapped["Permission"] = relationship("Permission", back_populates="route_patterns")

class PublicRoute(Base):
    __tablename__ = "public_routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    path_pattern_id: Mapped[int] = mapped_column(nullable=False)
    path_pattern: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_regex: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)