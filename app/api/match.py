from fastapi import APIRouter, Depends

from app.common.responses import ApiResponse
from app.core.dependencies import get_match_service
from app.services.match_service import MatchService

router = APIRouter(prefix="/match", tags=["Match"])


@router.post("/resume/{resume_id}/job/{job_id}")
async def match_resume_to_job(
    resume_id: int,
    job_id: int,
    match_service: MatchService = Depends(get_match_service),
):
    """
    Scores a resume against a job description.
    Returns compatibility score, matching skills, gaps, and recommendation.
    """
    result = await match_service.match_resume_to_job(
        resume_id=resume_id,
        job_id=job_id,
    )

    return ApiResponse.success(
        message="Match analysis complete.",
        data=result.model_dump(mode="json"),
    )