# FastAPI Messenger

A pet project built for learning purposes. A simple REST API messenger with user authentication, message exchange, and JWT-based authorization.

## Tech Stack

- **Python 3.13**
- **FastAPI** — web framework
- **PostgreSQL** — database
- **SQLAlchemy** — ORM
- **Alembic** — database migrations
- **Pydantic** — data validation
- **JWT** (python-jose) — authentication
- **bcrypt** (passlib) — password hashing
- **pytest** — unit testing
- **Docker** — running PostgreSQL locally
- **Ruff** — linter and formatter

## Setup

1. Copy `.env.example` to `.env` and fill in your values
2. Install dependencies: `pip install -r requirements.txt`
3. Start database: `docker compose up -d`
4. Apply migrations: `alembic upgrade head`
5. Run the app: `uvicorn app.main:app --reload`

API docs available at `http://localhost:8000/docs`

## API Endpoints

### Auth & Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/users/register` | — | Register new user, returns token |
| POST | `/users/login` | — | Login, returns token |
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
| GET | `/messages/{id}` | ✓ | Get message by ID (marks as read) |
| DELETE | `/messages/{id}` | ✓ | Delete unread message (sender only) |

### Query parameters

`GET /messages/inbox` supports:
- `unread_only=true` — unread messages only
- `page=1&size=20` — pagination

`GET /users/search` supports:
- `page=1&size=20` — pagination

## Running Tests

```bash
pytest tests/
pytest tests/ --cov=app --cov-report=term-missing
```