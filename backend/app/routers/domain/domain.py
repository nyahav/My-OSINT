from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
from app.db.session import AsyncSessionLocal

from app.utilities.logger import logger
from app.db.session import get_db 
from app.db.models.scan import Scan, ScanStatus
from app.crud import scan as crud_scan 
from app.schemas.scan import ScanCreate, ScanUpdate, ScanOut 
from tools.security_tools import SecurityTools 

router = APIRouter() 
security_tools = SecurityTools()


def deduplicate_results(results: dict, keys: List[str] = ["emails", "hosts", "subdomains", "ips"]) -> dict:
    """
    Remove duplicates from lists in results dict for the given keys.
    """
    for key in keys:
        if key in results and isinstance(results[key], list):
            results[key] = list(dict.fromkeys(results[key]))
    return results

async def _run_theharvester_and_update_db(db: AsyncSession, scan_id: str, domain: str):
    """
    Runs theHarvester and updates the database with results.
    """
    logger.info(f"Running theHarvester for scan_id={scan_id}, domain={domain}")
    results = None
    error_details = None
    try:
        tool_result = await security_tools.run_theharvester(domain, sources="all", timeout=180)

        if tool_result.get("success"):
            logger.info(f"theHarvester scan complete for scan_id={scan_id}")
            results = tool_result["results"]
            results = deduplicate_results(tool_result["results"])
            
        else:
            error_details = tool_result.get("error", "TheHarvester failed without specific error.")
            logger.error(f"theHarvester failed for scan_id={scan_id}: {error_details}")

    except Exception as e:
        error_details = f"Exception during theHarvester run: {str(e)}"
        logger.exception(f"Exception while running theHarvester for scan_id={scan_id}")

    # Update database with results or error
    await crud_scan.update_scan_results(
        db,
        scan_id,
        theharvester_results=results if results else {"error": error_details},
        updated_by="system_theharvester_runner" # Example for audit field
    )
    # The scan status will be finalized by the main run_scan_task
    # if this was the only tool or part of a combined run.

async def _run_amass_and_update_db(db: AsyncSession, scan_id: str, domain: str):
    """
    Runs Amass and updates the database with results.
    """
    logger.info(f"Running Amass for scan_id={scan_id}, domain={domain}")
    results = None
    error_details = None
    try:
        tool_result = await security_tools.run_amass(domain, timeout=600)

        if tool_result.get("success"):
            logger.info(f"Amass scan complete for scan_id={scan_id}")
            results = {
                "subdomains": tool_result["subdomains"],
                "count": tool_result["count"]
            }
        else:
            error_details = tool_result.get("error", "Amass failed without specific error.")
            logger.error(f"Amass failed for scan_id={scan_id}: {error_details}")

    except Exception as e:
        error_details = f"Exception during Amass run: {str(e)}"
        logger.exception(f"Exception while running Amass for scan_id={scan_id}")

    # Update database with results or error
    await crud_scan.update_scan_results(
        db,
        scan_id,
        amass_results=results if results else {"error": error_details},
        updated_by="system_amass_runner" # Example for audit field
    )
    # The scan status will be finalized by the main run_scan_task

# --- Main Scan Execution Task (Modified to use DB) ---

