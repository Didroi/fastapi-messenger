from fastapi import APIRouter, Depends, Query

from app.dependencies import get_current_user, get_user_service
from app.schemas import AuthResponse, LoginRequest, UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.utils.pagination import PaginationParams

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(data: UserCreate, service: UserService = Depends(get_user_service)):
    return service.register(data)


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, service: UserService = Depends(get_user_service)):
    return service.login(data.username, data.password)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.get("/search", response_model=list[UserResponse])
def search_users(
    q: str = Query(min_length=1, description="Username (partial match) or user ID"),
    pagination: PaginationParams = Depends(PaginationParams),
    service: UserService = Depends(get_user_service),
    _current_user: UserResponse = Depends(get_current_user),
):
    return service.search(q, pagination.page, pagination.size)


@router.patch("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(get_current_user),
):
    return service.update_me(current_user.id, data)


@router.delete("/me", status_code=204)
def deactivate_me(
    service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(get_current_user),
):
    service.deactivate_me(current_user.id)
