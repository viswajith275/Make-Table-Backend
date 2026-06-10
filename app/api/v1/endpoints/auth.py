from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.config import settings
from app.core.security import create_token
from app.core.rate_limiter import limiter
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UsersResponse,
    PasswordUpdationRequest,
    UserUpdate,
)
from app.services import user_service

"""
google_sso = GoogleSSO(
    client_id=settings.google_client_key,
    client_secret=settings.google_client_secret,
    redirect_uri="http://localhost:8000/google/callback",  # change to actual endpoint in production
    allow_insecure_http=True,  # Must be set to false in production
)
"""
router = APIRouter()


@router.get("/me", response_model=UsersResponse)
async def read_user_me(current_user: User = Depends(deps.get_current_active_user)):
    return current_user


"""
@router.get("/google/login")
async def google_login():
    return await google_sso.get_login_redirect()
"""


@router.patch("/change-password")
@limiter.limit("1/minute")
async def change_user_password(
    request: Request,
    password_patch: PasswordUpdationRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await user_service.update_user_password(
        db=db, password_patch=password_patch, user_id=current_user.id
    )


@router.patch("/change-username", response_model=UsersResponse)
@limiter.limit("1/minute")
async def change_username(
    request: Request,
    user_patch: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await user_service.update_username(
        db=db, user_patch=user_patch, user_id=current_user.id
    )


@router.post(
    "/register", response_model=UsersResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("10/minute")
async def create_user(
    request: Request, user_in: UserCreate, db: AsyncSession = Depends(deps.get_db)
):

    return await user_service.create_user(db=db, user_in=user_in)


@router.post("/login", response_model=UsersResponse)
@limiter.limit("10/minute")
async def login_user(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(deps.get_db),
):
    user = await user_service.authenticate_user(
        username=form_data.username, password=form_data.password, db=db
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password!",
        )

    token = await deps.create_refresh_token(db=db, user_id=user.id)

    access_token = create_token(
        user_id=user.id,
        token_type="access",
        expires_time=timedelta(minutes=settings.access_token_expire_minutes),
    )

    refresh_token = create_token(
        user_id=user.id,
        token_type="refresh",
        expires_time=timedelta(days=settings.refresh_token_expire_days),
        unique_id=str(token.id),
        secret=token.refresh_key,
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=True,
        samesite="none",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
    )

    return user


@router.post("/refresh")
@limiter.limit("1/minute")
async def refresh_tokens(
    request: Request, response: Response, db: AsyncSession = Depends(deps.get_db)
):

    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing!"
        )

    user_id = await deps.validate_refresh_token(refresh_token=refresh_token, db=db)

    access_token = create_token(
        user_id=user_id,
        token_type="access",
        expires_time=timedelta(minutes=settings.access_token_expire_minutes),
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=True,
        samesite="none",
    )

    return {"message": "Token refreshed"}


@router.post("/logout")
async def logout_user(
    request: Request, response: Response, db: AsyncSession = Depends(deps.get_db)
):

    refresh_token = request.cookies.get("refresh_token")

    await deps.delete_refresh_token(refresh_token=refresh_token, db=db)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "Logged out successfully"}
