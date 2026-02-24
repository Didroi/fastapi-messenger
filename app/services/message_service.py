import uuid
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.logger import get_logger
from app.models import Message, User
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository
from app.schemas import MessageCreate

logger = get_logger(__name__)


class MessageService:
    def __init__(self, db: Session):
        self.repo = MessageRepository(db)
        # UserRepository needed to validate receiver exists
        self.user_repo = UserRepository(db)

    def create(self, data: MessageCreate, sender: User) -> Message:
        receiver = self.user_repo.get_by_id(data.receiver_id)
        if not receiver or not receiver.is_active:
            raise HTTPException(status_code=404, detail="Receiver not found")

        message = self.repo.create(
            text=data.text,
            sender_id=sender.id,
            receiver_id=data.receiver_id,
        )

        logger.info("Message sent: from %s to %s", sender.id, data.receiver_id)
        return message

    def get_inbox(
        self,
        receiver_id: uuid.UUID,
        unread_only: Optional[bool],
        page: int,
        size: int,
    ) -> list[Message]:
        offset = (page - 1) * size
        return self.repo.get_inbox(receiver_id, unread_only, offset, size)

    def get_outbox(self, sender_id: uuid.UUID, page: int, size: int) -> list[Message]:
        offset = (page - 1) * size
        return self.repo.get_outbox(sender_id, offset, size)

    def read_message(self, message_id: int, current_user: User) -> Message:
        message = self.repo.get_by_id_and_receiver(message_id, current_user.id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        return self.repo.mark_as_read(message)

    def delete(self, message_id: int, current_user: User) -> None:
        message = self.repo.get_by_id(message_id)
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
        self.repo.delete(message)
