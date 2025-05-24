from fastapi.testclient import TestClient

from app.main import app
from app.utilities.static_values import RATE_LIMIT_EXCEED

client = TestClient(app)

BASE_PATH = "/v1/utils"


def test_api_status() -> None:
    """
    Test API status
    """
    r = client.get(f"{BASE_PATH}/api-status")
    assert r.status_code == 200
    assert r.json()["status"] == "success"


