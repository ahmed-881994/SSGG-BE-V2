from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base


class EntityMember(Base):
    __tablename__ = "entity_members"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to entities table
    # Links this membership to a specific entity
    entity_id: Mapped[int] = mapped_column(Integer, ForeignKey("entities.entity_id"))

    # Foreign key to members table
    # Links this membership to a specific member
    member_id: Mapped[str] = mapped_column(String(50), ForeignKey("members.member_id"))
    
    # Foreign key to entity_roles table
    # Defines what role the member has in this entity
    member_entity_role_id: Mapped[int] = mapped_column(Integer, ForeignKey("entity_roles.id"))
    
    # Membership period tracking
    date_from: Mapped[Date] = mapped_column(Date)  # When the membership started
    date_to: Mapped[Date] = mapped_column(Date)    # When the membership ended (NULL for active memberships)


    # Relationships to related tables
    
    # Many-to-one relationship to Entity
    # Each membership record belongs to one entity
    entity = relationship("Entity", back_populates="entity_members")
    
    # Many-to-one relationship to Member
    # Each membership record belongs to one member
    member = relationship("Member", back_populates="entity_memberships")
    
    # Many-to-one relationship to EntityRole
    # Each membership has one role
    role = relationship("EntityRole", back_populates="entity_members")
    
    def __repr__(self):
        return f"<EntityMember(entity_id={self.entity_id}, member_id={self.member_id}, role_id={self.member_entity_role_id}, date_from={self.date_from}, date_to={self.date_to})>"
    
    def to_dict(self) -> dict:
        """
        Convert EntityMember to a dictionary representation.
        """
        return {
            "entity_id": self.entity_id,
            "member_id": self.member_id,
            "member_entity_role_id": self.member_entity_role_id,
            "date_from": self.date_from,
            "date_to": self.date_to
        }