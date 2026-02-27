import pytest
from pydantic import ValidationError
from app.schemas import UserCreate, UserUpdate, MessageCreate
import uuid


# --- password_strength validator ---


def test_valid_password():
    user = UserCreate(username="dima", password="Password1")
    assert user.password == "Password1"


def test_password_too_short():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(username="dima", password="Pass1")
    assert "at least 8 characters" in str(exc_info.value)


def test_password_no_digit():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(username="dima", password="Password")
    assert "at least one digit" in str(exc_info.value)


def test_password_no_uppercase():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(username="dima", password="password1")
    assert "at least one uppercase" in str(exc_info.value)


def test_password_exactly_8_chars():
    user = UserCreate(username="dima", password="Password1")
    assert user.password == "Password1"


def test_password_all_rules_fail():
    with pytest.raises(ValidationError):
        UserCreate(username="dima", password="pass")


# --- UserUpdate ---


def test_update_empty_username():
    with pytest.raises(ValidationError):
        UserUpdate(username="")


def test_update_valid_username():
    u = UserUpdate(username="dima")
    assert u.username == "dima"


# --- MessageCreate ---


def test_message_empty_text():
    with pytest.raises(ValidationError):
        MessageCreate(text="", receiver_id=uuid.uuid4())


def test_message_valid():
    m = MessageCreate(text="hello", receiver_id=uuid.uuid4())
    assert m.text == "hello"


def test_message_too_long():
    with pytest.raises(ValidationError):
        MessageCreate(text="x" * 4097, receiver_id=uuid.uuid4())