async def run_scan_task(scan_id: str):
    async with AsyncSessionLocal() as db:
        logger.info(f"Starting background scan task for scan_id={scan_id}")

        scan = await crud_scan.get_scan_by_id(db, scan_id)
        if not scan:
            logger.error(f"Scan {scan_id} not found in DB for background task.")
            return

        domain = scan.domain
        tools_enabled = scan.tools_enabled or {"theharvester": True, "amass": False}  # Default to both tools if not specified
        overall_error_message = None

        # Update scan status to RUNNING
        await crud_scan.update_scan_status(db, scan_id, status=ScanStatus.RUNNING.value, updated_by="system_scanner")
        logger.info(f"Scan {scan_id} status updated to RUNNING.")

        tool_tasks = []
        if tools_enabled.get("theharvester"):
            tool_tasks.append(_run_theharvester_and_update_db(db, scan_id, domain))
        #if tools_enabled.get("amass"):
        #    tool_tasks.append(_run_amass_and_update_db(db, scan_id, domain))

        if not tool_tasks:
            overall_error_message = "No tools enabled for this scan."
            logger.warning(f"Scan {scan_id}: {overall_error_message}")
            await crud_scan.update_scan_status(db, scan_id, status=ScanStatus.ERROR.value, error_message=overall_error_message, updated_by="system_scanner")
            return

        try:
            # Run all enabled tool tasks concurrently
            await asyncio.gather(*tool_tasks, return_exceptions=True)

            # After all tools have run, retrieve the latest scan state from DB
            # to check for individual tool errors and determine overall status.
            scan_after_tools = await crud_scan.get_scan_by_id(db, scan_id)
            
            if not scan_after_tools:
                overall_error_message = "Scan disappeared during execution."
                raise ValueError(overall_error_message)

            # Aggregate summary and check for errors from individual tools
            summary = {
                "total_subdomains": scan_after_tools.total_subdomains,
                "total_emails": scan_after_tools.total_emails,
                "total_ips": scan_after_tools.total_ips
            }
            
            tool_errors = []
            if tools_enabled.get("theharvester") and scan_after_tools.theharvester_results and scan_after_tools.theharvester_results.get("error"):
                tool_errors.append(f"theHarvester: {scan_after_tools.theharvester_results['error']}")
            # if tools_enabled.get("amass") and scan_after_tools.amass_results and scan_after_tools.amass_results.get("error"):
            #     tool_errors.append(f"Amass: {scan_after_tools.amass_results['error']}")
            
            if tool_errors:
                overall_error_message = "Some tools failed: " + "; ".join(tool_errors)
                final_status = ScanStatus.ERROR.value
            else:
                final_status = ScanStatus.FINISHED.value

            # Update summary and final status
            await crud_scan.update_scan_results(db, scan_id, summary=summary, updated_by="system_scanner")
            await crud_scan.update_scan_status(
                db,
                scan_id,
                status=final_status,
                error_message=overall_error_message,
                updated_by="system_scanner"
            )
            logger.info(f"Scan {scan_id} finalized with status: {final_status}")

        except asyncio.CancelledError:
            logger.warning(f"Scan {scan_id} was cancelled.")
            await crud_scan.update_scan_status(db, scan_id, status=ScanStatus.CANCELLED.value, updated_by="system_scanner")
        except Exception as e:
            overall_error_message = f"Critical error during scan orchestration: {str(e)}"
            logger.exception(f"Critical exception in scan {scan_id} orchestration.")
            await crud_scan.update_scan_status(db, scan_id, status=ScanStatus.ERROR.value, error_message=overall_error_message, updated_by="system_scanner")

# --- API Endpoints ---

