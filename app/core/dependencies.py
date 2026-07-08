from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.database.session import get_db
from app.exceptions.custome_exceptions import UnauthorizedException
from app.services.analytics_service import AnalyticsService
from app.services.application_service import ApplicationService
from app.services.auth_service import AuthService
from app.services.auto_apply_service import AutoApplyService
from app.services.cover_letter_service import CoverLetterService
from app.services.document_service import DocumentService
from app.services.job_service import JobService
from app.services.match_service import MatchService
from app.services.resume_service import ResumeService
from app.services.tailor_service import TailorService
from app.services.user_service import UserService


def get_resume_service(db: Session = Depends(get_db)) -> ResumeService:
    return ResumeService(db)

def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    return DocumentService(db)

def get_job_service(db: Session = Depends(get_db)) -> JobService:
    return JobService(db)

def get_match_service(db: Session = Depends(get_db)) -> MatchService:
    return MatchService(db)

def get_tailor_service(db: Session = Depends(get_db)) -> TailorService:
    return TailorService(db)

def get_cover_letter_service(db: Session = Depends(get_db)) -> CoverLetterService:
    return CoverLetterService(db)

def get_application_service(db: Session = Depends(get_db)) -> ApplicationService:
    return ApplicationService(db)

def get_auto_apply_service(db: Session = Depends(get_db)) -> AutoApplyService:
    return AutoApplyService(db)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_current_user_id(
    authorization: str = Header(...),
) -> int:
    """
    Extracts and validates JWT access token from Authorization header.
    Expected format: Bearer <token>
    """
    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            raise UnauthorizedException()

        payload = decode_token(token)

        if payload.get("type") != "access":
            raise UnauthorizedException()

        return int(payload["sub"])

    except UnauthorizedException:
        raise

    except Exception:
        raise UnauthorizedException(message="Invalid or expired access token.")