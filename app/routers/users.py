from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_current_user, get_user_service
from app.exceptions import ConflictError, NotFoundError
from app.schemas import AuthResponse, LoginRequest, UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(data: UserCreate, service: UserService = Depends(get_user_service)):
    try:
        return service.register(data)
    except ConflictError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, service: UserService = Depends(get_user_service)):
    try:
        return service.login(data.username, data.password)
    except NotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.get("/search", response_model=list[UserResponse])
def search_users(
    q: str = Query(min_length=1, description="Username (partial match) or user ID"),
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Users per page"),
    service: UserService = Depends(get_user_service),
    _current_user: UserResponse = Depends(get_current_user),
):
    return service.search(q, page, size)


@router.patch("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        return service.update_me(current_user.id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/me", status_code=204)
def deactivate_me(
    service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        service.deactivate_me(current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