@router.post("/", response_model=ScanOut, status_code=status.HTTP_202_ACCEPTED)
async def start_scan(
    scan_create: ScanCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    
    logger.info(f"Received scan request for domain={scan_create.domain}")
    db_scan = await crud_scan.create_scan(db, scan_create, created_by="api_user") 
    if not db_scan:
     logger.error("Failed to create scan record! Check DB and migrations.")
     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create scan record.")
    if not db_scan:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create scan record.")

    background_tasks.add_task(run_scan_task, db_scan.id)     
    return ScanOut.model_validate(db_scan) 



@router.get("/{scan_id}/results", response_model=Dict[str, Any])
async def get_scan_results(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get scan results by scan ID (for frontend polling).
    """
    logger.info(f"Retrieving results for scan_id={scan_id}")
    scan = await crud_scan.get_scan_by_id(db, scan_id)
    if not scan or not scan.is_active:
        raise HTTPException(status_code=404, detail="Scan not found or soft-deleted.")

    
    return {
        "scan_id": scan.id,
        "status": scan.status,
        "theHarvester": scan.theharvester_results,
        "amass": scan.amass_results,
        "summary": scan.summary,
        "error": scan.error_message,
        "started_at": scan.started_at.isoformat() if scan.started_at else None,
        "finished_at": scan.finished_at.isoformat() if scan.finished_at else None,
        "duration_seconds": scan.duration_seconds,
        "domain": scan.domain,
    }
    
    
@router.get("/{scan_id}", response_model=ScanOut)
async def get_scan_details(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get full scan details by scan ID.
    """
    logger.info(f"Retrieving full details for scan_id={scan_id}")
    scan_data = await crud_scan.get_scan_by_id(db, scan_id)

    if not scan_data or not scan_data.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found or soft-deleted.")
    
    # Ensure duration is calculated if status is finished/error/cancelled
    if scan_data.is_completed and not scan_data.duration_seconds:
        # Re-fetch the scan to get the latest updated duration if it was just calculated
        # This might happen if the `finished_at` was just set, but the duration calculation
        # didn't trigger a refresh before this endpoint was called.
        # However, `update_scan_status` already updates `duration_seconds` before committing.
        # So, usually, you won't need to explicitly call it here.
        # If duration is missing, it implies a race condition or a specific scenario not handled.
        pass # The model's `to_dict` will calculate duration for ongoing scans if `started_at` is present.
    
    # Use the to_dict method from the SQLAlchemy model
    # Or preferably, use Pydantic's from_orm/model_validate
    return ScanOut.model_validate(scan_data) # Use .model_validate for Pydantic v2 or .from_orm for Pydantic v1


@router.get("/{scan_id}/status", response_model=Dict[str, Any]) # More specific response model if possible
async def get_scan_status(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get just the status and basic info of a scan (lighter endpoint).
    """
    logger.info(f"Checking status for scan_id={scan_id}")
    scan = await crud_scan.get_scan_by_id(db, scan_id)

    if not scan or not scan.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found or soft-deleted.")
    
    return {
        "scan_id": scan.id,
        "status": scan.status,
        "domain": scan.domain,
        "has_results": scan.has_results,
        "started_at": scan.started_at.isoformat() if scan.started_at else None,
        "finished_at": scan.finished_at.isoformat() if scan.finished_at else None,
        "duration_seconds": scan.duration_seconds
    }

@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan_record(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Soft deletes a scan record (sets is_active to False).
    """
    logger.info(f"Soft deleting scan {scan_id}")
    success = await crud_scan.delete_scan(db, scan_id, deleted_by="api_user") # You might want to get actual user from auth
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found.")
    return {} # Return empty response for 204 No Content

# Optional: Add an endpoint for hard deletion, typically for admins only
# @router.delete("/{scan_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
# async def hard_delete_scan_record(
#     scan_id: str,
#     db: AsyncSession = Depends(get_db)
# ):
#     """
#     Permanently deletes a scan record from the database. (Admin only)
#     """
#     logger.warning(f"Hard deleting scan {scan_id}. This action is irreversible.")
#     success = await crud_scan.hard_delete_scan(db, scan_id)
#     if not success:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found.")
#     return {}

@router.get("/", response_model=List[ScanOut])
async def list_scans(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[ScanStatus] = None, # Use the Enum for validation
    domain: Optional[str] = None,
    user_id: Optional[int] = None, # If you implement user authentication
    is_public: Optional[bool] = None,
    order_by: str = "created_date",
    order_direction: str = "desc"
):
    """
    List all scans with filtering and pagination.
    """
    logger.info(f"Listing scans with filters: status={status}, domain={domain}, user_id={user_id}")
    scans_from_db = await crud_scan.get_scans(
        db, 
        skip=skip, 
        limit=limit, 
        status=status.value if status else None, # Pass enum value to CRUD
        domain=domain,
        user_id=user_id,
        is_public=is_public,
        order_by=order_by,
        order_direction=order_direction
    )
    return [ScanOut.model_validate(scan) for scan in scans_from_db] # Use .model_validate for Pydantic v2 or .from_orm for Pydantic v1

@router.get("/stats", response_model=Dict[str, Any])
async def get_overall_scan_stats(
    db: AsyncSession = Depends(get_db),
    user_id: Optional[int] = None # Filter stats by user if needed
):
    """
    Retrieve overall scanning statistics.
    """
    logger.info(f"Retrieving scan statistics for user_id={user_id}")
    stats = await crud_scan.get_scan_stats(db, user_id=user_id)
    return stats

@router.get("/tools/health", response_model=Dict[str, Any])
async def check_tools_health():
    """
    Check if the security tools are available and responsive.
    """
    try:
        health_status = await security_tools.health_check()
        return health_status
    except Exception as e:
        logger.error(f"Tools health check failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Tools health check failed: {str(e)}")