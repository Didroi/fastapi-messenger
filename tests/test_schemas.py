import pytest
from pydantic import ValidationError
from app.schemas import UserCreate


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
    # короткий, без цифры, без заглавной
    with pytest.raises(ValidationError):
        UserCreate(username="dima", password="pass")
