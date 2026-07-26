"""FastAPI dependency providers: DB session, current user, RBAC.

Keeping these in one place makes the API routers thin and testable.
"""
from typing import Annotated, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import SessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# --------------------------------------------------------------------------- #
# DB session
# --------------------------------------------------------------------------- #
def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session and ensure it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]


# --------------------------------------------------------------------------- #
# Current user
# --------------------------------------------------------------------------- #
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbSession,
) -> User:
    """Resolve the JWT bearer to a User, raising 401 on any failure."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exc
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    user = db.get(User, int(user_id))
    if user is None or not user.is_active:
        raise credentials_exc
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


# --------------------------------------------------------------------------- #
# RBAC
# --------------------------------------------------------------------------- #
def require_admin(user: CurrentUser) -> User:
    """Dependency that only allows users with the `admin` role."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user


AdminUser = Annotated[User, Depends(require_admin)]
