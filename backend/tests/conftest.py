import os
import secrets
import sys
import pytest
import pytest_asyncio
import httpx
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Ensure backend root is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

TEST_DB_URL = "sqlite+aiosqlite:///./test_velai.db"
test_engine = create_async_engine(TEST_DB_URL, echo=False, connect_args={"check_same_thread": False})
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def init_test_db():
    """Create fresh schema before each test and drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def enable_development_otp_for_tests(monkeypatch):
    """Configure a per-test OTP without relying on local environment defaults."""
    monkeypatch.setattr(settings, "DEV_MODE", True)
    monkeypatch.setattr(settings, "DEV_OTP_CODE", f"{secrets.randbelow(1_000_000):06d}")


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def poster_client(client: httpx.AsyncClient) -> httpx.AsyncClient:
    """Provides an authenticated client for a student poster."""
    await client.post("/api/v1/auth/request-otp", json={"email": "club.poster@psgtech.ac.in"})
    res = await client.post("/api/v1/auth/verify-otp", json={
        "email": "club.poster@psgtech.ac.in",
        "otp_code": settings.DEV_OTP_CODE,
        "name": "Karthik Club Lead",
        "department": "Mechanical",
        "year": 4,
        "role": "student"
    })
    token = res.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest_asyncio.fixture
async def doer_client(client: httpx.AsyncClient) -> httpx.AsyncClient:
    """Provides an authenticated client for a student doer/freelancer."""
    # Use separate transport to avoid sharing headers
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as d_client:
        await d_client.post("/api/v1/auth/request-otp", json={"email": "freelancer@psgtech.ac.in"})
        res = await d_client.post("/api/v1/auth/verify-otp", json={
            "email": "freelancer@psgtech.ac.in",
            "otp_code": settings.DEV_OTP_CODE,
            "name": "Pooja Designer",
            "department": "Computer Science",
            "year": 3,
            "role": "student"
        })
        token = res.json()["access_token"]
        d_client.headers["Authorization"] = f"Bearer {token}"
        yield d_client


@pytest_asyncio.fixture
async def admin_client(client: httpx.AsyncClient) -> httpx.AsyncClient:
    """Provides an authenticated client for the campus admin."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as a_client:
        await a_client.post("/api/v1/auth/request-otp", json={"email": settings.ADMIN_EMAIL})
        res = await a_client.post("/api/v1/auth/verify-otp", json={
            "email": settings.ADMIN_EMAIL,
            "otp_code": settings.DEV_OTP_CODE,
            "name": "Dean Admin",
            "role": "admin"
        })
        token = res.json()["access_token"]
        a_client.headers["Authorization"] = f"Bearer {token}"
        yield a_client
