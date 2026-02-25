import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.services.user_service import UserService


def make_service():
    service = UserService(db=MagicMock())
    service.repo = MagicMock()
    return service


def make_user_create(username="dima", password="Password1"):
    data = MagicMock()
    data.username = username
    data.password = password
    return data


def make_db_user(username="dima", password_hash="hashed"):
    user = MagicMock()
    user.id = uuid.uuid4()
    user.username = username
    user.password_hash = password_hash
    user.is_active = True
    return user


# --- register ---


def test_register_username_taken():
    service = make_service()
    service.repo.exists_by_username.return_value = True

    with pytest.raises(Exception) as exc_info:
        service.register(make_user_create())

    assert "already exists" in str(exc_info.value)


def test_register_success():
    service = make_service()
    service.repo.exists_by_username.return_value = False
    service.repo.create.return_value = make_db_user()

    result = service.register(make_user_create())

    assert result.access_token is not None
    assert result.user is not None
    service.repo.create.assert_called_once()


# --- login ---


def test_login_user_not_found():
    service = make_service()
    service.repo.get_by_username.return_value = None

    with pytest.raises(Exception) as exc_info:
        service.login("dima", "Password1")

    assert "Invalid username or password" in str(exc_info.value)


def test_login_wrong_password():
    service = make_service()
    service.repo.get_by_username.return_value = make_db_user()

    with patch("app.services.user_service.verify_password", return_value=False):
        with pytest.raises(Exception) as exc_info:
            service.login("dima", "WrongPassword1")

    assert "Invalid username or password" in str(exc_info.value)


def test_login_success():
    service = make_service()
    service.repo.get_by_username.return_value = make_db_user()

    with patch("app.services.user_service.verify_password", return_value=True):
        result = service.login("dima", "Password1")

    assert result.access_token is not None
    assert result.user is not None


# --- update_me ---


def test_update_me_user_not_found():
    service = make_service()
    service.repo.get_by_id.return_value = None

    with pytest.raises(Exception) as exc_info:
        service.update_me(uuid.uuid4(), MagicMock(username="new_name"))

    assert "User not found" in str(exc_info.value)


# --- deactivate_me ---


def test_deactivate_me_user_not_found():
    service = make_service()
    service.repo.get_by_id.return_value = None

    with pytest.raises(Exception) as exc_info:
        service.deactivate_me(uuid.uuid4())

    assert "User not found" in str(exc_info.value)


def test_deactivate_me_success():
    service = make_service()
    user = make_db_user()
    service.repo.get_by_id.return_value = user

    service.deactivate_me(user.id)

    service.repo.deactivate.assert_called_once_with(user)
