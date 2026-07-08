from fastapi import APIRouter, Depends

from app.common.responses import ApiResponse
from app.core.dependencies import get_current_user_id, get_user_service
from app.schemas.user import SessionCookieUpdate, UserProfileUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile")
def get_profile(
    user_id: int = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
):
    result = user_service.get_profile(user_id)
    return ApiResponse.success(
        message="Profile retrieved.",
        data=result.model_dump(mode="json"),
    )


@router.patch("/profile")
def update_profile(
    payload: UserProfileUpdate,
    user_id: int = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
):
    result = user_service.update_profile(user_id, payload)
    return ApiResponse.success(
        message="Profile updated.",
        data=result.model_dump(mode="json"),
    )


@router.post("/session-cookies")
def save_session_cookies(
    payload: SessionCookieUpdate,
    user_id: int = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
):
    """
    Save encrypted session cookies for a platform.
    User exports cookies from their browser using a cookie export extension,
    pastes the JSON here. Your app reuses the session to apply as that user.

    platform: linkedin | indeed | naukri
    cookies_json: JSON array of cookie objects from browser
    """
    result = user_service.save_session_cookies(user_id, payload)
    return ApiResponse.success(
        message=result["message"],
        data=result,
    )