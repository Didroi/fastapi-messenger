import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.logger import get_logger
from app.models import Message
from app.repositories.message_repository import MessageRepository
from app.repositories.user_repository import UserRepository
from app.schemas import MessageCreate

logger = get_logger(__name__)


class MessageService:
    def __init__(self, db: Session):
        self.repo = MessageRepository(db)
        self.user_repo = UserRepository(db)

    def create(self, data: MessageCreate, sender_id: uuid.UUID) -> Message:
        receiver = self.user_repo.get_by_id(data.receiver_id)
        if not receiver or not receiver.is_active:
            raise NotFoundError("Receiver not found")

        message = self.repo.create(
            text=data.text,
            sender_id=sender_id,
            receiver_id=data.receiver_id,
        )

        logger.info("Message sent: from %s to %s", sender_id, data.receiver_id)
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

    def read_message(self, message_id: int, user_id: uuid.UUID) -> Message:
        message = self.repo.get_by_id_and_receiver(message_id, user_id)
        if not message:
            raise NotFoundError("Message not found")
        return self.repo.mark_as_read(message)

    def delete(self, message_id: int, user_id: uuid.UUID) -> None:
        message = self.repo.get_by_id(message_id)
        if not message:
            raise NotFoundError("Message not found")

        if message.sender_id != user_id:
            logger.warning(
                "Unauthorized delete attempt: message_id=%s user=%s",
                message_id,
                user_id,
            )
            raise ForbiddenError("Only the sender can delete this message")

        if message.is_read:
            raise ConflictError("Cannot delete a read message")

        logger.info("Message deleted: id=%s by user=%s", message_id, user_id)
        self.repo.delete(message)
