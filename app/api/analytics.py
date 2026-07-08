from fastapi import APIRouter, Depends

from app.common.responses import ApiResponse
from app.core.dependencies import get_analytics_service, get_current_user_id
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
def get_dashboard(
    user_id: int = Depends(get_current_user_id),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Full dashboard data:
    application stats + job insights + weekly activity + skill gap summary.
    """
    result = analytics_service.get_dashboard(user_id)

    return ApiResponse.success(
        message="Dashboard data retrieved.",
        data=result.model_dump(mode="json"),
    )