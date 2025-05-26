# from fastapi import APIRouter, BackgroundTasks
# from uuid import uuid4
# import asyncio
# import json
# from app.utilities.logger import logger
# import sys
# import os
# sys.path.append("\tools\security_tools.py") 
# from tools.security_tools import SecurityTools 

# router = APIRouter()
# scans = {}
# security_tools = SecurityTools()  


# async def run_theharvester(scan_id: str, domain: str):
#     """
#     Run theHarvester using the containerized tools
#     """
#     logger.info(f"Running theHarvester for scan_id={scan_id}, domain={domain}")
#     try:
#         # Use the SecurityTools class instead of direct subprocess
#         result = await security_tools.run_theharvester(domain, sources="all", timeout=600)
        
#         if result.get("success"):
#             logger.info(f"theHarvester scan complete for scan_id={scan_id}")
#             return result["results"]
#         else:
#             logger.error(f"theHarvester failed: {result.get('error', 'Unknown error')}")
#             return {"error": result.get("error", "theHarvester failed")}
            
#     except Exception as e:
#         logger.exception("Exception while running theHarvester")
#         return {"error": "Failed to run theHarvester", "details": str(e)}


# async def run_amass(scan_id: str, domain: str):
#     """
#     Run Amass using the containerized tools
#     """
#     logger.info(f"Running Amass for scan_id={scan_id}, domain={domain}")
#     try:
#         # Use the SecurityTools class instead of direct subprocess
#         result = await security_tools.run_amass(domain, timeout=600)
        
#         if result.get("success"):
#             logger.info(f"Amass scan complete for scan_id={scan_id}")
#             # Return the subdomains in a format similar to your original structure
#             return {
#                 "subdomains": result["subdomains"],
#                 "count": result["count"]
#             }
#         else:
#             logger.error(f"Amass failed: {result.get('error', 'Unknown error')}")
#             return {"error": result.get("error", "Amass failed")}
            
#     except Exception as e:
#         logger.exception("Exception while running Amass")
#         return {"error": "Failed to run Amass", "details": str(e)}


# async def run_scan(scan_id, domain):
#     """
#     Run both tools concurrently and store results
#     """
#     logger.info(f"Starting scan tasks for scan_id={scan_id}")
    
#     try:
#         # You can still run them separately if you want individual control
#         theharvester_task = asyncio.create_task(run_theharvester(scan_id, domain))
        

#         results = await asyncio.gather(theharvester_task, return_exceptions=True)

#         # Handle results and exceptions
#         theharvester_result = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
        
#         scans[scan_id]["theHarvester"] = theharvester_result
        
#         scans[scan_id]["status"] = "finished"
        
#         logger.info(f"Scan {scan_id} finished")
        
#     except Exception as e:
#         logger.exception(f"Exception in scan {scan_id}")
#         scans[scan_id]["status"] = "error"
#         scans[scan_id]["error"] = str(e)
        
#     # async def run_scan(scan_id, domain):
#     # """
#     # Run both tools concurrently and store results
#     # """
#     # logger.info(f"Starting scan tasks for scan_id={scan_id}")
    
#     # try:
#     #     # You can still run them separately if you want individual control
#     #     theharvester_task = asyncio.create_task(run_theharvester(scan_id, domain))
#     #     amass_task = asyncio.create_task(run_amass(scan_id, domain))

#     #     results = await asyncio.gather(theharvester_task, amass_task, return_exceptions=True)

#     #     # Handle results and exceptions
#     #     theharvester_result = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
#     #     amass_result = results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])}

#     #     scans[scan_id]["theHarvester"] = theharvester_result
#     #     scans[scan_id]["amass"] = amass_result
#     #     scans[scan_id]["status"] = "finished"
        
#     #     logger.info(f"Scan {scan_id} finished")
        
#     # except Exception as e:
#     #     logger.exception(f"Exception in scan {scan_id}")
#     #     scans[scan_id]["status"] = "error"
#     #     scans[scan_id]["error"] = str(e)


# # Alternative: Use the combined scan method
# async def run_combined_scan(scan_id, domain):
#     """
#     Use the combined scan method from SecurityTools
#     """
#     logger.info(f"Starting combined scan for scan_id={scan_id}")
    
