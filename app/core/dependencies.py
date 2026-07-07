from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.document_service import DocumentService
from app.services.job_service import JobService
from app.services.resume_service import ResumeService


def get_resume_service(db: Session = Depends(get_db)) -> ResumeService:
    """
    Provides a ResumeService instance with the request-scoped
    DB session injected.
    """
    return ResumeService(db)


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    """
    Provides a DocumentService instance with the request-scoped
    DB session injected.
    """
    return DocumentService(db)


def get_job_service(db: Session = Depends(get_db)) -> JobService:
    """
    Provides a JobService instance with the request-scoped
    DB session injected.
    """
    return JobService(db)


def get_current_user_id() -> int:
    """
    Temporary stand-in until authentication is implemented.

    Returns a hardcoded user_id so the upload pipeline can be
    fully tested end-to-end before auth exists.
    """
    return 1