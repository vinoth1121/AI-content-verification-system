"""Auth service: registration, login, refresh."""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_token_pair, hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.auth import UserCreate, UserOut


class AuthError(Exception):
    """Raised on invalid credentials or email conflict."""


def _record_auth_outcome(outcome: str) -> None:
    try:
        from app.core.metrics import auth_attempts_total
        auth_attempts_total.labels(outcome=outcome).inc()
    except Exception:
        pass


def register(db: Session, payload: UserCreate) -> tuple[User, str, str]:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        _record_auth_outcome("email_conflict")
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

    _record_auth_outcome("register_success")
    access, refresh = create_token_pair(str(user.id), extra_claims={"role": user.role.value})
    return user, access, refresh


def login(db: Session, email: str, password: str) -> tuple[User, str, str]:
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        _record_auth_outcome("unknown_user")
        raise AuthError("Invalid email or password")
    if not verify_password(password, user.hashed_password):
        _record_auth_outcome("bad_password")
        raise AuthError("Invalid email or password")
    if not user.is_active:
        _record_auth_outcome("disabled")
        raise AuthError("Account disabled")

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    _record_auth_outcome("success")
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
