import pytest
from datetime import datetime
from app.schemas.scan import ScanCreate, ScanOut

def test_scan_create_schema():
    """Test ScanCreate schema validation"""
    
    valid_scan = ScanCreate(
        domain="example.com",
        is_public=True
    )
    assert valid_scan.domain == "example.com"
    assert valid_scan.is_public == True

def test_scan_create_invalid_domain():
    """Test ScanCreate with invalid domain"""
    with pytest.raises(ValueError):
        ScanCreate(
            domain="invalid-domain-without-extension",
            is_public=True
        )

