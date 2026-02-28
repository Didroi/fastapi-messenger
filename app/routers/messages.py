from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_current_user, get_message_service
from app.schemas import MessageCreate, MessageResponse, UserResponse, PaginatedResponse
from app.services.message_service import MessageService
from app.utils.pagination import PaginationParams

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/", response_model=MessageResponse, status_code=201)
def create_message(
    data: MessageCreate,
    service: MessageService = Depends(get_message_service),
    current_user: UserResponse = Depends(get_current_user),
):
    return service.create(data, current_user.id)


@router.get("/inbox", response_model=PaginatedResponse[MessageResponse])
def get_inbox(
    pagination: PaginationParams = Depends(PaginationParams),
    unread_only: Optional[bool] = Query(
        default=None, description="true — unread only, false — read only, omit — all"
    ),
    service: MessageService = Depends(get_message_service),
    current_user: UserResponse = Depends(get_current_user),
):
    return service.get_inbox(
        current_user.id, unread_only, pagination.page, pagination.size
    )


@router.get("/outbox", response_model=PaginatedResponse[MessageResponse])
def get_outbox(
    pagination: PaginationParams = Depends(PaginationParams),
    service: MessageService = Depends(get_message_service),
    current_user: UserResponse = Depends(get_current_user),
):
    return service.get_outbox(current_user.id, pagination.page, pagination.size)


@router.post("/{message_id}/read", response_model=MessageResponse)
def read_message(
    message_id: int,
    service: MessageService = Depends(get_message_service),
    current_user: UserResponse = Depends(get_current_user),
):
    return service.read_message(message_id, current_user.id)


@router.delete("/{message_id}", status_code=204)
def delete_message(
    message_id: int,
    service: MessageService = Depends(get_message_service),
    current_user: UserResponse = Depends(get_current_user),
):
    service.delete(message_id, current_user.id)
