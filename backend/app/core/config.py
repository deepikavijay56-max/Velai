import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Velai Campus Gigs"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Single-college scope
    COLLEGE_ID: str = "psg-tech"
    COLLEGE_NAME: str = "PSG College of Technology"
    COLLEGE_EMAIL_DOMAIN: str = "psgtech.ac.in"

    # Database: Supports SQLite async for local dev and PostgreSQL asyncpg
    DATABASE_URL: str = "sqlite+aiosqlite:///./velai.db"

    # Security & JWT
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # OTP Auth
    MOCK_OTP: bool = True
    DEFAULT_TEST_OTP: str = "123456"

    # Rate limits & safety
    MAX_PUSH_NOTIFICATIONS_PER_DAY: int = 3

    # Firebase Cloud Messaging (Phase 1 — legacy server key)
    # Leave empty locally; set in .env for real devices
    FCM_SERVER_KEY: str = ""

    # Admin superuser bootstrap
    ADMIN_EMAIL: str = "admin@psgtech.ac.in"
    ADMIN_INITIAL_CODE: str = "change-me"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8081",
        "http://localhost:19006",
        "http://localhost:5173",
        "*",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
