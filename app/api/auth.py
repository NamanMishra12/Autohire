from fastapi import APIRouter, Depends

from app.common.responses import ApiResponse
from app.core.dependencies import get_auth_service
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new user. Returns access + refresh tokens."""
    result = auth_service.register(
        name=payload.name,
        email=payload.email,
        password=payload.password,
    )
    return ApiResponse.success(
        message="Registration successful.",
        data=result.model_dump(),
    )


@router.post("/login")
def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Login with email + password. Returns access + refresh tokens."""
    result = auth_service.login(
        email=payload.email,
        password=payload.password,
    )
    return ApiResponse.success(
        message="Login successful.",
        data=result.model_dump(),
    )


@router.post("/refresh")
def refresh(
    payload: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get new access token using refresh token."""
    result = auth_service.refresh(payload.refresh_token)
    return ApiResponse.success(
        message="Token refreshed.",
        data=result.model_dump(),
    )