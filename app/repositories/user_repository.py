import uuid
from typing import Optional

from sqlalchemy import String, or_, exists
from sqlalchemy.orm import Session, Query

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

    def get_active_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        # Separate method instead of active_only parameter — explicit business intent
        return (
            self.db.query(User)
            .filter(User.id == user_id, User.is_active.is_(True))
            .first()
        )

    def exists_by_username(
        self, username: str, exclude_user_id: uuid.UUID | None = None
    ) -> bool:
        condition = User.username == username
        if exclude_user_id is not None:
            condition = condition & (User.id != exclude_user_id)
        return self.db.query(exists().where(condition)).scalar()

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

    def _search_query(self, q: str) -> Query:
        return self.db.query(User).filter(
            User.is_active.is_(True),
            or_(
                User.username.ilike(f"%{q}%"),
                User.id.cast(String).ilike(f"%{q}%"),
            ),
        )

    def search(self, q: str, offset: int, limit: int) -> list[User]:
        return self._search_query(q).offset(offset).limit(limit).all()

    def count_search(self, q: str) -> int:
        return self._search_query(q).count()
