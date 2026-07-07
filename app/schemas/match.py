from pydantic import BaseModel


class MatchResponse(BaseModel):

    resume_id: int
    job_id: int
    job_title: str
    score: int
    match_level: str
    matching_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    gaps: list[str]
    recommendation: str