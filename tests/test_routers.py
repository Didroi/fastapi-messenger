import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_user_service, get_message_service, get_current_user
from app.schemas import AuthResponse, UserResponse, MessageResponse
import uuid
from datetime import datetime


# --- helpers ---


def make_user_response():
    return UserResponse(
        id=uuid.uuid4(),
        username="dima",
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def make_auth_response():
    return AuthResponse(
        access_token="test-token",
        token_type="bearer",
        user=make_user_response(),
    )


def make_message_response():
    return MessageResponse(
        id=1,
        text="hello",
        sender_id=uuid.uuid4(),
        receiver_id=uuid.uuid4(),
        is_read=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def mock_user_service():
    return MagicMock()


@pytest.fixture
def mock_message_service():
    return MagicMock()


@pytest.fixture
def client(mock_user_service, mock_message_service):
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    app.dependency_overrides[get_message_service] = lambda: mock_message_service
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(mock_user_service, mock_message_service):
    current_user = make_user_response()
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    app.dependency_overrides[get_message_service] = lambda: mock_message_service
    app.dependency_overrides[get_current_user] = lambda: current_user
    yield TestClient(app), current_user
    app.dependency_overrides.clear()


# --- register ---


def test_register_returns_201(client, mock_user_service):
    mock_user_service.register.return_value = make_auth_response()

    response = client.post(
        "/users/register", json={"username": "dima", "password": "Password1"}
    )

    assert response.status_code == 201
    assert "access_token" in response.json()


def test_register_username_taken_returns_400(client, mock_user_service):
    from app.exceptions import ConflictError

    mock_user_service.register.side_effect = ConflictError("Username already exists")

    response = client.post(
        "/users/register", json={"username": "dima", "password": "Password1"}
    )

    assert response.status_code == 400


# --- login ---


def test_login_returns_200(client, mock_user_service):
    mock_user_service.login.return_value = make_auth_response()

    response = client.post(
        "/users/login", json={"username": "dima", "password": "Password1"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


# --- get_me ---


def test_get_me_without_token_returns_401(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_get_me_with_token_returns_200(auth_client):
    client, current_user = auth_client
    response = client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["username"] == current_user.username


# --- messages ---


def test_create_message_without_token_returns_401(client):
    response = client.post(
        "/messages/", json={"text": "hello", "receiver_id": str(uuid.uuid4())}
    )
    assert response.status_code == 401


def test_create_message_returns_201(auth_client, mock_message_service):
    client, current_user = auth_client
    mock_message_service.create.return_value = make_message_response()

    response = client.post(
        "/messages/", json={"text": "hello", "receiver_id": str(uuid.uuid4())}
    )

    assert response.status_code == 201


# --- health ---


def test_health_returns_200(client):
    # health endpoint uses get_db directly, not through service
    # override it to avoid real DB connection
    from app.main import app as fastapi_app
    from app.db import get_db

    def mock_db():
        db = MagicMock()
        db.execute.return_value = None
        yield db

    fastapi_app.dependency_overrides[get_db] = mock_db
    response = client.get("/health")
    fastapi_app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
