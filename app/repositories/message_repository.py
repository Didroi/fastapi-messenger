import uuid
from typing import Optional

from sqlalchemy.orm import Session, Query

from app.models import Message


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, text: str, sender_id: uuid.UUID, receiver_id: uuid.UUID
    ) -> Message:
        message = Message(text=text, sender_id=sender_id, receiver_id=receiver_id)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def _inbox_query(
        self, receiver_id: uuid.UUID, unread_only: Optional[bool]
    ) -> Query:
        query = self.db.query(Message).filter(Message.receiver_id == receiver_id)
        if unread_only is not None:
            if unread_only:
                query = query.filter(Message.is_read.is_(False))
            else:
                query = query.filter(Message.is_read.is_(True))
        return query

    def get_inbox(
        self,
        receiver_id: uuid.UUID,
        unread_only: Optional[bool],
        offset: int,
        limit: int,
    ) -> list[Message]:
        return (
            self._inbox_query(receiver_id, unread_only)
            .order_by(Message.id)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_inbox(self, receiver_id: uuid.UUID, unread_only: Optional[bool]) -> int:
        return self._inbox_query(receiver_id, unread_only).count()

    def get_outbox(
        self, sender_id: uuid.UUID, offset: int, limit: int
    ) -> list[Message]:
        return (
            self.db.query(Message)
            .filter(Message.sender_id == sender_id)
            .order_by(Message.id)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_outbox(self, sender_id: uuid.UUID) -> int:
        return self.db.query(Message).filter(Message.sender_id == sender_id).count()

    def get_by_id(self, message_id: int) -> Optional[Message]:
        return self.db.query(Message).filter(Message.id == message_id).first()

    def get_by_id_and_receiver(
        self, message_id: int, receiver_id: uuid.UUID
    ) -> Optional[Message]:
        return (
            self.db.query(Message)
            .filter(Message.id == message_id, Message.receiver_id == receiver_id)
            .first()
        )

    def mark_as_read(self, message: Message) -> Message:
        message.is_read = True
        self.db.commit()
        self.db.refresh(message)
        return message

    def delete(self, message: Message) -> None:
        self.db.delete(message)
        self.db.commit()
