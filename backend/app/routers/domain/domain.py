from fastapi import APIRouter, BackgroundTasks
from uuid import uuid4
import asyncio
import json
from app.utilities.logger import logger

router = APIRouter()
scans = {}


async def run_theharvester(scan_id: str, domain: str):
    filename_prefix = f"result_{scan_id}"
    json_file = f"{filename_prefix}.json"
    logger.info(f"Running theHarvester for scan_id={scan_id}, domain={domain}")
    try:
        proc = await asyncio.create_subprocess_exec(
            "theHarvester",
            "-d", domain,
            "-b", "all",
            "-f", filename_prefix,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        logger.debug(f"theHarvester stdout: {stdout.decode()}")
        logger.debug(f"theHarvester stderr: {stderr.decode()}")

        if proc.returncode == 0:
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    logger.info(f"theHarvester scan complete for scan_id={scan_id}")
                    return data
            except Exception as e:
                logger.exception("Failed to parse theHarvester output")
                return {"error": "Could not parse theHarvester output", "details": str(e)}
        else:
            logger.error(f"theHarvester failed with code {proc.returncode}")
            return {"error": "theHarvester failed", "stderr": stderr.decode()}
    except Exception as e:
        logger.exception("Exception while running theHarvester")
        return {"error": "Failed to run theHarvester", "details": str(e)}

async def run_amass(scan_id: str, domain: str):
    json_file = f"amass_{scan_id}.json"
    logger.info(f"Running Amass for scan_id={scan_id}, domain={domain}")
    try:
        proc = await asyncio.create_subprocess_exec(
            "amass",
            "enum",
            "-d", domain,
            "-json", json_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        logger.debug(f"Amass stdout: {stdout.decode()}")
        logger.debug(f"Amass stderr: {stderr.decode()}")

        if proc.returncode == 0:
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    logger.info(f"Amass scan complete for scan_id={scan_id}")
                    return data
            except Exception as e:
                logger.exception("Failed to parse Amass output")
                return {"error": "Could not parse Amass output", "details": str(e)}
        else:
            logger.error(f"Amass failed with code {proc.returncode}")
            return {"error": "Amass failed", "stderr": stderr.decode()}
    except Exception as e:
        logger.exception("Exception while running Amass")
        return {"error": "Failed to run Amass", "details": str(e)}

async def run_scan(scan_id, domain):
    logger.info(f"Starting scan tasks for scan_id={scan_id}")
    theharvester_task = asyncio.create_task(run_theharvester(scan_id, domain))
    amass_task = asyncio.create_task(run_amass(scan_id, domain))

    results = await asyncio.gather(theharvester_task, amass_task)

    scans[scan_id]["theHarvester"] = results[0]
    scans[scan_id]["amass"] = results[1]
    scans[scan_id]["status"] = "finished"
    logger.info(f"Scan {scan_id} finished")

@router.post("/scan")
async def start_scan(data: dict, background_tasks: BackgroundTasks):
    domain = data.get("domain")
    if not domain:
        logger.warning("Scan start request missing domain")
        return {"error": "No domain provided"}
    
    scan_id = str(uuid4())
    logger.info(f"Received scan request for domain={domain}, assigned scan_id={scan_id}")
    scans[scan_id] = {"status": "running", "theHarvester": None, "amass": None}
    background_tasks.add_task(run_scan, scan_id, domain)
    return {"scan_id": scan_id}

@router.get("/scan/{scan_id}/results")
async def get_scan_results(scan_id: str):
    logger.info(f"Retrieving results for scan_id={scan_id}")
    return scans.get(scan_id, {"status": "not_found"})