from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Base repository interface for all entities"""
    
    @abstractmethod
    async def create(self, db: AsyncSession, obj_in: dict, **kwargs) -> T:
        pass
    
    @abstractmethod
    async def get_by_id(self, db: AsyncSession, id: str) -> Optional[T]:
        pass
    
    @abstractmethod
    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[T]:
        pass
    
    @abstractmethod
    async def update(self, db: AsyncSession, id: str, obj_in: dict, **kwargs) -> Optional[T]:
        pass
    
    @abstractmethod
    async def delete(self, db: AsyncSession, id: str, **kwargs) -> bool:
        pass