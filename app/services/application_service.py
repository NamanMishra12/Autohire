from datetime import datetime

from sqlalchemy.orm import Session

from app.common.enums import ApplicationStatus, ApplyMethod
from app.exceptions.custome_exceptions import ResumeNotFoundException
from app.models.application import Application
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.application import ApplicationCreate, ApplicationResponse
from app.utils.logger import logger


class ApplicationService:
    """
    Tracks job applications — both manual and auto-applied.
    Central source of truth for application state.
    """

    def __init__(self, db: Session):
        self.db = db
        self.application_repository = ApplicationRepository(db)
        self.resume_repository = ResumeRepository(db)
        self.job_repository = JobRepository(db)

    def create_application(
        self,
        user_id: int,
        payload: ApplicationCreate,
    ) -> ApplicationResponse:

        resume = self.resume_repository.get_by_id(payload.resume_id)
        if not resume:
            raise ResumeNotFoundException(
                message=f"Resume with id {payload.resume_id} not found."
            )

        job = self.job_repository.get_by_id(payload.job_id)
        if not job:
            raise ResumeNotFoundException(
                message=f"Job with id {payload.job_id} not found."
            )

        existing = self.application_repository.get_by_resume_and_job(
            resume_id=payload.resume_id,
            job_id=payload.job_id,
        )

        if existing:
            logger.info(f"Application already exists for resume {payload.resume_id} / job {payload.job_id}")
            return ApplicationResponse.model_validate(existing)

        application = Application(
            user_id=user_id,
            resume_id=payload.resume_id,
            job_id=payload.job_id,
            status=ApplicationStatus.PENDING.value,
            apply_method=payload.apply_method,
            match_score=payload.match_score,
            match_level=payload.match_level,
            cover_letter_used=payload.cover_letter_used,
        )

        application = self.application_repository.create(application)

        return ApplicationResponse.model_validate(application)

    def get_applications(self, user_id: int) -> list[ApplicationResponse]:
        applications = self.application_repository.get_by_user(user_id)
        return [ApplicationResponse.model_validate(a) for a in applications]

    def get_application(self, application_id: int) -> ApplicationResponse:
        application = self.application_repository.get_by_id(application_id)

        if not application:
            raise ResumeNotFoundException(
                message=f"Application with id {application_id} not found."
            )

        return ApplicationResponse.model_validate(application)

    def update_status(
        self,
        application_id: int,
        status: str,
    ) -> ApplicationResponse:

        application = self.application_repository.get_by_id(application_id)

        if not application:
            raise ResumeNotFoundException(
                message=f"Application with id {application_id} not found."
            )

        application.status = status.upper()

        if status.upper() == ApplicationStatus.APPLIED.value:
            application.applied_at = datetime.utcnow()

        self.application_repository.update(application)

        return ApplicationResponse.model_validate(application)

    def get_stats(self, user_id: int) -> dict:
        return self.application_repository.get_stats(user_id)