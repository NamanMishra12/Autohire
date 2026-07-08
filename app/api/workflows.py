from fastapi import APIRouter, Depends, Query

from app.common.responses import ApiResponse
from app.core.dependencies import get_current_user_id
from app.workflows.apply_workflow import apply_workflow
from app.workflows.search_workflow import search_workflow

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.post("/search")
async def run_search_workflow(
    resume_id: int = Query(...),
    keyword: str = Query(..., min_length=2),
    location: str = Query(""),
    max_results: int = Query(10, ge=1, le=20),
    threshold: int = Query(70, ge=0, le=100),
    user_id: int = Depends(get_current_user_id),
):
    """
    Runs the full LangGraph search workflow:
    load_resume → search_jobs → analyze_jobs → match_jobs

    Returns ranked jobs with scores and match analysis.
    """
    initial_state = {
        "resume_id": resume_id,
        "user_id": user_id,
        "keyword": keyword,
        "location": location,
        "max_results": max_results,
        "threshold": threshold,
        "resume_text": "",
        "raw_jobs": [],
        "analyzed_jobs": [],
        "matched_jobs": [],
        "errors": [],
    }

    final_state = await search_workflow.ainvoke(initial_state)

    return ApiResponse.success(
        message=f"Search workflow complete. Found {len(final_state['matched_jobs'])} matched jobs.",
        data={
            "keyword": keyword,
            "location": location,
            "jobs_found": len(final_state["raw_jobs"]),
            "jobs_matched": len(final_state["matched_jobs"]),
            "threshold": threshold,
            "results": final_state["matched_jobs"],
            "errors": final_state["errors"],
        },
    )


@router.post("/apply")
async def run_apply_workflow(
    resume_id: int = Query(...),
    keyword: str = Query(..., min_length=2),
    location: str = Query(""),
    max_jobs: int = Query(10, ge=1, le=20),
    threshold: int = Query(70, ge=0, le=100),
    user_id: int = Depends(get_current_user_id),
):
    """
    Runs the full LangGraph autonomous apply workflow:
    load_context → search_jobs → filter_and_match
    → generate_cover_letters → auto_apply

    This is the main autonomous pipeline.
    """
    initial_state = {
        "resume_id": resume_id,
        "user_id": user_id,
        "keyword": keyword,
        "location": location,
        "max_jobs": max_jobs,
        "threshold": threshold,
        "session_cookies": {},
        "resume_text": "",
        "resume_path": "",
        "user_profile": {},
        "raw_jobs": [],
        "processed_jobs": [],
        "results": [],
        "jobs_found": 0,
        "jobs_above_threshold": 0,
        "applications_attempted": 0,
        "applications_succeeded": 0,
        "applications_skipped": 0,
        "applications_failed": 0,
        "errors": [],
    }

    final_state = await apply_workflow.ainvoke(initial_state)

    return ApiResponse.success(
        message="Apply workflow complete.",
        data={
            "resume_id": resume_id,
            "keyword": keyword,
            "location": location,
            "threshold": threshold,
            "jobs_found": final_state["jobs_found"],
            "jobs_above_threshold": final_state["jobs_above_threshold"],
            "applications_attempted": final_state["applications_attempted"],
            "applications_succeeded": final_state["applications_succeeded"],
            "applications_skipped": final_state["applications_skipped"],
            "applications_failed": final_state["applications_failed"],
            "results": final_state["results"],
            "errors": final_state["errors"],
        },
    )