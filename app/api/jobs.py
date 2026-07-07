# from fastapi import APIRouter, Depends, Query

# from app.common.responses import ApiResponse
# from app.core.dependencies import get_job_service
# from app.services.job_service import JobService

# router = APIRouter(prefix="/jobs", tags=["Jobs"])


# @router.get("/search")
# async def search_jobs(
#     keyword: str = Query(..., min_length=2),
#     location: str = Query(""),
#     max_results: int = Query(20, ge=1, le=50),
#     job_service: JobService = Depends(get_job_service),
# ):
#     """
#     Searches Naukri for jobs matching the keyword/location,
#     stores new results, and returns them.
#     """
#     jobs = await job_service.search_naukri(
#         keyword=keyword,
#         location=location,
#         max_results=max_results,
#     )

#     return ApiResponse.success(
#         message=f"Found {len(jobs)} job(s).",
#         data=[job.model_dump(mode="json") for job in jobs],
#     )

from fastapi import APIRouter, Depends, Query

from app.common.responses import ApiResponse
from app.core.dependencies import get_job_service
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/search")
async def search_jobs(
    keyword: str = Query(..., min_length=2),
    location: str = Query(""),
    max_results: int = Query(20, ge=1, le=50),
    job_service: JobService = Depends(get_job_service),
):
    jobs = await job_service.search_naukri(
        keyword=keyword,
        location=location,
        max_results=max_results,
    )

    return ApiResponse.success(
        message=f"Found {len(jobs)} job(s).",
        data=[job.model_dump(mode="json") for job in jobs],
    )


@router.post("/{job_id}/analyze")
async def analyze_job(
    job_id: int,
    job_service: JobService = Depends(get_job_service),
):
    """
    Runs the LLM job analyzer on a stored job description.
    Extracts skills, seniority, responsibilities, and keywords.
    """
    result = await job_service.analyze_job(job_id)

    return ApiResponse.success(
        message="Job analyzed successfully.",
        data=result.model_dump(mode="json"),
    )