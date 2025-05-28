from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.repositories.base_repository import BaseRepository
from app.db.models import scan as Scan
from app.schemas.scan import ScanCreate, ScanUpdate

class ScanRepository(BaseRepository[Scan]):
    """Repository for Scan entity operations"""
    
    async def create(self, db: AsyncSession, obj_in: ScanCreate, **kwargs) -> Scan:
        """Create a new scan"""
        scan_data = obj_in.model_dump()
        scan_data.update(kwargs)
        
        scan = Scan(**scan_data)
        db.add(scan)
        await db.commit()
        await db.refresh(scan)
        return scan
    
    async def get_by_id(self, db: AsyncSession, id: str) -> Optional[Scan]:
        """Get scan by ID"""
        result = await db.execute(
            select(Scan).where(Scan.id == id, Scan.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def get_by_domain(self, db: AsyncSession, domain: str) -> List[Scan]:
        """Get scans by domain"""
        result = await db.execute(
            select(Scan)
            .where(Scan.domain == domain, Scan.is_active == True)
            .order_by(Scan.created_date.desc())
        )
        return result.scalars().all()
    
    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Scan]:
        """Get all active scans"""
        result = await db.execute(
            select(Scan)
            .where(Scan.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(Scan.created_date.desc())
        )
        return result.scalars().all()
    
    async def update(self, db: AsyncSession, id: str, obj_in: dict, **kwargs) -> Optional[Scan]:
        """Update scan"""
        update_data = obj_in.copy()
        update_data.update(kwargs)
        
        await db.execute(
            update(Scan)
            .where(Scan.id == id)
            .values(**update_data)
        )
        await db.commit()
        return await self.get_by_id(db, id)
    
    async def delete(self, db: AsyncSession, id: str, **kwargs) -> bool:
        """Soft delete scan"""
        deleted_by = kwargs.get('deleted_by', 'system')
        
        result = await db.execute(
            update(Scan)
            .where(Scan.id == id)
            .values(is_active=False, updated_by=deleted_by)
        )
        await db.commit()
        return result.rowcount > 0

# Create instance
scan_repository = ScanRepository()