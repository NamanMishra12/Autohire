from fastapi import APIRouter, Depends

from app.common.responses import ApiResponse
from app.core.dependencies import get_application_service, get_current_user_id
from app.schemas.application import ApplicationCreate, ApplicationStatusUpdate
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("")
def create_application(
    payload: ApplicationCreate,
    user_id: int = Depends(get_current_user_id),
    application_service: ApplicationService = Depends(get_application_service),
):
    """
    Manually track a new job application.
    """
    result = application_service.create_application(
        user_id=user_id,
        payload=payload,
    )

    return ApiResponse.success(
        message="Application tracked successfully.",
        data=result.model_dump(mode="json"),
    )


@router.get("")
def get_applications(
    user_id: int = Depends(get_current_user_id),
    application_service: ApplicationService = Depends(get_application_service),
):
    """
    Get all applications for the current user.
    """
    results = application_service.get_applications(user_id=user_id)

    return ApiResponse.success(
        message=f"Found {len(results)} application(s).",
        data=[r.model_dump(mode="json") for r in results],
    )


@router.get("/stats")
def get_stats(
    user_id: int = Depends(get_current_user_id),
    application_service: ApplicationService = Depends(get_application_service),
):
    """
    Returns application statistics — total, applied, interviews,
    rejections, success rate.
    """
    stats = application_service.get_stats(user_id=user_id)

    return ApiResponse.success(
        message="Application stats retrieved.",
        data=stats,
    )


@router.get("/{application_id}")
def get_application(
    application_id: int,
    application_service: ApplicationService = Depends(get_application_service),
):
    result = application_service.get_application(application_id)

    return ApiResponse.success(
        message="Application retrieved.",
        data=result.model_dump(mode="json"),
    )


@router.patch("/{application_id}/status")
def update_status(
    application_id: int,
    payload: ApplicationStatusUpdate,
    application_service: ApplicationService = Depends(get_application_service),
):
    """
    Update application status — APPLIED, INTERVIEW, REJECTED, OFFER.
    """
    result = application_service.update_status(
        application_id=application_id,
        status=payload.status,
    )

    return ApiResponse.success(
        message="Application status updated.",
        data=result.model_dump(mode="json"),
    )