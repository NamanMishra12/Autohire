from sqlalchemy.orm import Session

from app.core.encryption import decrypt, encrypt
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):

    def __init__(self, db: Session):
        super().__init__(db)

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user: User) -> User:
        return self.add(user)

    def save_session_cookies(
        self,
        user_id: int,
        platform: str,
        cookies_json: str,
    ) -> User | None:
        import json

        user = self.get_by_id(user_id)
        if not user:
            return None

        # Sanitize — re-parse and re-serialize to strip control characters
        try:
            parsed = json.loads(cookies_json)
            clean_json = json.dumps(parsed)
        except json.JSONDecodeError:
            logger.warning("Invalid cookies JSON provided")
            return None

        encrypted = encrypt(clean_json)
        platform = platform.lower()

        if platform == "linkedin":
            user.linkedin_cookies_encrypted = encrypted
        elif platform == "indeed":
            user.indeed_cookies_encrypted = encrypted
        elif platform == "naukri":
            user.naukri_cookies_encrypted = encrypted

        return self.update(user)

    def get_session_cookies(
        self,
        user_id: int,
        platform: str,
    ) -> list | None:
        import json

        user = self.get_by_id(user_id)

        if not user:
            return None

        platform = platform.lower()

        encrypted = None

        if platform == "linkedin":
            encrypted = user.linkedin_cookies_encrypted
        elif platform == "indeed":
            encrypted = user.indeed_cookies_encrypted
        elif platform == "naukri":
            encrypted = user.naukri_cookies_encrypted

        if not encrypted:
            return None

        try:
            decrypted = decrypt(encrypted)
            return json.loads(decrypted)
        except Exception:
            return None