from fastapi import APIRouter, Depends

from app.common.responses import ApiResponse
from app.core.dependencies import get_tailor_service
from app.services.tailor_service import TailorService

router = APIRouter(prefix="/tailor", tags=["Tailor"])


@router.post("/resume/{resume_id}/job/{job_id}")
async def tailor_resume(
    resume_id: int,
    job_id: int,
    tailor_service: TailorService = Depends(get_tailor_service),
):
    """
    Tailors a resume for a specific job.
    Runs job analysis + matching first, then rewrites resume content
    to highlight relevant experience and address skill gaps.
    """
    result = await tailor_service.tailor_resume(
        resume_id=resume_id,
        job_id=job_id,
    )

    return ApiResponse.success(
        message="Resume tailored successfully.",
        data=result.model_dump(mode="json"),
    )