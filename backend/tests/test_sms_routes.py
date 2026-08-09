import os

os.environ.setdefault("SESSION_SECRET", "test-secret")

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_sms_status_endpoint_is_available():
    response = client.get("/api/sms/status")
    assert response.status_code == 200
    body = response.json()
    assert "configured" in body
    assert "provider" in body
