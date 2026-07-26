"""Auth service: registration, login, refresh.

All password handling happens here — routers never touch hashes directly.
"""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_token_pair, hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.auth import UserCreate, UserOut


class AuthError(Exception):
    """Raised on invalid credentials or email conflict."""


def register(db: Session, payload: UserCreate) -> tuple[User, str, str]:
    """Create a new user. First user automatically becomes admin."""
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise AuthError("Email already registered")

    is_first_user = db.scalar(select(User.id)) is None
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=UserRole.admin if is_first_user else UserRole.user,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access, refresh = create_token_pair(str(user.id), extra_claims={"role": user.role.value})
    return user, access, refresh


def login(db: Session, email: str, password: str) -> tuple[User, str, str]:
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.hashed_password):
        raise AuthError("Invalid email or password")
    if not user.is_active:
        raise AuthError("Account disabled")

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    access, refresh = create_token_pair(str(user.id), extra_claims={"role": user.role.value})
    return user, access, refresh


def to_user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
    )
