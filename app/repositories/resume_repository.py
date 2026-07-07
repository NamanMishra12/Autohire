from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.repositories.base_repository import BaseRepository


class ResumeRepository(BaseRepository):

    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, resume: Resume) -> Resume:
        """
        Persist a new resume record.
        """
        return self.add(resume)

    def get_by_checksum(self, checksum: str) -> Resume | None:
        """
        Returns an existing resume having the given SHA256 checksum.
        Used to detect duplicate uploads.
        """
        return (
            self.db.query(Resume)
            .filter(Resume.checksum == checksum)
            .first()
        )

    def get_by_id(self, resume_id: int) -> Resume | None:
        """
        Fetch resume by primary key.
        """
        return (
            self.db.query(Resume)
            .filter(Resume.id == resume_id)
            .first()
        )

    def get_active_by_user(self, user_id: int):
        """
        Returns all active resumes of a user.
        """
        return (
            self.db.query(Resume)
            .filter(
                Resume.user_id == user_id,
                Resume.is_active.is_(True),
            )
            .order_by(Resume.created_at.desc())
            .all()
        )