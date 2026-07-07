from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobResponse(BaseModel):

    id: int

    source: str

    title: str

    company: str | None

    location: str | None

    experience: str | None

    salary: str | None

    skills: str | None

    posted_label: str | None

    job_url: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )