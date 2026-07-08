from sqlalchemy.orm import Session

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

    def update(self, user: User) -> User:
        return super().update(user)