from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from app.db import get_db
from app.routers import users, messages

app = FastAPI(title="Messenger")

app.include_router(users.router)
app.include_router(messages.router)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503, content={"status": "error", "db": "unavailable"}
        )
