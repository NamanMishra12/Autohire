from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.exceptions.custome_exceptions import (
    InvalidCredentialsException,
    UnauthorizedException,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse


class AuthService:

    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def register(self, name: str, email: str, password: str) -> TokenResponse:
        existing = self.user_repository.get_by_email(email)
        if existing:
            raise InvalidCredentialsException(message="Email already registered.")

        user = User(
            name=name,
            email=email,
            hashed_password=hash_password(password),
            is_active=True,
        )
        user = self.user_repository.create(user)

        return self._generate_tokens(user)

    def login(self, email: str, password: str) -> TokenResponse:
        user = self.user_repository.get_by_email(email)

        if not user or not user.hashed_password:
            raise InvalidCredentialsException()

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        if not user.is_active:
            raise UnauthorizedException(message="Account is inactive.")

        return self._generate_tokens(user)

    def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)

            if payload.get("type") != "refresh":
                raise UnauthorizedException(message="Invalid token type.")

            user_id = int(payload["sub"])
            user = self.user_repository.get_by_id(user_id)

            if not user or not user.is_active:
                raise UnauthorizedException()

            return self._generate_tokens(user)

        except Exception:
            raise UnauthorizedException(message="Invalid or expired refresh token.")

    def _generate_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        user.refresh_token = refresh_token
        self.user_repository.update(user)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )