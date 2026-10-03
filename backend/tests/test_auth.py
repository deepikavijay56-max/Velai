import pytest
import httpx
from app.core.config import settings


@pytest.mark.asyncio
async def test_otp_request_valid_college_domain(client: httpx.AsyncClient):
    """Users with valid college email receive an OTP."""
    res = await client.post("/api/v1/auth/request-otp", json={"email": "student@psgtech.ac.in"})
    assert res.status_code == 200
    data = res.json()
    assert "Verification code sent" in data["message"]
    assert data["dev_mock_otp"] is not None


@pytest.mark.asyncio
async def test_otp_request_invalid_domain_rejected(client: httpx.AsyncClient):
    """Non-college domains like gmail.com must be rejected."""
    res = await client.post("/api/v1/auth/request-otp", json={"email": "intruder@gmail.com"})
    assert res.status_code == 400
    assert "restricted to college emails" in res.json()["detail"]


@pytest.mark.asyncio
async def test_otp_verify_success(client: httpx.AsyncClient):
    """Correct OTP returns JWT access and refresh tokens with user payload."""
    await client.post("/api/v1/auth/request-otp", json={"email": "arun@psgtech.ac.in"})
    res = await client.post("/api/v1/auth/verify-otp", json={
        "email": "arun@psgtech.ac.in",
        "otp_code": settings.DEV_OTP_CODE,
        "name": "Arun Kumar",
        "department": "Mechanical",
        "year": 4,
        "role": "student"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["college_email"] == "arun@psgtech.ac.in"
    assert data["user"]["college_id"] == "psg-tech"


@pytest.mark.asyncio
async def test_otp_verify_uses_otp_code_field(client: httpx.AsyncClient):
    """The login contract accepts otp_code and rejects the obsolete code key."""
    await client.post("/api/v1/auth/request-otp", json={"email": "login@psgtech.ac.in"})

    old_contract = await client.post("/api/v1/auth/verify-otp", json={
        "email": "login@psgtech.ac.in",
        "code": settings.DEV_OTP_CODE,
    })
    assert old_contract.status_code == 422

    current_contract = await client.post("/api/v1/auth/verify-otp", json={
        "email": "login@psgtech.ac.in",
        "otp_code": settings.DEV_OTP_CODE,
    })
    assert current_contract.status_code == 200
    assert current_contract.json()["access_token"]


@pytest.mark.asyncio
async def test_otp_verify_invalid_code_rejected(client: httpx.AsyncClient):
    """Incorrect OTP must be rejected with 400."""
    await client.post("/api/v1/auth/request-otp", json={"email": "arun@psgtech.ac.in"})
    res = await client.post("/api/v1/auth/verify-otp", json={
        "email": "arun@psgtech.ac.in",
        "otp_code": "999999",
    })
    assert res.status_code == 400
    assert "Invalid or expired" in res.json()["detail"]


@pytest.mark.asyncio
async def test_protected_route_without_token(client: httpx.AsyncClient):
    """Accessing protected /auth/me without Bearer token must return 401."""
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_update_student_skills_and_links(poster_client: httpx.AsyncClient):
    """Students can save their skills with levels and portfolio links."""
    res = await poster_client.put("/api/v1/auth/me/skills", json=[
        {"skill_name": "Figma", "level": "expert", "sample_links": ["https://figma.com/@arun"]},
        {"skill_name": "SolidWorks", "level": "intermediate", "sample_links": []}
    ])
    assert res.status_code == 200
    skills = res.json()
    assert len(skills) == 2
    assert skills[0]["skill_name"] == "Figma"
    assert skills[0]["level"] == "expert"
