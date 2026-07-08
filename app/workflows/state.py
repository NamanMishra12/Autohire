from typing import Any
from typing_extensions import TypedDict


class SearchWorkflowState(TypedDict):
    """State for the job search workflow."""
    resume_id: int
    user_id: int
    keyword: str
    location: str
    max_results: int

    # Populated by nodes
    resume_text: str
    raw_jobs: list[dict]
    analyzed_jobs: list[dict]
    matched_jobs: list[dict]
    threshold: int
    errors: list[str]


class ApplyWorkflowState(TypedDict):
    """State for the auto-apply workflow."""
    resume_id: int
    user_id: int
    keyword: str
    location: str
    max_jobs: int
    threshold: int
    session_cookies: dict

    # Populated by nodes
    resume_text: str
    resume_path: str
    user_profile: dict
    raw_jobs: list[dict]
    processed_jobs: list[dict]
    results: list[dict]

    # Summary counters
    jobs_found: int
    jobs_above_threshold: int
    applications_attempted: int
    applications_succeeded: int
    applications_skipped: int
    applications_failed: int
    errors: list[str]