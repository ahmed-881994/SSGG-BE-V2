"""
Base repository class providing common CRUD operations.

This module defines a generic repository base class that can be extended
by specific repositories to provide common database operations.
"""

from abc import ABC
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session

# Generic type variable for model classes
T = TypeVar('T')

class BaseRepository(Generic[T], ABC):
    """
    Abstract base repository class providing common CRUD operations.
    
    This class provides a foundation for all repository classes with:
    - Generic type support for any SQLAlchemy model
    - Common CRUD operations (Create, Read, Update, Delete)
    - Session management integration
    - Type safety through generics
    
    Usage:
        class MemberRepository(BaseRepository[Member]):
            def __init__(self, db: Session):
                super().__init__(db, Member)
    """
    
    def __init__(self, db: Session, model: Type[T]):
        """
        Initialize the repository with database session and model class.
        
        Args:
            db: SQLAlchemy database session
            model: SQLAlchemy model class (e.g., Member, Entity)
        """
        self.db = db
        self.model = model
    
    def get_by_id(self, entity_id: Any) -> Optional[T]:
        """
        Get entity by primary key.
        
        Args:
            entity_id: Primary key value
            
        Returns:
            Model instance if found, None otherwise
        """
        return self.db.query(self.model).get(entity_id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Get all entities with pagination.
        
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of model instances
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, entity: T) -> T:
        """
        Create new entity in the database.
        
        Args:
            entity: Model instance to create
            
        Returns:
            Created model instance with updated fields (like auto-generated IDs)
        """
        self.db.add(entity)          # Add to session
        self.db.commit()             # Commit transaction
        self.db.refresh(entity)      # Refresh to get updated fields
        return entity
    
    def update(self, entity: T) -> T:
        """
        Update existing entity in the database.
        
        Args:
            entity: Model instance with updated values
            
        Returns:
            Updated model instance
        """
        self.db.commit()             # Commit changes
        self.db.refresh(entity)      # Refresh to get updated fields
        return entity
    
    def delete(self, entity: T) -> bool:
        """
        Delete entity from the database.
        
        Args:
            entity: Model instance to delete
            
        Returns:
            True if deletion was successful
        """
        self.db.delete(entity)       # Mark for deletion
        self.db.commit()             # Commit transaction
        return True
    
    def count(self) -> int:
        """
        Count total number of entities.
        
        Returns:
            Total count of records
        """
        return self.db.query(self.model).count()
