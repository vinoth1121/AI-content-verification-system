"""Tests for the observability + rate-limit features."""
from app.core.metrics import (
    http_requests_total,
    scans_completed_total,
    auth_attempts_total,
)


def _register_and_login(client, email="obs@example.com", password="Password123!"):
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Observer", "password": password},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    ).json()
    return {"Authorization": f"Bearer {login['access_token']}"}


def test_metrics_endpoint_returns_prometheus_format(client):
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "text/plain" in r.headers.get("content-type", "")
    text = r.text
    assert "acvs_http_requests_total" in text or "acvs_auth_attempts_total" in text


def test_metrics_endpoint_records_auth_attempts(client):
    auth_attempts_total.clear()
    client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "wrong"},
    )
    _register_and_login(client)
    r = client.get("/metrics")
    assert "acvs_auth_attempts_total" in r.text


def test_metrics_endpoint_records_scan_metrics(client):
    scans_completed_total.clear()
    h = _register_and_login(client, email="scan-metrics@example.com")
    client.post("/api/v1/scan/text", json={"text": "Hello world."}, headers=h)
    r = client.get("/metrics")
    text = r.text
    assert "acvs_scans_completed_total" in text
    assert "acvs_scan_duration_seconds" in text


def test_http_request_metrics_recorded(client):
    http_requests_total.clear()
    client.get("/health")
    client.get("/")
    r = client.get("/metrics")
    text = r.text
    assert "acvs_http_requests_total" in text
    assert "acvs_http_request_duration_seconds" in text


def test_health_endpoint_unauthenticated(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
