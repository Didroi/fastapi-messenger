# FastAPI Messenger

A pet project built to explore modern Python backend development. A REST API messenger with user authentication, message exchange, and clean layered architecture.

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

## Running Tests

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing
```