#     try:
#         result = await security_tools.run_combined_scan(domain)
        
#         # Extract results in the format your frontend expects
#         theharvester_data = result["results"]["theharvester"]
#         amass_data = result["results"]["amass"]
        
#         scans[scan_id]["theHarvester"] = theharvester_data.get("results") if theharvester_data.get("success") else theharvester_data
#         scans[scan_id]["amass"] = {"subdomains": amass_data.get("subdomains", []), "count": amass_data.get("count", 0)} if amass_data.get("success") else amass_data
#         scans[scan_id]["status"] = "finished"
#         scans[scan_id]["summary"] = result["summary"]
        
#         logger.info(f"Combined scan {scan_id} finished")
        
#     except Exception as e:
#         logger.exception(f"Exception in combined scan {scan_id}")
#         scans[scan_id]["status"] = "error"
#         scans[scan_id]["error"] = str(e)


# @router.post("/scan")
# async def start_scan(data: dict, background_tasks: BackgroundTasks):
#     """
#     Start a new security scan
#     """
#     domain = data.get("domain")
#     if not domain:
#         logger.warning("Scan start request missing domain")
#         return {"error": "No domain provided"}
    
#     scan_id = str(uuid4())
#     logger.info(f"Received scan request for domain={domain}, assigned scan_id={scan_id}")
    
    
#     scans[scan_id] = {
#         "status": "running", 
#         "domain": domain,
#         "theHarvester": None, 
#         "amass": None,
#         "started_at": asyncio.get_event_loop().time()
#     }
    
    
#     # Option 1: Use individual tools (maintains your original structure)
#     background_tasks.add_task(run_scan, scan_id, domain)
    
#     # Option 2: Use combined scan (more efficient)
#     # background_tasks.add_task(run_combined_scan, scan_id, domain)
    
#     return {"scan_id": scan_id}


# @router.get("/scan/{scan_id}/results")
# async def get_scan_results(scan_id: str):
#     """
#     Get scan results by scan ID
#     """
#     logger.info(f"Retrieving results for scan_id={scan_id}")
    
#     scan_data = scans.get(scan_id, {"status": "not_found"})
    
#     # Add some additional metadata if scan exists
#     if scan_data.get("status") != "not_found":
#         scan_data["scan_id"] = scan_id
#         if scan_data.get("started_at"):
#             current_time = asyncio.get_event_loop().time()
#             scan_data["duration"] = current_time - scan_data["started_at"]
    
#     return scan_data


# @router.get("/scan/{scan_id}/status")
# async def get_scan_status(scan_id: str):
#     """
#     Get just the status of a scan (lighter endpoint)
#     """
#     logger.info(f"Checking status for scan_id={scan_id}")
    
#     scan_data = scans.get(scan_id, {"status": "not_found"})
    
#     return {
#         "scan_id": scan_id,
#         "status": scan_data.get("status", "not_found"),
#         "domain": scan_data.get("domain"),
#         "has_results": scan_data.get("theHarvester") is not None or scan_data.get("amass") is not None
#     }


# @router.delete("/scan/{scan_id}")
# async def delete_scan(scan_id: str):
#     """
#     Delete scan results (cleanup)
#     """
#     if scan_id in scans:
#         del scans[scan_id]
#         logger.info(f"Deleted scan {scan_id}")
#         return {"message": f"Scan {scan_id} deleted"}
#     else:
#         return {"error": "Scan not found"}


# @router.get("/scans")
# async def list_scans():
#     """
#     List all scans with their status
#     """
#     scan_list = []
#     for scan_id, scan_data in scans.items():
#         scan_list.append({
#             "scan_id": scan_id,
#             "status": scan_data.get("status"),
#             "domain": scan_data.get("domain"),
#             "started_at": scan_data.get("started_at")
#         })
    
#     return {"scans": scan_list, "count": len(scan_list)}


# # Health check for the tools
# @router.get("/tools/health")
# async def check_tools_health():
#     """
#     Check if the security tools are available
#     """
#     try:
#         health_status = await security_tools.health_check()
#         return health_status
#     except Exception as e:
#         logger.error(f"Tools health check failed: {e}")
#         return {"status": "unhealthy", "error": str(e)}