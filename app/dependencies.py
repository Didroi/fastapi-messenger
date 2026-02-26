from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import UserResponse
from app.services.message_service import MessageService
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.utils.security import decode_access_token

# HTTPBearer shows a simple token input in Swagger UI (unlike OAuth2PasswordBearer which shows username/password form)
oauth2_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserResponse:
    user_id = decode_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = UserRepository(db).get_active_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return UserResponse.model_validate(user)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_message_service(db: Session = Depends(get_db)) -> MessageService:
    return MessageService(db)
