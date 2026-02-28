# FastAPI Messenger

A pet project built to explore modern Python backend development. A REST API messenger with user authentication, message exchange, and clean layered architecture.

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.129-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-database-336791?logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![Alembic](https://img.shields.io/badge/Alembic-1.18-lightgrey)
![Pydantic](https://img.shields.io/badge/Pydantic-2.12-E92063?logo=pydantic&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-auth-orange?logo=jsonwebtokens&logoColor=white)
![bcrypt](https://img.shields.io/badge/bcrypt-4.0-yellow)
![pytest](https://img.shields.io/badge/pytest-9.0-green?logo=pytest&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED?logo=docker&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-0.15-purple)

## Setup

### With Docker (recommended)
1. Copy `.env.example` to `.env`
2. `docker compose up --build`

API docs available at `http://localhost:8000/docs`

### Local development
1. Copy `.env.example` to `.env`
2. `pip install -r requirements.txt`
3. `docker compose up -d db` — start database only
4. `alembic upgrade head`
5. `uvicorn app.main:app --reload`

## Architecture

The project follows a layered architecture:
```
Router → Service → Repository → Database
```

- **Routers** — accept requests, delegate to services, return responses
- **Services** — business logic and rules
- **Repositories** — database queries only
- **Schemas** — data validation and serialization (DTO)

## API Endpoints

### Auth & Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/users/register` | — | Register new user, returns token + user data |
| POST | `/users/login` | — | Login, returns token + user data |
| GET | `/users/me` | ✓ | Get current user profile |
| PATCH | `/users/me` | ✓ | Update username |
| DELETE | `/users/me` | ✓ | Deactivate account |
| GET | `/users/search?q=` | ✓ | Search users by username or ID |

### Messages

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/messages/` | ✓ | Send a message |
| GET | `/messages/inbox` | ✓ | Get received messages |
| GET | `/messages/outbox` | ✓ | Get sent messages |
| POST | `/messages/{id}/read` | ✓ | Mark message as read, returns message |
| DELETE | `/messages/{id}` | ✓ | Delete unread message (sender only) |

### Query parameters

`GET /messages/inbox` supports:
- `unread_only=true` — unread messages only
- `page=1&size=20` — pagination (max 100 per page)

`GET /users/search` supports:
- `page=1&size=20` — pagination

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check — returns app and DB status |

## Design Decisions

**Soft delete for users** — deactivating an account sets `is_active = False` instead of deleting the record. This preserves message history and maintains referential integrity. Hard delete would orphan messages or require cascading deletes, which is destructive and irreversible.

**`POST /messages/{id}/read` instead of `GET`** — marking a message as read is a state change, not a read operation. GET requests must be side-effect free (REST principle of idempotency). A dedicated POST action endpoint makes the intent explicit and avoids issues with caching and prefetching.

**`inbox` / `outbox` naming** — instead of a generic `/messages` endpoint with filter parameters, explicit named routes make the API self-documenting and the intent immediately clear to any consumer.

**Same error for wrong username and wrong password** — returning `"Invalid username or password"` for both cases prevents user enumeration attacks, where an attacker could determine which usernames exist by observing different error responses.

**UUID as user ID** — harder to enumerate than sequential integers, which adds a layer of security against ID-based scraping or unauthorized access attempts.

**Paginated responses** — all list endpoints return `items`, `total`, `page`, `size`, `pages` instead of a plain array. This gives clients everything needed to build pagination UI without additional requests.

**JWT access token without refresh** — token lifetime is set to 24 hours. Refresh token flow was deliberately omitted as out of scope for this project. In production, short-lived access tokens (15–60 min) with refresh tokens would be the standard approach.

## Running Tests

### Unit & integration tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing
```

Tests include:
- Unit tests for services (business logic with mocks)
- Router tests via TestClient (HTTP status codes, auth, response schemas)

### Regression tests

API regression suite built with Postman, covering all endpoints with real HTTP requests against a running instance.

Repository: [postman-tests-fastapi-messenger](https://github.com/Didroi/postman-tests-fastapi-messenger)