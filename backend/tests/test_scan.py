"""Tests for the scan endpoints using the in-process AI engine."""
def _auth_header(client, email="scanner@example.com"):
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Scanner", "password": "Password123!"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    ).json()
    return {"Authorization": f"Bearer {login['access_token']}"}


def test_text_scan_returns_result(client):
    h = _auth_header(client)
    r = client.post("/api/v1/scan/text", json={"text": "The quick brown fox jumps over the lazy dog."}, headers=h)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["modality"] == "text"
    assert data["status"] == "completed"
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["label"] in {"human", "ai_generated", "suspicious"}


def test_history_returns_scans(client):
    h = _auth_header(client)
    for i in range(3):
        client.post("/api/v1/scan/text", json={"text": f"Sample text {i}."}, headers=h)
    r = client.get("/api/v1/scan/history", headers=h)
    assert r.status_code == 200
    assert r.json()["total"] >= 3


def test_history_requires_auth(client):
    r = client.get("/api/v1/scan/history")
    assert r.status_code == 401


def test_admin_stats_requires_admin(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "admin@example.com", "full_name": "Admin", "password": "Password123!"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "Password123!"},
    ).json()
    h = {"Authorization": f"Bearer {login['access_token']}"}
    r = client.get("/api/v1/admin/stats", headers=h)
    assert r.status_code == 200
    assert "scans" in r.json()
