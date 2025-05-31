from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Union
import logging

from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.exc import SQLAlchemyError
from infrastructure.database.models.base import Base

# Define generic type for model
T = TypeVar('T', bound=Base)

class BaseRepo(Generic[T]):
    """
    Base repository for SQLAlchemy models.
    
    Provides common CRUD methods for working with models.
    
    Attributes:
        session (AsyncSession): SQLAlchemy async session for database operations
        model (Type[T]): Model class used by the repository
    """
    model: Type[T] = None
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository with the specified session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session: AsyncSession = session
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def create(self, data: Dict[str, Any]) -> Optional[T]:
        """
        Create a new record in the database.
        
        Args:
            data: Dictionary with data for object creation
            
        Returns:
            Created object or None in case of error
        """
        try:
            obj = self.model(**data)
            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating {self.model.__name__}: {e}")
            await self.session.rollback()
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error creating {self.model.__name__}: {e}")
            await self.session.rollback()
            return None
    
    async def get_by_id(self, id_value: Any) -> Optional[T]:
        """
        Get object by ID.
        
        Args:
            id_value: ID value
            
        Returns:
            Found object or None if not found
        """
        try:
            # Get the primary key column name
            pk_name = self.model.__table__.primary_key.columns.keys()[0]
            stmt = select(self.model).where(getattr(self.model, pk_name) == id_value)
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving {self.model.__name__} by ID {id_value}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving {self.model.__name__} by ID {id_value}: {e}")
            return None
    
    async def get_all(self, 
                     conditions: Optional[List[BinaryExpression]] = None, 
                     order_by: Optional[Union[str, List[str]]] = None,
                     limit: Optional[int] = None,
                     offset: Optional[int] = None) -> List[T]:
        """
        Get all records with optional filtering and sorting.
        
        Args:
            conditions: List of filter conditions
            order_by: Fields for sorting
            limit: Limit the number of returned records
            offset: Number of records to skip
            
        Returns:
            List of found objects
        """
        try:
            stmt = select(self.model)
            
            # Apply conditions
            if conditions:
                for condition in conditions:
                    stmt = stmt.where(condition)
            
            # Apply sorting
            if order_by:
                if isinstance(order_by, str):
                    order_by = [order_by]
                for field in order_by:
                    # Determine sort direction
                    if field.startswith('-'):
                        # Descending sort
                        stmt = stmt.order_by(getattr(self.model, field[1:]).desc())
                    else:
                        # Ascending sort
                        stmt = stmt.order_by(getattr(self.model, field).asc())
            
            # Apply limit
            if limit is not None:
                stmt = stmt.limit(limit)
                
            # Apply offset
            if offset is not None:
                stmt = stmt.offset(offset)
                
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving all {self.model.__name__}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving all {self.model.__name__}: {e}")
            return []
    
    async def update(self, id_value: Any, data: Dict[str, Any]) -> Optional[T]:
        """
        Update record by ID.
        
        Args:
            id_value: ID value
            data: Dictionary with fields to update
            
        Returns:
            Updated object or None in case of error
        """
        try:
            # Get the primary key column name
            pk_name = self.model.__table__.primary_key.columns.keys()[0]
            
            # Update record
            stmt = (
                update(self.model)
                .where(getattr(self.model, pk_name) == id_value)
                .values(**data)
                .returning(self.model)
            )
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.scalars().first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error updating {self.model.__name__} with ID {id_value}: {e}")
            await self.session.rollback()
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error updating {self.model.__name__} with ID {id_value}: {e}")
            await self.session.rollback()
            return None
    
    async def update_field(self, id_value: Any, field_name: str, field_value: Any) -> bool:
        """
        Update a single field of a record by ID.
        
        Args:
            id_value: ID value
            field_name: Field name to update
            field_value: New field value
            
        Returns:
            True if update was successful, otherwise False
        """
        try:
            # Get the primary key column name
            pk_name = self.model.__table__.primary_key.columns.keys()[0]
            
            # Update field
            stmt = (
                update(self.model)
                .where(getattr(self.model, pk_name) == id_value)
                .values({field_name: field_value})
            )
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.logger.error(f"Error updating field {field_name} of {self.model.__name__} with ID {id_value}: {e}")
            await self.session.rollback()
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error updating field {field_name} of {self.model.__name__} with ID {id_value}: {e}")
            await self.session.rollback()
            return False
    
    async def delete(self, id_value: Any) -> bool:
        """
        Delete record by ID.
        
        Args:
            id_value: ID value
            
        Returns:
            True if deletion was successful, otherwise False
        """
        try:
            # Get the primary key column name
            pk_name = self.model.__table__.primary_key.columns.keys()[0]
            
            # Delete record
            stmt = delete(self.model).where(getattr(self.model, pk_name) == id_value)
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.logger.error(f"Error deleting {self.model.__name__} with ID {id_value}: {e}")
            await self.session.rollback()
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error deleting {self.model.__name__} with ID {id_value}: {e}")
            await self.session.rollback()
            return False
            
    async def exists(self, id_value: Any) -> bool:
        """
        Check if a record with the given ID exists.
        
        Args:
            id_value: ID value
            
        Returns:
            True if record exists, otherwise False
        """
        try:
            # Get the primary key column name
            pk_name = self.model.__table__.primary_key.columns.keys()[0]
            
            # Create query to check existence
            stmt = select(1).where(getattr(self.model, pk_name) == id_value).exists().select()
            
            result = await self.session.execute(stmt)
            return result.scalar()
        except Exception as e:
            self.logger.error(f"Error checking existence of {self.model.__name__} with ID {id_value}: {e}")
            return False
