from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class EntityType(Base):
    __tablename__ = "entity_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    entity_type_name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type_name_ar: Mapped[str] = mapped_column(String(100), nullable=True)
    entities: Mapped[list["Entity"]] = relationship("Entity", back_populates="entity_type")

    
    def __repr__(self):
        return f"<EntityType(entity_type_id={self.entity_type_id}, entity_type_name_en={self.entity_type_name_en}, entity_type_name_ar={self.entity_type_name_ar})>"

    def to_dict(self):
        return {
            "entity_type_id": self.entity_type_id,
            "entity_type_name_en": self.entity_type_name_en,
            "entity_type_name_ar": self.entity_type_name_ar,
        }