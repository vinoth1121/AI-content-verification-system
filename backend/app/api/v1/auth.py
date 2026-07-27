"""Auth router: register / login / refresh / me."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, DbSession
from app.core.rate_limit import limiter
from app.core.security import decode_token
from app.models.user import User
from app.schemas.auth import RefreshRequest, TokenPair, UserCreate, UserLogin, UserOut
from app.services.auth_service import AuthError, login, register, to_user_out

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def register_endpoint(payload: UserCreate, request: Request, response: Response, db: DbSession):
    try:
        user, access, refresh = register(db, payload)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return TokenPair(access_token=access, refresh_token=refresh, user=to_user_out(user))


@router.post("/login", response_model=TokenPair)
@limiter.limit("10/minute")
def login_endpoint(payload: UserLogin, request: Request, response: Response, db: DbSession):
    try:
        user, access, refresh = login(db, payload.email, payload.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return TokenPair(access_token=access, refresh_token=refresh, user=to_user_out(user))


@router.post("/refresh", response_model=TokenPair)
@limiter.limit("30/minute")
def refresh_endpoint(payload: RefreshRequest, request: Request, response: Response, db: DbSession):
    try:
        claims = decode_token(payload.refresh_token)
        if claims.get("type") != "refresh":
            raise JWTError("not a refresh token")
        user = db.get(User, int(claims["sub"]))
        if not user or not user.is_active:
            raise JWTError("user not found")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    from app.core.security import create_token_pair
    access, refresh = create_token_pair(str(user.id), extra_claims={"role": user.role.value})
    return TokenPair(access_token=access, refresh_token=refresh, user=to_user_out(user))


@router.get("/me", response_model=UserOut)
def me_endpoint(user: CurrentUser):
    return to_user_out(user)
