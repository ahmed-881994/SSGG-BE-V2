from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class EntityRole(Base):
    __tablename__ = "entity_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Role names in English and Arabic
    entity_role_name_en: Mapped[str] = mapped_column(String(255))  # English role name (e.g., "Leader")
    entity_role_name_ar: Mapped[str] = mapped_column(String(255))  # Arabic role name (e.g., "قائد")

    # Reverse relationship to entity members
    # This allows querying all members with a specific role
    entity_members = relationship("EntityMember", back_populates="role")