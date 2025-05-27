
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_, desc, asc
from app.db.models.scan import Scan
from app.schemas.scan import ScanCreate, ScanUpdate, ScanOut
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


async def get_scan_by_id(db: AsyncSession, scan_id: str) -> Optional[Scan]:
    """
    Retrieves a single scan from the database by its ID.
    """
    
    result = await db.execute(select(Scan).filter(Scan.id == scan_id))
    return result.scalars().first()


async def get_scans_by_domain(db: AsyncSession, domain: str, skip: int = 0, limit: int = 100) -> List[Scan]:
    """
    Retrieves scans for a specific domain with pagination.
    """
    result = await db.execute(
        select(Scan)
        .filter(Scan.domain == domain, Scan.is_active == True)
        .order_by(desc(Scan.created_date))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_scans_by_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[Scan]:
    """
    Retrieves scans created by a specific user with pagination.
    """
    result = await db.execute(
        select(Scan)
        .filter(Scan.user_id == user_id, Scan.is_active == True)
        .order_by(desc(Scan.created_date))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_scans(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    domain: Optional[str] = None,
    user_id: Optional[int] = None,
    is_public: Optional[bool] = None,
    order_by: str = "created_date",
    order_direction: str = "desc"
) -> List[Scan]:
    """
    Retrieves a list of scans from the database with filtering and pagination.
    """
    query = select(Scan).filter(Scan.is_active == True)
    
    
    if status:
        query = query.filter(Scan.status == status)
    if domain:
        query = query.filter(Scan.domain.ilike(f"%{domain}%"))
    if user_id:
        query = query.filter(Scan.user_id == user_id)
    if is_public is not None:
        query = query.filter(Scan.is_public == is_public)
    
    
    order_column = getattr(Scan, order_by, Scan.created_date)
    if order_direction.lower() == "desc":
        query = query.order_by(desc(order_column))
    else:
        query = query.order_by(asc(order_column))
    
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_scan(db: AsyncSession, scan: ScanCreate, created_by: Optional[str] = None) -> Scan:
    """
    Creates a new scan record in the database.
    """
    db_scan = Scan(
        domain=scan.domain,
        status="pending",
        tools_enabled=scan.tools_enabled or {"theharvester": True, "amass": True, "subfinder": True},
        scan_options=scan.scan_options,
        user_id=scan.user_id,
        is_public=scan.is_public or False,
        created_by=created_by,
        updated_by=created_by,
    )
    db.add(db_scan)
    await db.commit()
    await db.refresh(db_scan)
    return db_scan


async def update_scan(db: AsyncSession, scan_id: str, scan_update: ScanUpdate, updated_by: Optional[str] = None) -> Optional[Scan]:
    """
    Updates an existing scan's details in the database.
    """
    
    update_data = scan_update.model_dump(exclude_unset=True)
    
    if "started_at" in update_data and "finished_at" in update_data:
        if update_data["started_at"] and update_data["finished_at"]:
            duration = (update_data["finished_at"] - update_data["started_at"]).total_seconds()
            update_data["duration_seconds"] = int(duration)
    
    stmt = (
        update(Scan)
        .where(Scan.id == scan_id)
        .values(
            **update_data,
            updated_by=updated_by,
            updated_date=datetime.now()
        )
    )
    logger.debug(f"update_data: {update_data}")
    await db.execute(stmt)
    await db.commit()
    return await get_scan_by_id(db, scan_id)


async def update_scan_status(
    db: AsyncSession, 
    scan_id: str, 
    status: str, 
    error_message: Optional[str] = None,
    updated_by: Optional[str] = None
) -> Optional[Scan]:
    """
    Updates a scan's status and optionally sets error message.
    """
    update_data = {"status": status, "updated_by": updated_by, "updated_date": datetime.now()}
    
    if status == "running" and not await _scan_has_started_at(db, scan_id):
        update_data["started_at"] = datetime.now()
    elif status in ["finished", "error", "cancelled"]:
        update_data["finished_at"] = datetime.now()
        
        scan = await get_scan_by_id(db, scan_id)
        if scan and scan.started_at:
            duration = (datetime.now() - scan.started_at).total_seconds()
            update_data["duration_seconds"] = int(duration)
    
    if error_message:
        update_data["error_message"] = error_message
    
    stmt = update(Scan).where(Scan.id == scan_id).values(**update_data)
    await db.execute(stmt)
    await db.commit()
    return await get_scan_by_id(db, scan_id)


async def update_scan_results(
    db: AsyncSession,
    scan_id: str,
    theharvester: Optional[Dict[str, Any]] = None,
    amass: Optional[Dict[str, Any]] = None,
    subfinder: Optional[Dict[str, Any]] = None,
    summary: Optional[Dict[str, Any]] = None,
    updated_by: Optional[str] = None
) -> Optional[Scan]:
    """
    Updates scan results and metadata.
    """
    update_data = {"updated_by": updated_by, "updated_date": datetime.now()}
    
    if theharvester is not None:
        update_data["theharvester"] = theharvester

    if amass is not None:
        update_data["amass"] = amass

    if subfinder is not None:
        update_data["subfinder"] = subfinder

    if summary is not None:
        update_data["summary"] = summary
    
    
    stmt = update(Scan).where(Scan.id == scan_id).values(**update_data)
    await db.execute(stmt)
    await db.commit()
    return await get_scan_by_id(db, scan_id)


async def delete_scan(db: AsyncSession, scan_id: str, deleted_by: Optional[str] = None) -> bool:
    """
    Soft deletes a scan by setting is_active to False.
    """
    stmt = (
        update(Scan)
        .where(Scan.id == scan_id)
        .values(
            is_active=False,
            updated_by=deleted_by,
            updated_date=datetime.now()
        )
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def hard_delete_scan(db: AsyncSession, scan_id: str) -> bool:
    """
    Permanently deletes a scan from the database.
    """
    stmt = delete(Scan).where(Scan.id == scan_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def get_scan_stats(db: AsyncSession, user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Retrieves scanning statistics.
    """
    base_query = select(Scan).filter(Scan.is_active == True)
    if user_id:
        base_query = base_query.filter(Scan.user_id == user_id)
    
    
    total_result = await db.execute(select(func.count(Scan.id)).select_from(base_query.subquery()))
    total_scans = total_result.scalar()
    
 
    status_query = (
        select(Scan.status, func.count(Scan.id))
        .select_from(base_query.subquery())
        .group_by(Scan.status)
    )
    status_result = await db.execute(status_query)
    status_counts = dict(status_result.fetchall())
    
   
    yesterday = datetime.now() - timedelta(days=1)
    recent_query = base_query.filter(Scan.created_date >= yesterday)
    recent_result = await db.execute(select(func.count(Scan.id)).select_from(recent_query.subquery()))
    recent_scans = recent_result.scalar()
    
    
    domain_query = (
        select(Scan.domain, func.count(Scan.id))
        .select_from(base_query.subquery())
        .group_by(Scan.domain)
        .order_by(desc(func.count(Scan.id)))
        .limit(10)
    )
    domain_result = await db.execute(domain_query)
    top_domains = dict(domain_result.fetchall())
    
    
    duration_query = (
        select(func.avg(Scan.duration_seconds))
        .select_from(base_query.subquery())
        .filter(Scan.duration_seconds.isnot(None))
    )
    duration_result = await db.execute(duration_query)
    avg_duration = duration_result.scalar()
    
    return {
        "total_scans": total_scans,
        "status_counts": status_counts,
        "recent_scans_24h": recent_scans,
        "top_domains": top_domains,
        "average_duration_seconds": avg_duration
    }


async def get_running_scans(db: AsyncSession) -> List[Scan]:
    """
    Retrieves all currently running scans.
    """
    result = await db.execute(
        select(Scan).filter(
            Scan.status == "running",
            Scan.is_active == True
        )
    )
    return list(result.scalars().all())


async def get_stale_scans(db: AsyncSession, timeout_minutes: int = 60) -> List[Scan]:
    """
    Retrieves scans that have been running for longer than the timeout period.
    """
    timeout_time = datetime.now() - timedelta(minutes=timeout_minutes)
    result = await db.execute(
        select(Scan).filter(
            Scan.status == "running",
            Scan.started_at < timeout_time,
            Scan.is_active == True
        )
    )
    return list(result.scalars().all())


async def count_scans_by_domain(db: AsyncSession, domain: str) -> int:
    """
    Counts the number of scans for a specific domain.
    """
    result = await db.execute(
        select(func.count(Scan.id)).filter(
            Scan.domain == domain,
            Scan.is_active == True
        )
    )
    return result.scalar()


async def _scan_has_started_at(db: AsyncSession, scan_id: str) -> bool:
    """
    Helper function to check if a scan has a started_at timestamp.
    """
    result = await db.execute(
        select(Scan.started_at).filter(Scan.id == scan_id)
    )
    started_at = result.scalar()
    return started_at is not None