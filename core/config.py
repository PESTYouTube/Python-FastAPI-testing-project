import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_COOKIE_NAME: str
    JWT_EXPIRE_MINUTES: int
    cors_allowed_origins: list[str]


def get_settings() -> Settings:
    return Settings(
        DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///./app.db"),
        JWT_SECRET_KEY=os.getenv(
            "JWT_SECRET_KEY",
            "dev-secret-key-min-32-bytes-long!!",
        ),
        JWT_ALGORITHM="HS256",
        JWT_ACCESS_COOKIE_NAME="access_token",
        JWT_EXPIRE_MINUTES=int(os.getenv("JWT_EXPIRE_MINUTES", "60")),
        cors_allowed_origins=["*"],
    )
