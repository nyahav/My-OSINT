import subprocess
import json
import os
import asyncio
from typing import List, Dict, Any
from tools.logger import logger

class SecurityTools:
    def __init__(self):
        self.shared_dir = "/home/app/shared"
        self.tools_container = "security-tools"
      
        self.partial_results = {}
    
    async def get_partial_results(self, domain: str) -> Dict[str, Any]:
       
        return self.partial_results.get(domain, {
            "subdomains": [],
            "emails": [],
            "hosts": [],
            "ips": []
        })
    
    def clear_partial_results(self, domain: str):
      
        if domain in self.partial_results:
            del self.partial_results[domain]
    
    async def run_amass(self, domain: str, timeout: int = 300) -> Dict[str, Any]:
        """
        Run Amass subdomain enumeration with partial results support
        """
        logger.info(f"Starting Amass scan for domain: {domain}")
        
      
        self.partial_results[domain] = {
            "subdomains": [],
            "emails": [],
            "hosts": [],
            "ips": []
        }
        
        try:
            cmd = [
                "docker", "exec", self.tools_container,
                "amass", "enum", "-passive", "-d", domain
            ]
            logger.debug(f"Executing Amass command: {' '.join(cmd)}")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            subdomains_found = []
            
            try:
                while True:
                    try:
                        line = await asyncio.wait_for(
                            process.stdout.readline(), 
                            timeout=10
                        )
                        if not line:
                            break
                            
                        decoded = line.decode().strip()
                        if decoded and decoded not in subdomains_found:
                            subdomains_found.append(decoded)
                            self.partial_results[domain]["subdomains"] = subdomains_found
                            logger.debug(f"Found subdomain: {decoded} (total: {len(subdomains_found)})")
                            
                    except asyncio.TimeoutError:
                      
                        if process.returncode is not None:
                            break
                        continue
                        
              
                await asyncio.wait_for(process.wait(), timeout=timeout)
                
                logger.info(f"Amass completed successfully for {domain}. Found {len(subdomains_found)} subdomains.")
                return {
                    "success": True,
                    "tool": "amass",
                    "domain": domain,
                    "subdomains": subdomains_found,
                    "count": len(subdomains_found)
                }
                
            except asyncio.TimeoutError:
              
                logger.warning(f"Amass timed out for {domain}, returning partial results: {len(subdomains_found)} subdomains")
                try:
                    process.kill()
                    await process.wait()
                except:
                    pass
                    
                return {
                    "success": True, 
                    "partial": True,
                    "timeout": True,
                    "tool": "amass",
                    "domain": domain,
                    "subdomains": subdomains_found,
                    "count": len(subdomains_found),
                    "error": f"Timeout after {timeout} seconds"
                }
                
        except Exception as e:
            logger.exception(f"Exception in Amass for {domain}")
          
            partial = self.partial_results.get(domain, {})
            return {
                "success": False,
                "error": str(e),
                "subdomains": partial.get("subdomains", []),
                "count": len(partial.get("subdomains", []))
            }
    
    async def run_subfinder(self, domain: str, timeout: int = 120) -> Dict[str, Any]:
        """
        Run subfinder with partial results support
        """
        logger.info(f"Starting subfinder scan for domain: {domain}")
        
     
        self.partial_results[domain] = {
            "subdomains": [],
            "emails": [],
            "hosts": [],
            "ips": []
        }
        
        try:
            cmd = [
                "docker", "exec", self.tools_container,
                "subfinder", "-d", domain, "-silent"
            ]
            logger.debug(f"Executing subfinder command: {' '.join(cmd)}")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            subdomains_found = []
            
            try:
                while True:
                    try:
                        line = await asyncio.wait_for(
                            process.stdout.readline(), 
                            timeout=10
                        )
                        if not line:
                            break
                            
                        decoded = line.decode().strip()
                        if decoded and decoded not in subdomains_found:
                            subdomains_found.append(decoded)
                            self.partial_results[domain]["subdomains"] = subdomains_found
                            logger.debug(f"Subfinder found: {decoded} (total: {len(subdomains_found)})")
                            
                    except asyncio.TimeoutError:
                        if process.returncode is not None:
                            break
                        continue
                        
                await asyncio.wait_for(process.wait(), timeout=timeout)
                
                logger.info(f"Subfinder completed for {domain}. Found {len(subdomains_found)} subdomains.")
                return {
                    "success": True,
                    "tool": "subfinder",
                    "domain": domain,
                    "subdomains": subdomains_found,
                    "count": len(subdomains_found)
                }
                
            except asyncio.TimeoutError:
                logger.warning(f"Subfinder timed out for {domain}, returning partial results: {len(subdomains_found)} subdomains")
                try:
                    process.kill()
                    await process.wait()
                except:
                    pass
                    
                return {
                    "success": True,
                    "partial": True,
                    "timeout": True,
                    "tool": "subfinder", 
                    "domain": domain,
                    "subdomains": subdomains_found,
                    "count": len(subdomains_found),
                    "error": f"Timeout after {timeout} seconds"
                }
                
        except Exception as e:
            logger.exception(f"Exception in subfinder for {domain}")
            partial = self.partial_results.get(domain, {})
            return {
                "success": False,
                "error": str(e),
                "subdomains": partial.get("subdomains", []),
                "count": len(partial.get("subdomains", []))
            }

    async def run_theharvester(self, domain: str, sources: str = "google,bing", timeout: int = 300) -> Dict[str, Any]:
        """
        Run theHarvester with partial results support
        """
        logger.info(f"Starting theHarvester scan for domain: {domain}")
        
     
        self.partial_results[domain] = {
            "subdomains": [],
            "emails": [],
            "hosts": [],
            "ips": []
        }
        
        output_file_name = f"harvester_output_{domain.replace('.', '_')}.json"
        tools_output_path = f"/home/tools/shared/{output_file_name}"
        api_output_path = f"{self.shared_dir}/{output_file_name}"

        try:
            cmd = [
                "docker", "exec", self.tools_container,
                "python3", "/opt/theHarvester/theHarvester.py",
                "-d", domain,
                "-b", sources,
                "-f", tools_output_path
            ]
            logger.debug(f"Executing theHarvester command: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
          
                results = {"emails": [], "hosts": [], "ips": []}
                if os.path.exists(api_output_path):
                    try:
                        with open(api_output_path, 'r') as f:
                            file_results = json.load(f)
                            if 'hosts' in file_results:
                                results['hosts'].extend(file_results['hosts'])
                            if 'emails' in file_results:
                                results['emails'].extend(file_results['emails'])
                            if 'ips' in file_results:
                                results['ips'].extend(file_results['ips'])
                        
                      
                        self.partial_results[domain].update(results)
                        
                    except Exception as e:
                        logger.error(f"Error reading theHarvester output: {e}")
                    finally:
                        if os.path.exists(api_output_path):
                            os.remove(api_output_path)
                
                return {
                    "success": True,
                    "tool": "theHarvester",
                    "domain": domain,
                    "sources": sources,
                    "results": results
                }
                
            except asyncio.TimeoutError:
                logger.warning(f"theHarvester timed out for {domain}")
                try:
                    process.kill()
                    await process.wait()
                except:
                    pass
                
         
                partial_results = {"emails": [], "hosts": [], "ips": []}
                if os.path.exists(api_output_path):
                    try:
                        with open(api_output_path, 'r') as f:
                            file_results = json.load(f)
                            if 'hosts' in file_results:
                                partial_results['hosts'].extend(file_results['hosts'])
                            if 'emails' in file_results:
                                partial_results['emails'].extend(file_results['emails'])
                            if 'ips' in file_results:
                                partial_results['ips'].extend(file_results['ips'])
                        os.remove(api_output_path)
                    except:
                        pass
                
                return {
                    "success": True,
                    "partial": True,
                    "timeout": True,
                    "tool": "theHarvester",
                    "domain": domain,
                    "sources": sources,
                    "results": partial_results,
                    "error": f"Timeout after {timeout} seconds"
                }
                
        except Exception as e:
            logger.exception(f"Exception in theHarvester for {domain}")
            partial = self.partial_results.get(domain, {})
            return {
                "success": False,
                "error": str(e),
                "results": {
                    "emails": partial.get("emails", []),
                    "hosts": partial.get("hosts", []),
                    "ips": partial.get("ips", [])
                }
            }
    
    async def run_combined_scan(self, domain: str) -> Dict[str, Any]:
        """
        Run both tools and combine results
        """
        logger.info(f"Starting combined scan for domain: {domain}")
        amass_task = self.run_amass(domain)
        theharvester_task = self.run_theharvester(domain)
        subfinder_task = self.run_subfinder(domain) 
        
        amass, harvester , subfinder = await asyncio.gather(amass_task, theharvester_task, subfinder_task)

        results = {
            "domain": domain,
            "amass": amass,
            "theharvester": harvester,
            "subfinder": subfinder
            
        }
        
        logger.info(f"Combined scan for domain: {domain} completed.")
        return results