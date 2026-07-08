from sqlalchemy.orm import Session

from app.models.application import Application
from app.repositories.base_repository import BaseRepository


class ApplicationRepository(BaseRepository):

    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, application: Application) -> Application:
        return self.add(application)

    def get_by_id(self, application_id: int) -> Application | None:
        return (
            self.db.query(Application)
            .filter(Application.id == application_id)
            .first()
        )

    def get_by_user(self, user_id: int) -> list[Application]:
        return (
            self.db.query(Application)
            .filter(Application.user_id == user_id)
            .order_by(Application.created_at.desc())
            .all()
        )

    def get_by_resume_and_job(
        self,
        resume_id: int,
        job_id: int,
    ) -> Application | None:
        return (
            self.db.query(Application)
            .filter(
                Application.resume_id == resume_id,
                Application.job_id == job_id,
            )
            .first()
        )

    def get_by_status(
        self,
        user_id: int,
        status: str,
    ) -> list[Application]:
        return (
            self.db.query(Application)
            .filter(
                Application.user_id == user_id,
                Application.status == status,
            )
            .all()
        )

    def get_stats(self, user_id: int) -> dict:
        applications = self.get_by_user(user_id)
        total = len(applications)

        stats = {
            "total": total,
            "applied": 0,
            "interview": 0,
            "rejected": 0,
            "offer": 0,
            "pending": 0,
            "failed": 0,
        }

        for app in applications:
            status = app.status.lower()
            if status in stats:
                stats[status] += 1

        stats["success_rate"] = (
            round((stats["interview"] + stats["offer"]) / total * 100, 1)
            if total > 0
            else 0.0
        )

        return stats