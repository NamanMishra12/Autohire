from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApplicationResponse(BaseModel):

    id: int
    user_id: int
    resume_id: int
    job_id: int
    status: str
    apply_method: str
    match_score: float | None
    match_level: str | None
    cover_letter_used: bool
    auto_apply_attempted: bool
    auto_apply_success: bool
    failure_reason: str | None
    applied_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationStatusUpdate(BaseModel):
    status: str


class ApplicationCreate(BaseModel):
    resume_id: int
    job_id: int
    match_score: float | None = None
    match_level: str | None = None
    cover_letter_used: bool = False
    apply_method: str = "MANUAL"