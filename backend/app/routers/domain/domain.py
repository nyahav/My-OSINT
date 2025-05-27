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
    
def aggregate_total_results(scan) -> dict:
    def get_list(tool, key):
        if not tool or not isinstance(tool, dict):
            return []
        return tool.get(key, [])

    return {
        "total_subdomains": (
            len(get_list(scan.theharvester, "subdomains")) +
            len(get_list(scan.amass, "subdomains")) +
            len(get_list(scan.subfinder, "subdomains"))
        ),
        "total_emails": (
            len(get_list(scan.theharvester, "emails")) +
            len(get_list(scan.amass, "emails")) +
            len(get_list(scan.subfinder, "emails"))
        ),
        "total_hosts": (
            len(get_list(scan.theharvester, "hosts")) +
            len(get_list(scan.amass, "hosts")) +
            len(get_list(scan.subfinder, "hosts"))
        ),
        "total_ips": (
            len(get_list(scan.theharvester, "ips")) +
            len(get_list(scan.amass, "ips")) +
            len(get_list(scan.subfinder, "ips"))
        ),
    }
    

async def run_tool_and_update_db(
    db: AsyncSession,
    scan_id: str,
    domain: str,
    tool_func,             
    db_field: str,           
    tool_name: str,           
    tool_kwargs: dict = None, 
    timeout: int = 180
):
    logger.info(f"Running {tool_name} for scan_id={scan_id}, domain={domain}")
    results = None
    error_details = None
    start_time = datetime.utcnow()
    tool_kwargs = tool_kwargs or {}
    
    try:
        
        tool_result = await asyncio.wait_for(
            tool_func(domain, **tool_kwargs), 
            timeout=timeout
        )
        end_time = datetime.utcnow()
        
        if tool_result.get("success"):
            
            if tool_name.lower() == "theharvester" and "results" in tool_result:
                data = tool_result["results"]
            else:
                data = tool_result
           
            
            results = {
                "subdomains": data.get("subdomains", []),
                "emails": data.get("emails", []),
                "hosts": data.get("hosts", []),
                "ips": data.get("ips", []),
                "count": len(data.get("subdomains", [])),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
            results = deduplicate_results(results)
            logger.info(f"{tool_name} scan complete for scan_id={scan_id}")
        else:
            error_details = tool_result.get("error", f"{tool_name} failed without specific error.")
            logger.error(f"{tool_name} failed for scan_id={scan_id}: {error_details}")
            results = {"error": error_details, "start_time": start_time.isoformat(), "end_time": end_time.isoformat()}
            
    except asyncio.TimeoutError:
        logger.warning(f"{tool_name} timed out for scan_id={scan_id}, saving partial results if available.")
        end_time = datetime.utcnow()
        partial_data = {}

        
        try:
            partial_data = await security_tools.get_partial_results(domain)
            logger.info(f"Retrieved partial results for {tool_name}: {len(partial_data.get('subdomains', []))} subdomains, {len(partial_data.get('emails', []))} emails")
        except Exception as e:
            logger.error(f"Failed to get partial results from {tool_name}: {e}")
            partial_data = {}

        
        results = {
            "subdomains": partial_data.get("subdomains", []),
            "emails": partial_data.get("emails", []),
            "hosts": partial_data.get("hosts", []),
            "ips": partial_data.get("ips", []),
            "count": len(partial_data.get("subdomains", [])),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "timeout": True,
            "partial": True,
            "error": f"{tool_name} timed out after {timeout} seconds"
        }
        results = deduplicate_results(results)
        
        
        security_tools.clear_partial_results(domain)

    except Exception as e:
        error_details = f"Exception during {tool_name} run: {str(e)}"
        logger.exception(f"Exception while running {tool_name} for scan_id={scan_id}")
        results = {
            "error": error_details,
            "start_time": start_time.isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "timeout": False,
            "partial": False,
        }

   
    await crud_scan.update_scan_results(
        db,
        scan_id,
        **{db_field: results if results else {"error": error_details}},
        updated_by=f"system_{tool_name.lower()}_runner"
    )
    logger.info(f"Updated scan {scan_id} with {tool_name} results in DB (timeout={results.get('timeout', False)})")
    return results

async def run_scan_task(scan_id: str):
    async with AsyncSessionLocal() as db:
        logger.info(f"Starting background scan task for scan_id={scan_id}")

        scan = await crud_scan.get_scan_by_id(db, scan_id)
        if not scan:
            logger.error(f"Scan {scan_id} not found in DB for background task.")
            return

        domain = scan.domain
        tools_enabled =  {"theharvester": True, "amass": True , "subfinder": True}
        logger.info(f"tools_enabled: {tools_enabled}")
      
        overall_error_message = None

       
        await crud_scan.update_scan_status(db, scan_id, status=ScanStatus.RUNNING.value, updated_by="system_scanner")
        logger.info(f"Scan {scan_id} status updated to RUNNING.")

        tool_tasks = []
       
        if tools_enabled.get("theharvester"):
            logger.info("Adding theHarvester to tool_tasks")
            tool_tasks.append(
                
                run_tool_and_update_db(
                db, scan_id, domain,
                security_tools.run_theharvester,
                "theharvester",
                "theHarvester",
                tool_kwargs={"sources": "all"},
                timeout=120
                
        ))
        if tools_enabled.get("amass"):
            logger.info("Adding amass to tool_tasks")
            tool_tasks.append(
                run_tool_and_update_db(
                db, scan_id, domain,
                security_tools.run_amass,
                "amass",
                "amass",
                tool_kwargs={},
                timeout=120
            ))
        if tools_enabled.get("subfinder"):
            logger.info("Adding subfinder to tool_tasks")
            tool_tasks.append(
                run_tool_and_update_db(
                db, scan_id, domain,
                security_tools.run_subfinder,
                "subfinder",
                "subfinder",
                tool_kwargs={},
                timeout=120
            ) )  
            
        if not tool_tasks:
            overall_error_message = "No tools enabled for this scan."
            logger.warning(f"Scan {scan_id}: {overall_error_message}")
            await crud_scan.update_scan_status(db, scan_id, status=ScanStatus.ERROR.value, error_message=overall_error_message, updated_by="system_scanner")
            return

        try:
            
            await asyncio.gather(*tool_tasks, return_exceptions=True)

            scan_after_tools = await crud_scan.get_scan_by_id(db, scan_id)
            
            if not scan_after_tools:
                overall_error_message = "Scan disappeared during execution."
                raise ValueError(overall_error_message)

            
            summary = aggregate_total_results(scan_after_tools)
            
            tool_errors = []
            if tools_enabled.get("theharvester") and scan_after_tools.theharvester and scan_after_tools.theharvester.get("error"):
                tool_errors.append(f"theHarvester: {scan_after_tools.theharvester['error']}")
          
            if tool_errors:
                overall_error_message = "Some tools failed: " + "; ".join(tool_errors)
                final_status = ScanStatus.ERROR.value
            else:
                final_status = ScanStatus.FINISHED.value

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
    logger.info(f"Retrieving results for scan_id={scan_id}")
    scan = await crud_scan.get_scan_by_id(db, scan_id)
    if not scan or not scan.is_active:
        raise HTTPException(status_code=404, detail="Scan not found or soft-deleted.")

    if scan.status != ScanStatus.FINISHED.value:
        return {
        "scan_id": scan.id,
        "status": scan.status,
        "domain": scan.domain,  
    }
         
    return {
        "scan_id": scan.id,
        "status": scan.status,
        "theHarvester": scan.theharvester,
        "amass": scan.amass,
        "subfinder": scan.subfinder,  
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
    
   
    if scan_data.is_completed and not scan_data.duration_seconds:
       
        pass 
    
    return ScanOut.model_validate(scan_data) 


@router.get("/{scan_id}/status", response_model=Dict[str, Any]) 
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
    return {} 



@router.get("/", response_model=List[ScanOut])
async def list_scans(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[ScanStatus] = None, 
    domain: Optional[str] = None,
    user_id: Optional[int] = None, 
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
        status=status.value if status else None,
        domain=domain,
        user_id=user_id,
        is_public=is_public,
        order_by=order_by,
        order_direction=order_direction
    )
    return [ScanOut.model_validate(scan) for scan in scans_from_db] 

@router.get("/stats", response_model=Dict[str, Any])
async def get_overall_scan_stats(
    db: AsyncSession = Depends(get_db),
    user_id: Optional[int] = None 
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


