"""Smoke tests for the auth flow."""
from app.core.security import hash_password
from app.models.user import User, UserRole


def _register(client, email="user@example.com", password="Password123!"):
    return client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Test User", "password": password},
    )


def test_register_returns_tokens(client):
    r = _register(client)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["user"]["email"] == "user@example.com"


def test_first_user_is_admin(client):
    r = _register(client, email="first@example.com")
    assert r.json()["user"]["role"] == "admin"


def test_second_user_is_not_admin(client):
    _register(client, email="first@example.com")
    r = _register(client, email="second@example.com")
    assert r.json()["user"]["role"] == "user"


def test_login_with_valid_credentials(client):
    _register(client, email="x@example.com", password="Password123!")
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "x@example.com", "password": "Password123!"},
    )
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_login_with_invalid_credentials(client):
    _register(client, email="x@example.com", password="Password123!")
    r = client.post(
        "/api/v1/auth/login",
        json={"email": "x@example.com", "password": "wrong"},
    )
    assert r.status_code == 401


def test_me_requires_auth(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


def test_me_returns_user(client):
    _register(client, email="me@example.com", password="Password123!")
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": "Password123!"},
    ).json()
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {login['access_token']}"})
    assert r.status_code == 200
    assert r.json()["email"] == "me@example.com"
