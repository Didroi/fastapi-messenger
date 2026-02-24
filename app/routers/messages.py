from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import Message, User
from app.schemas import MessageCreate, MessageResponse
from app.logger import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/", response_model=MessageResponse, status_code=201)
def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    receiver = (
        db.query(User)
        .filter(User.id == message.receiver_id, User.is_active.is_(True))
        .first()
    )
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    new_message = Message(
        text=message.text,
        sender_id=current_user.id,
        receiver_id=message.receiver_id,
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    logger.info("Message sent: from %s to %s", current_user.id, message.receiver_id)
    return new_message


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
    query = db.query(Message).filter(Message.receiver_id == current_user.id)

    if unread_only is not None:
        query = query.filter(Message.is_read == (not unread_only))

    offset = (page - 1) * size
    messages = query.order_by(Message.id).offset(offset).limit(size).all()
    return messages


@router.get("/outbox", response_model=list[MessageResponse])
def get_outbox(
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=20, ge=1, le=100, description="Messages per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    offset = (page - 1) * size
    messages = (
        db.query(Message)
        .filter(Message.sender_id == current_user.id)
        .order_by(Message.id)
        .offset(offset)
        .limit(size)
        .all()
    )
    return messages


@router.get("/{message_id}", response_model=MessageResponse)
def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = (
        db.query(Message)
        .filter(
            Message.receiver_id == current_user.id,
            Message.id == message_id,
        )
        .first()
    )
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    message.is_read = True
    db.commit()
    db.refresh(message)
    return message


@router.delete("/{message_id}", status_code=204)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    if message.sender_id != current_user.id:
        logger.warning(
            "Unauthorized delete attempt: message_id=%s user=%s",
            message_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=403, detail="Only the sender can delete this message"
        )

    if message.is_read:
        raise HTTPException(status_code=400, detail="Cannot delete a read message")

    logger.info("Message deleted: id=%s by user=%s", message_id, current_user.id)
    db.delete(message)
    db.commit()
