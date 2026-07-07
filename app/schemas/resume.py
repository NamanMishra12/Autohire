from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class ResumeResponse(BaseModel):

    id: int

    original_filename: str

    version: int

    parsed: bool

    parsing_status: str

    embedding_generated: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )