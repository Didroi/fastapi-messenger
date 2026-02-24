from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import String, or_
from sqlalchemy.orm import Session

from app.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.db import get_db
from app.models import User
from app.schemas import AuthResponse, LoginRequest, UserCreate, UserResponse, UserUpdate
from app.logger import get_logger

router = APIRouter(prefix="/users", tags=["users"])
logger = get_logger(__name__)


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Check username is not already taken (case-insensitive)
    existing = db.query(User).filter(User.username == user.username.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    # 2. Hash password and create user
    new_user = User(
        username=user.username.lower(),
        password_hash=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 3. Log and issue token immediately (registered = logged in)
    logger.info("User registered: %s", new_user.username)
    token = create_access_token(str(new_user.id))

    # 4. Return token and user data
    return AuthResponse(access_token=token, user=new_user)


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # 1. Find active user by username (case-insensitive)
    user = (
        db.query(User)
        .filter(User.username == data.username.lower(), User.is_active.is_(True))
        .first()
    )

    # 2. Verify password — same error for wrong username and wrong password (security)
    if not user or not verify_password(data.password, str(user.password_hash)):
        logger.warning("Failed login attempt: %s", data.username)
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # 3. Issue token and return user data
    token = create_access_token(str(user.id))
    return AuthResponse(access_token=token, user=user)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    # 1. Current user is already resolved from token by get_current_user dependency
    return current_user


@router.get("/search", response_model=list[UserResponse])
def search_users(
    q: str = Query(min_length=1, description="Username (partial match) or user ID"),
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Users per page"),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    # 1. Search active users by username substring or user ID (case-insensitive)
    offset = (page - 1) * size
    users = (
        db.query(User)
        .filter(
            User.is_active.is_(True),
            or_(
                User.username.ilike(f"%{q}%"),
                User.id.cast(String).ilike(f"%{q}%"),
            ),
        )
        .offset(offset)
        .limit(size)
        .all()
    )

    # 2. Return paginated results
    return users


@router.patch("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Update username (store lowercase for case-insensitive matching)
    current_user.username = data.username.lower()
    db.commit()
    db.refresh(current_user)

    # 2. Return updated user
    return current_user


@router.delete("/me", status_code=204)
def deactivate_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Soft delete — mark as inactive instead of removing from DB
    # Messages are preserved (sender/receiver history remains intact)
    current_user.is_active = False
    db.commit()
