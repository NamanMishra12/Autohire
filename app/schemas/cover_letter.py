from pydantic import BaseModel


class CoverLetterResponse(BaseModel):
    resume_id: int
    job_id: int
    job_title: str
    company: str
    score_before: int
    match_level_before: str
    subject: str
    opening_paragraph: str
    body_paragraph_1: str
    body_paragraph_2: str
    closing_paragraph: str
    full_cover_letter: str