from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Application(Base):

    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    resume_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("resumes.id"),
        nullable=False,
    )

    job_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING",
        nullable=False,
    )

    apply_method: Mapped[str] = mapped_column(
        String(20),
        default="MANUAL",
        nullable=False,
    )

    match_score: Mapped[float] = mapped_column(Float, nullable=True)

    match_level: Mapped[str] = mapped_column(String(20), nullable=True)

    cover_letter_used: Mapped[bool] = mapped_column(Boolean, default=False)

    auto_apply_attempted: Mapped[bool] = mapped_column(Boolean, default=False)

    auto_apply_success: Mapped[bool] = mapped_column(Boolean, default=False)

    failure_reason: Mapped[str] = mapped_column(Text, nullable=True)

    applied_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )