"""Security primitives: password hashing, JWT issuance & verification.

Implements the OWASP ASVS V2 recommendations:
- Argon2id for password hashing (memory-hard, GPU-resistant)
- JWT for stateless auth with short-lived access + long-lived refresh
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Optional
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

# Argon2 is preferred; bcrypt kept as a fallback for legacy hashes.
_pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


# --------------------------------------------------------------------------- #
# Password hashing
# --------------------------------------------------------------------------- #
def hash_password(plain: str) -> str:
    """Hash a password using Argon2id."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    try:
        return _pwd_context.verify(plain, hashed)
    except Exception:
        return False


# --------------------------------------------------------------------------- #
# JWT
# --------------------------------------------------------------------------- #
TokenType = Literal["access", "refresh"]


def create_token(
    subject: str,
    token_type: TokenType,
    *,
    extra_claims: Optional[dict[str, Any]] = None,
) -> str:
    """Issue a signed JWT.

    Args:
        subject: usually the user id (str).
        token_type: "access" or "refresh".
        extra_claims: arbitrary claims to embed (e.g. roles).
    """
    now = datetime.now(timezone.utc)
    if token_type == "access":
        ttl = timedelta(minutes=settings.JWT_ACCESS_TTL_MINUTES)
    else:
        ttl = timedelta(days=settings.JWT_REFRESH_TTL_DAYS)

    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
        "jti": uuid4().hex,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode & verify a JWT. Raises `JWTError` on failure."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])


def create_token_pair(subject: str, extra_claims: Optional[dict] = None) -> tuple[str, str]:
    """Convenience: issue (access, refresh) pair."""
    return (
        create_token(subject, "access", extra_claims=extra_claims),
        create_token(subject, "refresh", extra_claims=extra_claims),
    )
