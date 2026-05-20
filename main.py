from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models.models
from db.seed import seed_database
from db.session import SessionLocal, engine
from middleware.auth import AuthMiddleware
from routers import admin, auth, business, users

models.models.Base.metadata.create_all(bind=engine)


def _init_db() -> None:
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _init_db()
    yield


app = FastAPI(
    title="Auth & Authorization API",
    description="Собственная система аутентификации (JWT + bcrypt) и авторизации (RBAC)",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(business.router)


@app.get("/")
def root():
    return {
        "message": "Auth API",
        "docs": "/docs",
        "demo_users": [
            "admin@example.com / admin123",
            "manager@example.com / manager123",
            "user@example.com / user1234",
        ],
    }
