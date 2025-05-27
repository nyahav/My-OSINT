import subprocess
import json
import os
import asyncio
from typing import List, Dict, Any
from tools.logger import logger # Corrected import path for logger

class SecurityTools:
    def __init__(self):
        self.shared_dir = "/home/app/shared"
        self.tools_container = "security-tools"  # Name of the tools container
    
    async def run_amass(self, domain: str, timeout: int = 300) -> Dict[str, Any]:
        """
        Run Amass subdomain enumeration
        """
        logger.info(f"Starting Amass scan for domain: {domain}")
        
        try:
            cmd = [
                "docker", "exec", self.tools_container,
                "amass", "enum",  "-passive" ,"-d", domain
            ]
            logger.debug(f"Executing Amass command: {' '.join(cmd)}")

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
            except asyncio.TimeoutError:
                logger.error(f"Amass scan for {domain} timed out after {timeout} seconds.")
                # Try to get whatever output is available before killing
                try:
                    process.kill()
                    stdout, stderr = await process.communicate()
                    output = stdout.decode().splitlines()
                    subdomains = [line.strip() for line in output if line.strip()]
                    logger.warning(f"Partial Amass results for {domain} due to timeout. Found {len(subdomains)} subdomains.")
                    return {
                        "success": True,
                        "tool": "amass",
                        "domain": domain,
                        "subdomains": subdomains,
                        "count": len(subdomains),
                        "partial": True,
                        "error": f"Timeout after {timeout} seconds"
                    }
                except Exception as e:
                    logger.error(f"Failed to retrieve partial Amass results after timeout: {e}")
                    return {"error": f"Amass scan for {domain} timed out and no results could be retrieved", "success": False}

            if process.returncode == 0:
                output = stdout.decode().splitlines()
                subdomains = [line.strip() for line in output if line.strip()]
                logger.info(f"Successfully processed Amass results for {domain}. Found {len(subdomains)} subdomains.")
                return {
                    "success": True,
                    "tool": "amass",
                    "domain": domain,
                    "subdomains": subdomains,
                    "count": len(subdomains)
                }
            else:
                error_message = stderr.decode().strip()
                logger.error(f"Amass failed for domain {domain}. Error: {error_message}")
                return {
                    "error": f"Amass failed: {error_message}",
                    "success": False
                }
                
        except Exception as e:
            logger.exception(f"Unhandled exception while trying to run Amass for {domain}") # Use exception for full traceback
            return {
                "error": f"Failed to run Amass: {str(e)}",
                "success": False
            }
    
    async def run_theharvester(self, domain: str, sources: str = "google,bing", timeout: int = 300) -> Dict[str, Any]:
        """
        Run theHarvester for information gathering
        """
        logger.info(f"Starting theHarvester scan for domain: {domain} with sources: {sources}")
        output_file_name = f"harvester_output_{domain.replace('.', '_')}.json" # Use _output_ for consistency
        tools_output_path = f"/home/tools/shared/{output_file_name}" 
        api_output_path = f"{self.shared_dir}/{output_file_name}" # Use self.shared_dir

        try:
            cmd = [
                "docker", "exec", self.tools_container,
                "python3", "/opt/theHarvester/theHarvester.py",
                "-d", domain,
                "-b", sources,
                "-f", tools_output_path # Specify the JSON output file directly
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
            except asyncio.TimeoutError:
                process.kill()
                logger.error(f"theHarvester scan for {domain} timed out after {timeout} seconds.")
                return {"error": "theHarvester scan timed out", "success": False} # Added success: False for consistency
            
            if process.returncode == 0:
                logger.info(f"theHarvester scan for {domain} completed successfully. Reading results from {api_output_path}")
                results = {"emails": [], "hosts": [], "ips": []}
                
                if os.path.exists(api_output_path):
                    try:
                        with open(api_output_path, 'r') as f:
                            file_results = json.load(f)
                            # theHarvester's JSON output structure might vary.
                            # Ensure you merge relevant fields, e.g., 'hosts', 'emails', 'ips'
                            if 'hosts' in file_results:
                                results['hosts'].extend(file_results['hosts'])
                            if 'emails' in file_results:
                                results['emails'].extend(file_results['emails'])
                            if 'ips' in file_results: # Assuming it might output IPs
                                results['ips'].extend(file_results['ips'])
                            # Add other relevant keys if theHarvester outputs them
                            
                        logger.debug(f"Successfully loaded JSON output from {api_output_path}")
                    except json.JSONDecodeError as jde:
                        logger.error(f"Error decoding JSON from theHarvester output {api_output_path}: {jde}")
                    except Exception as e: # Catch other file errors
                        logger.error(f"Error reading theHarvester output file {api_output_path}: {e}")
                    finally:
                        # Clean up the output file after reading
                        if os.path.exists(api_output_path):
                            os.remove(api_output_path)
                            logger.debug(f"Removed theHarvester output file: {api_output_path}")
                else:
                    logger.warning(f"theHarvester JSON output file not found at {api_output_path}. Relying on stdout.")

                output_text = stdout.decode().strip() # Capture stdout even on success
                if output_text:
                    logger.debug(f"theHarvester stdout for {domain}: {output_text}")

                logger.info(f"Successfully processed theHarvester results for {domain}.")
                return {
                    "success": True,
                    "tool": "theHarvester",
                    "domain": domain,
                    "sources": sources,
                    "results": results,
                    "raw_output": output_text
                }
            else:
                error_message = stderr.decode().strip()
                logger.error(f"theHarvester failed for domain {domain}. Error: {error_message}")
                # Also log stdout if available, as theHarvester can print errors there too
                if stdout.strip():
                    logger.error(f"theHarvester stdout during failure for {domain}: {stdout.decode().strip()}")
                return {
                    "error": f"theHarvester failed: {error_message}",
                    "success": False
                }
                
        except Exception as e:
            logger.exception(f"Unhandled exception while trying to run theHarvester for {domain}") # Use exception for full traceback
            return {
                "error": f"Failed to run theHarvester: {str(e)}",
                "success": False
            }
    
    async def run_combined_scan(self, domain: str) -> Dict[str, Any]:
        """
        Run both tools and combine results
        """
        logger.info(f"Starting combined scan for domain: {domain}")
        # Run tasks concurrently
        amass_task = self.run_amass(domain)
        theharvester_task = self.run_theharvester(domain)

        amass_results, harvester_results = await asyncio.gather(amass_task, theharvester_task)

        results = {
            "domain": domain,
            "amass": amass_results,
            "theharvester": harvester_results
        }
        
        logger.info(f"Combined scan for domain: {domain} completed.")
        return results