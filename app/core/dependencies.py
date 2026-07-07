from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.document_service import DocumentService
from app.services.job_service import JobService
from app.services.match_service import MatchService
from app.services.resume_service import ResumeService


def get_resume_service(db: Session = Depends(get_db)) -> ResumeService:
    return ResumeService(db)


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    return DocumentService(db)


def get_job_service(db: Session = Depends(get_db)) -> JobService:
    return JobService(db)


def get_match_service(db: Session = Depends(get_db)) -> MatchService:
    return MatchService(db)


def get_current_user_id() -> int:
    return 1