import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services.message_service import MessageService


def make_service():
    """Create MessageService with mocked repositories."""
    service = MessageService(db=MagicMock())
    service.repo = MagicMock()
    service.user_repo = MagicMock()
    return service


def make_user(user_id=None):
    user = MagicMock()
    user.id = user_id or uuid.uuid4()
    user.is_active = True
    return user


def make_message(sender_id=None, is_read=False):
    message = MagicMock()
    message.sender_id = sender_id or uuid.uuid4()
    message.is_read = is_read
    return message


# --- create ---


def test_create_receiver_not_found():
    service = make_service()
    service.user_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.create(MagicMock(receiver_id=uuid.uuid4()), sender=make_user())

    assert exc_info.value.status_code == 404


def test_create_receiver_inactive():
    service = make_service()
    inactive_user = make_user()
    inactive_user.is_active = False
    service.user_repo.get_by_id.return_value = inactive_user

    with pytest.raises(HTTPException) as exc_info:
        service.create(MagicMock(receiver_id=uuid.uuid4()), sender=make_user())

    assert exc_info.value.status_code == 404


# --- delete ---


def test_delete_message_not_found():
    service = make_service()
    service.repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.delete(message_id=1, current_user=make_user())

    assert exc_info.value.status_code == 404


def test_delete_not_sender():
    service = make_service()
    sender_id = uuid.uuid4()
    other_user_id = uuid.uuid4()

    service.repo.get_by_id.return_value = make_message(sender_id=sender_id)

    with pytest.raises(HTTPException) as exc_info:
        service.delete(message_id=1, current_user=make_user(user_id=other_user_id))

    assert exc_info.value.status_code == 403


def test_delete_already_read():
    service = make_service()
    user = make_user()
    service.repo.get_by_id.return_value = make_message(sender_id=user.id, is_read=True)

    with pytest.raises(HTTPException) as exc_info:
        service.delete(message_id=1, current_user=user)

    assert exc_info.value.status_code == 400


def test_delete_success():
    service = make_service()
    user = make_user()
    service.repo.get_by_id.return_value = make_message(sender_id=user.id, is_read=False)

    service.delete(message_id=1, current_user=user)

    service.repo.delete.assert_called_once()


# --- read_message ---


def test_read_message_not_found():
    service = make_service()
    service.repo.get_by_id_and_receiver.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        service.read_message(message_id=1, current_user=make_user())

    assert exc_info.value.status_code == 404


def test_read_message_success():
    service = make_service()
    message = make_message()
    service.repo.get_by_id_and_receiver.return_value = message
    service.repo.mark_as_read.return_value = message

    result = service.read_message(message_id=1, current_user=make_user())

    service.repo.mark_as_read.assert_called_once_with(message)
    assert result == message
