from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_current_user, get_message_service
from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.schemas import MessageCreate, MessageResponse, UserResponse
from app.services.message_service import MessageService

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/", response_model=MessageResponse, status_code=201)
def create_message(
    data: MessageCreate,
    service: MessageService = Depends(get_message_service),
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        return service.create(data, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/inbox", response_model=list[MessageResponse])
def get_inbox(
    unread_only: Optional[bool] = Query(
        default=None, description="true — unread only, false — read only, omit — all"
    ),
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Messages per page"),
    service: MessageService = Depends(get_message_service),
    current_user: UserResponse = Depends(get_current_user),
):
    return service.get_inbox(current_user.id, unread_only, page, size)


@router.get("/outbox", response_model=list[MessageResponse])
def get_outbox(
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Messages per page"),
    service: MessageService = Depends(get_message_service),
    current_user: UserResponse = Depends(get_current_user),
):
    return service.get_outbox(current_user.id, page, size)


@router.post("/{message_id}/read", response_model=MessageResponse)
def read_message(
    message_id: int,
    service: MessageService = Depends(get_message_service),
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        return service.read_message(message_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{message_id}", status_code=204)
def delete_message(
    message_id: int,
    service: MessageService = Depends(get_message_service),
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        service.delete(message_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=400, detail=str(e))
