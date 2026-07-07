from fastapi import APIRouter, Depends

from app.common.responses import ApiResponse
from app.core.dependencies import get_cover_letter_service
from app.services.cover_letter_service import CoverLetterService

router = APIRouter(prefix="/cover-letter", tags=["Cover Letter"])


@router.post("/resume/{resume_id}/job/{job_id}")
async def generate_cover_letter(
    resume_id: int,
    job_id: int,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service),
):
    """
    Generates a personalized cover letter for a resume + job combination.
    Runs job analysis and matching first, then writes the cover letter.
    """
    result = await cover_letter_service.generate_cover_letter(
        resume_id=resume_id,
        job_id=job_id,
    )

    return ApiResponse.success(
        message="Cover letter generated successfully.",
        data=result.model_dump(mode="json"),
    )