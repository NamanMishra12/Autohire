from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(150))

    email: Mapped[str] = mapped_column(String(150), unique=True)

    phone: Mapped[str] = mapped_column(String(20), nullable=True)

    location: Mapped[str] = mapped_column(String(150), nullable=True)

    linkedin_url: Mapped[str] = mapped_column(String(255), nullable=True)

    portfolio_url: Mapped[str] = mapped_column(String(255), nullable=True)

    years_of_experience: Mapped[int] = mapped_column(Integer, nullable=True)

    # Encrypted session cookies per platform
    linkedin_cookies_encrypted: Mapped[str] = mapped_column(Text, nullable=True)

    indeed_cookies_encrypted: Mapped[str] = mapped_column(Text, nullable=True)

    naukri_cookies_encrypted: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )