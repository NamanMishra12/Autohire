from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    location: str | None
    linkedin_url: str | None
    portfolio_url: str | None
    years_of_experience: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None
    years_of_experience: int | None = None