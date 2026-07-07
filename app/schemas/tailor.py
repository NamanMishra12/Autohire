from pydantic import BaseModel


class TailorRequest(BaseModel):
    resume_id: int
    job_id: int


class TailorResponse(BaseModel):
    resume_id: int
    job_id: int
    job_title: str
    score_before: int
    match_level_before: str
    summary: str
    skills: list[str]
    experience_highlights: list[str]
    improvements: list[str]