from fastapi import APIRouter, Depends, Query

from app.common.responses import ApiResponse
from app.core.dependencies import get_auto_apply_service, get_current_user_id
from app.services.auto_apply_service import AutoApplyService

router = APIRouter(prefix="/auto-apply", tags=["Auto Apply"])


@router.post("/run")
async def run_auto_apply(
    resume_id: int = Query(...),
    keyword: str = Query(..., min_length=2),
    location: str = Query(""),
    max_jobs: int = Query(10, ge=1, le=20),
    threshold: int = Query(70, ge=0, le=100),
    user_id: int = Depends(get_current_user_id),
    auto_apply_service: AutoApplyService = Depends(get_auto_apply_service),
):
    """
    The autonomous pipeline.
    Searches jobs, matches against resume, applies to those above threshold.
    Tracks every attempt in the applications table.
    """
    summary = await auto_apply_service.run(
        user_id=user_id,
        resume_id=resume_id,
        keyword=keyword,
        location=location,
        max_jobs=max_jobs,
        threshold=threshold,
    )

    return ApiResponse.success(
        message="Auto apply pipeline complete.",
        data=summary,
    )