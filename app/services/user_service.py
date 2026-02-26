import uuid

from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.logger import get_logger
from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas import AuthResponse, UserCreate, UserUpdate
from app.utils.security import create_access_token, hash_password, verify_password

logger = get_logger(__name__)


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, data: UserCreate) -> AuthResponse:
        username = data.username.lower()

        if self.repo.exists_by_username(username):
            raise ConflictError("Username already exists")

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
            raise UnauthorizedError("Invalid username or password")

        token = create_access_token(str(user.id))
        return AuthResponse(access_token=token, user=user)

    def get_by_id(self, user_id: uuid.UUID) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    def update_me(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        user = self.get_by_id(user_id)
        return self.repo.update_username(user, data.username.lower())

    def deactivate_me(self, user_id: uuid.UUID) -> None:
        user = self.get_by_id(user_id)
        self.repo.deactivate(user)

    def search(self, q: str, page: int, size: int) -> list[User]:
        offset = (page - 1) * size
        return self.repo.search(q, offset=offset, limit=size)
