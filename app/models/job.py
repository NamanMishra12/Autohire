from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Job(Base):

    __tablename__ = "jobs"

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_job_source_external_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    source: Mapped[str] = mapped_column(String(30), nullable=False)

    external_id: Mapped[str] = mapped_column(String(100), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    company: Mapped[str] = mapped_column(String(255), nullable=True)

    location: Mapped[str] = mapped_column(String(255), nullable=True)

    experience: Mapped[str] = mapped_column(String(100), nullable=True)

    salary: Mapped[str] = mapped_column(String(100), nullable=True)

    skills: Mapped[str] = mapped_column(Text, nullable=True)

    posted_label: Mapped[str] = mapped_column(String(100), nullable=True)

    job_url: Mapped[str] = mapped_column(String(500), nullable=True)

    description: Mapped[str] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )