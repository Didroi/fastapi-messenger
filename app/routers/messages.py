from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import User
from app.schemas import MessageCreate, MessageResponse
from app.services.message_service import MessageService

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/", response_model=MessageResponse, status_code=201)
def create_message(
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MessageService(db).create(data, current_user)


@router.get("/inbox", response_model=list[MessageResponse])
def get_inbox(
    unread_only: Optional[bool] = Query(
        default=None, description="true — unread only, false — read only, omit — all"
    ),
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Messages per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MessageService(db).get_inbox(current_user.id, unread_only, page, size)


@router.get("/outbox", response_model=list[MessageResponse])
def get_outbox(
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Messages per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MessageService(db).get_outbox(current_user.id, page, size)


@router.post("/{message_id}/read", response_model=MessageResponse)
def read_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MessageService(db).read_message(message_id, current_user)


@router.delete("/{message_id}", status_code=204)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    MessageService(db).delete(message_id, current_user)
