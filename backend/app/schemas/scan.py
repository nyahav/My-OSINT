from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"
    CANCELLED = "cancelled"

class ScanBase(BaseModel):
    domain: str = Field(..., description="The domain being scanned.")
    tools_enabled: Optional[Dict[str, bool]] = Field(
        default_factory=lambda: {"theharvester": True, "amass": True, "subfinder": True},
        description="Dictionary indicating which tools are enabled for the scan."
    )
    scan_options: Optional[Dict[str, Any]] = Field(None, description="Additional scan options or parameters.")
    user_id: Optional[int] = Field(None, description="ID of the user who initiated the scan.")
    is_public: bool = Field(False, description="Whether the scan results can be publicly shared.")

class ScanCreate(ScanBase):
    """Schema for creating a new scan."""
    pass 

class ScanUpdate(BaseModel):
    """Schema for updating an existing scan."""
    status: Optional[ScanStatus] = Field(None, description="Current status of the scan.")
    theharvester: Optional[Dict[str, Any]] = Field(None, description="Results from TheHarvester tool.")
    amass: Optional[Dict[str, Any]] = Field(None, description="Results from Amass tool.")
    subfinder: Optional[Dict[str, Any]] = Field(None, description="Results from subfinder tool.")
    summary: Optional[Dict[str, Any]] = Field(None, description="Summary of the scan results.")
    error_message: Optional[str] = Field(None, description="Error message if the scan failed.")
    total_subdomains: Optional[int] = Field(0, description="Total number of subdomains found.")
    total_emails: Optional[int] = Field(0, description="Total number of emails found.")
    total_ips: Optional[int] = Field(0, description="Total number of IPs found.")
    total_hosts: Optional[int] = Field(0, description="Total number of hosts found.")
    started_at: Optional[datetime] = Field(None, description="Timestamp when the scan started.")
    finished_at: Optional[datetime] = Field(None, description="Timestamp when the scan finished.")
    is_public: Optional[bool] = Field(None, description="Whether the scan results can be publicly shared.")
    tools_enabled: Optional[Dict[str, bool]] = Field(None, description="Updated tools enabled for the scan.")
    scan_options: Optional[Dict[str, Any]] = Field(None, description="Updated additional scan options/parameters.")
    is_active: Optional[bool] = Field(None, description="Flag for soft deletion.")

class ScanOut(ScanBase):
    """Schema for returning scan details (read-only)."""
    scan_id: str = Field(..., alias="id", description="Unique identifier of the scan.")  
    status: ScanStatus = Field(..., description="Current status of the scan.")
    created_date: datetime = Field(..., description="Timestamp when the scan record was created.")
    started_at: Optional[datetime] = Field(None, description="Timestamp when the scan started.")
    finished_at: Optional[datetime] = Field(None, description="Timestamp when the scan finished.")
    duration_seconds: Optional[int] = Field(None, description="Duration of the scan in seconds.")
    theharvester: Optional[Dict[str, Any]] = Field(None, alias="theharvester_results", description="Results from TheHarvester tool.")
    amass: Optional[Dict[str, Any]] = Field(None, alias="amass_results", description="Results from Amass tool.")
    subfinder: Optional[Dict[str, Any]] = Field(None, alias="subfinder_results", description="Results from subfinder tool.")
    
    
    summary: Optional[Dict[str, Any]] = Field(None, description="Summary of the scan results.")
    error: Optional[str] = Field(None, alias="error_message", description="Error message if the scan failed.")
    total_subdomains: int = Field(..., description="Total number of subdomains found.")
    total_emails: int = Field(..., description="Total number of emails found.")
    total_ips: int = Field(..., description="Total number of IPs found.")
    total_hosts: int = Field(..., description="Total number of hosts found.")
    is_active: bool = Field(..., description="Indicates if the scan record is active (not soft-deleted).")
    created_by: Optional[str] = Field(None, description="User who created the scan record.")
    updated_by: Optional[str] = Field(None, description="Last user who updated the scan record.")
    updated_date: Optional[datetime] = Field(None, description="Timestamp of the last update.")
    
    class Config:
        from_attributes = True 
        
        use_enum_values = True 