from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    entity_name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_name_ar: Mapped[str] = mapped_column(String(100), nullable=True)
    entity_parent_id: Mapped[int] = mapped_column(ForeignKey("entities.entity_id"), nullable=True)
    entity_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("entity_types.entity_type_id"), nullable=False)    
    
    # Relationships
    # These define how this table relates to other entities in the database
    # Each Entity belongs to one EntityType
    entity_type: Mapped["EntityType"] = relationship("EntityType", back_populates="entities")
    # Each Entity can have multiple child Entities
    children: Mapped[list["Entity"]] = relationship(
        "Entity", 
        back_populates="parent",
        foreign_keys=[entity_parent_id]
    )
    # Each Entity can have one parent Entity
    parent: Mapped["Entity"] = relationship(
        "Entity", 
        back_populates="children", 
        remote_side=[entity_id]  # This is the parent entity in the relationship
    )
    # Each Entity can have multiple Members
    members: Mapped[list["EntityMember"]] = relationship("EntityMember", back_populates="entity")

    def __repr__(self):
        return f"<Entity(entity_name_en={self.entity_name_en}, entity_name_ar={self.entity_name_ar}, entity_parent_id={self.entity_parent_id}, entity_type={self.entity_type})>"

    def to_dict(self, include_relationships=False, include_members=False) -> dict:
        """
        Convert entity to dictionary.
        
        Args:
            include_relationships: If True, includes parent/children relationships.
                                 If False, only includes basic entity info to avoid recursion.
        """
        entity_dict = {
            "entity_id": self.entity_id,
            "entity_name_en": self.entity_name_en,
            "entity_name_ar": self.entity_name_ar,
            "entity_parent_id": self.entity_parent_id,
            "entity_type": self.entity_type.to_dict() if self.entity_type else None,
        }
        if include_relationships:
            entity_dict.update({
                "children": [child.to_dict(include_relationships=False) for child in self.children] if self.children else [],
                "parent": self.parent.to_dict(include_relationships=False) if self.parent else None
            })

        if include_members:
            entity_dict["members"] = [member.to_dict_brief() for member in self.members] if self.members else []

        return entity_dict