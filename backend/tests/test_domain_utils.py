import pytest
from app.routers.domain.domain import deduplicate_results, aggregate_total_results

def test_deduplicate_results():
    """Test deduplicate_results function"""
    input_data = {
        "emails": ["test@example.com", "test@example.com", "other@example.com"],
        "subdomains": ["sub1.example.com", "sub1.example.com", "sub2.example.com"],
        "hosts": ["host1", "host2", "host1"],
        "ips": ["1.1.1.1", "2.2.2.2", "1.1.1.1"]
    }
    
    result = deduplicate_results(input_data)
    
    assert len(result["emails"]) == 2
    assert len(result["subdomains"]) == 2
    assert len(result["hosts"]) == 2
    assert len(result["ips"]) == 2
    assert "test@example.com" in result["emails"]
    assert "other@example.com" in result["emails"]

def test_deduplicate_results_empty():
    """Test deduplicate_results with empty data"""
    input_data = {
        "emails": [],
        "subdomains": [],
        "hosts": [],
        "ips": []
    }
    
    result = deduplicate_results(input_data)
    
    assert len(result["emails"]) == 0
    assert len(result["subdomains"]) == 0

def test_deduplicate_results_missing_keys():
    """Test deduplicate_results with missing keys"""
    input_data = {
        "emails": ["test@example.com"]
        # missing other keys
    }
    
    result = deduplicate_results(input_data)
    
    assert len(result["emails"]) == 1
    # Should not crash on missing keys

class MockScan:
    def __init__(self, theharvester=None, amass=None, subfinder=None):
        self.theharvester = theharvester
        self.amass = amass
        self.subfinder = subfinder

def test_aggregate_total_results():
    """Test aggregate_total_results function"""
    mock_scan = MockScan(
        theharvester={"subdomains": ["sub1.com", "sub2.com"], "emails": ["test@example.com"]},
        amass={"subdomains": ["sub3.com"], "emails": []},
        subfinder={"subdomains": ["sub4.com", "sub5.com"], "emails": []}
    )
    
    result = aggregate_total_results(mock_scan)
    
    assert result["total_subdomains"] == 5  # 2 + 1 + 2
    assert result["total_emails"] == 1
    assert result["total_hosts"] == 0
    assert result["total_ips"] == 0

def test_aggregate_total_results_null_tools():
    """Test aggregate_total_results with null tools"""
    mock_scan = MockScan(
        theharvester=None,
        amass={"subdomains": ["sub1.com"]},
        subfinder=None
    )
    
    result = aggregate_total_results(mock_scan)
    
    assert result["total_subdomains"] == 1
    assert result["total_emails"] == 0