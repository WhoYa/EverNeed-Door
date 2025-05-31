"""
Base repository with common error handling and database operations
"""
import logging
from typing import Generic, TypeVar, List, Optional, Dict, Any, Type, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.exc import SQLAlchemyError

# Avoid circular imports by importing the error classes directly
from tgbot.utils.error_handling import (
    safe_db_operation,
    RepositoryError,
    NotFoundError,
    ValidationError,
    DatabaseError
)

T = TypeVar('T')
logger = logging.getLogger(__name__)

class BaseRepository(Generic[T]):
    """
    Base repository class with common CRUD operations and standardized error handling
    """
    
    def __init__(self, session: AsyncSession, model_class: Type[T]):
        """
        Initialize repository with session and model class
        
        Args:
            session: SQLAlchemy async session
            model_class: Model class for this repository
        """
        self.session = session
        self.model_class = model_class
    
    @safe_db_operation("Failed to get all records")
    async def get_all(self) -> List[T]:
        """
        Get all records of the model
        
        Returns:
            List of model instances
        """
        query = select(self.model_class)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    @safe_db_operation("Failed to get record by ID")
    async def get_by_id(self, id_value: Any) -> Optional[T]:
        """
        Get record by ID
        
        Args:
            id_value: ID value to search for
            
        Returns:
            Model instance or None if not found
        """
        query = select(self.model_class).filter_by(id=id_value)
        result = await self.session.execute(query)
        instance = result.scalars().first()
        
        if not instance:
            raise NotFoundError(f"Record with ID {id_value} not found")
            
        return instance
    
    @safe_db_operation("Failed to create record")
    async def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new record
        
        Args:
            data: Dictionary of field values
            
        Returns:
            Created model instance
        """
        try:
            instance = self.model_class(**data)
            self.session.add(instance)
            await self.session.commit()
            await self.session.refresh(instance)
            return instance
        except ValueError as e:
            # Handle validation errors
            raise ValidationError(f"Invalid data for {self.model_class.__name__}", str(e))
    
    @safe_db_operation("Failed to update record")
    async def update(self, id_value: Any, data: Dict[str, Any]) -> bool:
        """
        Update a record by ID
        
        Args:
            id_value: ID value to update
            data: Dictionary of field values to update
            
        Returns:
            True if updated successfully
        """
        # Verify record exists
        instance = await self.get_by_id(id_value)
        if not instance:
            return False
            
        # Update record
        query = update(self.model_class).where(self.model_class.id == id_value).values(**data)
        await self.session.execute(query)
        await self.session.commit()
        return True
    
    @safe_db_operation("Failed to delete record")
    async def delete(self, id_value: Any) -> bool:
        """
        Delete a record by ID
        
        Args:
            id_value: ID value to delete
            
        Returns:
            True if deleted successfully
        """
        # Verify record exists
        instance = await self.get_by_id(id_value)
        if not instance:
            return False
            
        # Delete record
        query = delete(self.model_class).where(self.model_class.id == id_value)
        await self.session.execute(query)
        await self.session.commit()
        return True
    
    async def safe_rollback(self) -> None:
        """
        Safely rolls back the session in case of errors
        """
        try:
            await self.session.rollback()
        except Exception as e:
            logger.error(f"Error during session rollback: {e}")
            
    # Common filter operations
    @safe_db_operation("Failed to filter records")
    async def filter_by(self, **kwargs: Any) -> List[T]:
        """
        Filter records by attributes
        
        Args:
            **kwargs: Field value pairs to filter by
            
        Returns:
            List of matching model instances
        """
        query = select(self.model_class).filter_by(**kwargs)
        result = await self.session.execute(query)
        return result.scalars().all()
        
    @safe_db_operation("Failed to count records")
    async def count(self, **kwargs: Any) -> int:
        """
        Count records matching filter criteria
        
        Args:
            **kwargs: Field value pairs to filter by
            
        Returns:
            Count of matching records
        """
        from sqlalchemy import func
        query = select(func.count()).select_from(self.model_class)
        
        if kwargs:
            query = query.filter_by(**kwargs)
            
        result = await self.session.execute(query)
        return result.scalar() or 0