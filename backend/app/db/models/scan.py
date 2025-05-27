# app/db/models/scan.py
from sqlalchemy import Column, Enum, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base 
from datetime import datetime  
import uuid
from enum import Enum

class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"
    CANCELLED = "cancelled"
    
class Scan(Base):
    __tablename__ = "scans"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    domain = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)  # pending, running, finished, error, cancelled
    
    # Tool results stored as JSON
    theharvester = Column(JSON, nullable=True)
    amass = Column(JSON, nullable=True)
    subfinder = Column(JSON, nullable=True)
    summary = Column(JSON, nullable=True)
    
    
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Metadata for quick access
    total_subdomains = Column(Integer, default=0)
    total_emails = Column(Integer, default=0)
    total_ips = Column(Integer, default=0)
    total_hosts = Column(Integer, default=0)  
    # Scan timing
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # Calculated duration for quick queries
    
    # User relationship (optional - if you want to track which user started the scan)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    user = relationship("User", back_populates="scans")
    
    # Scan configuration
    tools_enabled = Column(JSON, default=lambda: {"theharvester": True, "amass": True, "subfinder": True})  # Which tools to run
    scan_options = Column(JSON, nullable=True)  # Additional scan options/parameters
    
    # Status flags
    is_active = Column(Boolean, default=True)  # For soft deletion
    is_public = Column(Boolean, default=False)  # If results can be shared publicly
    
    # Audit fields following your user model pattern
    created_by = Column(String(255), nullable=True)
    created_date = Column(DateTime, default=datetime.now, nullable=True)
    updated_by = Column(String(255), nullable=True)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=True)

    def __repr__(self):
        return f"<Scan(id='{self.id}', domain='{self.domain}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert scan to dictionary for API responses"""
        return {
            "scan_id": self.id,
            "domain": self.domain,
            "status": self.status,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_seconds": self.duration_seconds,
            "theHarvester": self.theharvester,
            "amass": self.amass,
            "subfinder": self.subfinder,
            "summary": self.summary,
            "error": self.error_message,
            "total_subdomains": self.total_subdomains,
            "total_emails": self.total_emails,
            "total_ips": self.total_ips,
            "total_hosts": self.total_hosts,
            "tools_enabled": self.tools_enabled,
            "scan_options": self.scan_options,
            "is_public": self.is_public,
            "user_id": self.user_id,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "updated_date": self.updated_date.isoformat() if self.updated_date else None
        }
    
    def calculate_duration(self):
        """Calculate and update duration if scan is finished"""
        if self.started_at and self.finished_at:
            duration = (self.finished_at - self.started_at).total_seconds()
            self.duration_seconds = int(duration)
            return duration
        return None
    
    @property
    def is_completed(self):
        """Check if scan is in a completed state"""
        return self.status in ["finished", "error", "cancelled"]
    
    @property
    def is_running(self):
        """Check if scan is currently running"""
        return self.status == "running"
    
    @property 
    def has_results(self):
        """Check if scan has any results"""
        return (self.theharvester is not None or 
                self.amass is not None
                or self.subfinder is not None)
    
    def get_success_rate(self):
        """Calculate success rate of enabled tools"""
        if not self.tools_enabled:
            return 0.0
            
        total_tools = sum(1 for enabled in self.tools_enabled.values() if enabled)
        if total_tools == 0:
            return 0.0
            
        successful_tools = 0
        
        if self.tools_enabled.get("theharvester") and self.theharvester:
            if not self.theharvester.get("error"):
                successful_tools += 1
                
        if self.tools_enabled.get("amass") and self.amass:
            if not self.amass.get("error"):
                successful_tools += 1
                
        if self.tools_enabled.get("subfinder") and self.subfinder:
            if not self.subfinder.get("error"):
                successful_tools += 1
                
        return (successful_tools / total_tools) * 100