from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password
from app.logger import get_logger
from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas import AuthResponse, UserCreate, UserUpdate

logger = get_logger(__name__)


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, data: UserCreate) -> AuthResponse:
        username = data.username.lower()

        if self.repo.exists_by_username(username):
            raise HTTPException(status_code=400, detail="Username already exists")

        user = self.repo.create(
            username=username,
            password_hash=hash_password(data.password),
        )

        logger.info("User registered: %s", user.username)
        token = create_access_token(str(user.id))
        return AuthResponse(access_token=token, user=user)

    def login(self, username: str, password: str) -> AuthResponse:
        user = self.repo.get_by_username(username.lower())

        # Same error for wrong username and wrong password (security)
        if not user or not verify_password(password, str(user.password_hash)):
            logger.warning("Failed login attempt: %s", username)
            raise HTTPException(status_code=401, detail="Invalid username or password")

        token = create_access_token(str(user.id))
        return AuthResponse(access_token=token, user=user)

    def update_me(self, user: User, data: UserUpdate) -> User:
        return self.repo.update_username(user, data.username.lower())

    def deactivate_me(self, user: User) -> None:
        self.repo.deactivate(user)

    def search(self, q: str, page: int, size: int) -> list[User]:
        offset = (page - 1) * size
        return self.repo.search(q, offset=offset, limit=size)
