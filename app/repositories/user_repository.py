import uuid
from typing import Optional

from sqlalchemy import String, or_
from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.username == username, User.is_active.is_(True))
            .first()
        )

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def exists_by_username(self, username: str) -> bool:
        return self.db.query(User).filter(User.username == username).first() is not None

    def create(self, username: str, password_hash: str) -> User:
        user = User(username=username, password_hash=password_hash)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_username(self, user: User, username: str) -> User:
        user.username = username
        self.db.commit()
        self.db.refresh(user)
        return user

    def deactivate(self, user: User) -> None:
        user.is_active = False
        self.db.commit()

    def search(self, q: str, offset: int, limit: int) -> list[User]:
        return (
            self.db.query(User)
            .filter(
                User.is_active.is_(True),
                or_(
                    User.username.ilike(f"%{q}%"),
                    User.id.cast(String).ilike(f"%{q}%"),
                ),
            )
            .offset(offset)
            .limit(limit)
            .all()
        )
