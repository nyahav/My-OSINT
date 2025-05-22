from fastapi import APIRouter, BackgroundTasks
from uuid import uuid4
import asyncio
import json

router = APIRouter()
scans = {}

async def run_theharvester(domain: str):
    try:
        proc = await asyncio.create_subprocess_exec(
            "theHarvester",
            "-d", domain,
            "-b", "all",
            "-f", "result",  # creates result.xml and result.json
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            try:
                with open("result.json") as f:
                    data = json.load(f)
                    return data
            except Exception as e:
                return {"error": "Could not parse theHarvester output", "details": str(e)}
        else:
            return {"error": "theHarvester failed", "stderr": stderr.decode()}
    except Exception as e:
        return {"error": "Failed to run theHarvester", "details": str(e)}

async def run_amass(domain: str):
    try:
        proc = await asyncio.create_subprocess_exec(
            "amass",
            "enum",
            "-d", domain,
            "-json", "amass.json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            try:
                with open("amass.json") as f:
                    data = json.load(f)
                    return data
            except Exception as e:
                return {"error": "Could not parse Amass output", "details": str(e)}
        else:
            return {"error": "Amass failed", "stderr": stderr.decode()}
    except Exception as e:
        return {"error": "Failed to run Amass", "details": str(e)}

async def run_scan(scan_id, domain):
    theharvester_task = asyncio.create_task(run_theharvester(domain))
    amass_task = asyncio.create_task(run_amass(domain))
    results = await asyncio.gather(theharvester_task, amass_task)
    scans[scan_id]["theHarvester"] = results[0]
    scans[scan_id]["amass"] = results[1]
    scans[scan_id]["status"] = "finished"

@router.post("/scan")
async def start_scan(data: dict, background_tasks: BackgroundTasks):
    domain = data.get("domain")
    if not domain:
        return {"error": "No domain provided"}
    
    scan_id = str(uuid4())
    scans[scan_id] = {"status": "running", "theHarvester": None, "amass": None}
    background_tasks.add_task(run_scan, scan_id, domain)
    return {"scan_id": scan_id}

@router.get("/scan/{scan_id}/results")
async def get_scan_results(scan_id: str):
    return scans.get(scan_id, {"status": "not_found"})
