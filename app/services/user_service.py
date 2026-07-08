from sqlalchemy.orm import Session

from app.exceptions.custome_exceptions import ResumeNotFoundException
from app.repositories.user_repository import UserRepository
from app.schemas.user import SessionCookieUpdate, UserProfileUpdate, UserResponse


class UserService:

    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def get_profile(self, user_id: int) -> UserResponse:
        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise ResumeNotFoundException(message="User not found.")

        return self._build_response(user)

    def update_profile(
        self,
        user_id: int,
        payload: UserProfileUpdate,
    ) -> UserResponse:
        user = self.user_repository.get_by_id(user_id)

        if not user:
            raise ResumeNotFoundException(message="User not found.")

        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(user, field, value)

        user = self.user_repository.update(user)

        return self._build_response(user)

    def save_session_cookies(
        self,
        user_id: int,
        payload: SessionCookieUpdate,
    ) -> dict:
        user = self.user_repository.save_session_cookies(
            user_id=user_id,
            platform=payload.platform,
            cookies_json=payload.cookies_json,
        )

        if not user:
            raise ResumeNotFoundException(message="User not found.")

        return {
            "platform": payload.platform,
            "saved": True,
            "message": f"{payload.platform.title()} session cookies saved and encrypted.",
        }

    @staticmethod
    def _build_response(user) -> UserResponse:
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            location=user.location,
            linkedin_url=user.linkedin_url,
            portfolio_url=user.portfolio_url,
            years_of_experience=user.years_of_experience,
            has_linkedin_session=bool(user.linkedin_cookies_encrypted),
            has_indeed_session=bool(user.indeed_cookies_encrypted),
            has_naukri_session=bool(user.naukri_cookies_encrypted),
            created_at=user.created_at,
        )