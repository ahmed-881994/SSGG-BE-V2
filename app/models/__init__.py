"""
Models package initialization.

This module imports and exposes all SQLAlchemy models for the application.
Having all models imported here ensures they are registered with SQLAlchemy
and available for relationship resolution.
"""

# Import the base class first
from .base import Base

# Import all model classes
# Order matters for relationship resolution
# from .user_type import UserType
from .user import User
# from .event_type import EventType
# from .event import Event
from .entity_type import EntityType
from .entity_role import EntityRole  
from .entity import Entity
from .member import Member
from .entity_member import EntityMember
# from .attendance_state import AttendanceState
# from .attendance import Attendance

# Export all models for easy importing
# This allows other modules to import all models with:
# from app.models import Base, Member, Entity, etc.
__all__ = [
    "Base",           # Base class for all models
    # "UserType",       # User type classifications
    "User",           # System users  
    # "EventType",      # Event type classifications
    # "Event",          # Events and activities
    "EntityType",     # Entity type classifications
    "EntityRole",     # Roles within entities
    "Entity",         # Organizational units
    "Member",         # Member information
    "EntityMember",   # Entity-member relationships
    # "AttendanceState", # Attendance status types
    # "Attendance"      # Attendance records
]
