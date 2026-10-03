# Velai (Campus Gigs) — Phase 1 MVP

Velai is a campus-only marketplace for **ONE college** where students take small paid gigs from clubs, departments, and approved organisations.

---

## Architecture Overview

- **Backend:** FastAPI (Python), SQLAlchemy Async, Alembic Migrations, Pydantic v2
- **Auth:** JWT tokens with College Email 6-digit OTP verification (`@college.edu`)
- **State Machine:** Centralized enforcement in `backend/app/core/state_machine.py` (`Draft -> Open -> InProgress -> Delivered -> Completed`)
- **Safety:** Automatic keyword-based academic dishonesty filter (blocks homework/exam/proxy gigs from public feed and routes to admin moderation)
- **Payments:** Record-only direct UPI tracking (`paid_by_poster`, `received_by_doer`)

---

## Step 1: Running & Testing the Backend

### 1. Requirements
- Python 3.10+ (tested with Python 3.14)
- Virtual environment in `backend/.venv`

### 2. Environment Setup
The backend environment is configured in `backend/.env` (mirrored from `.env.example`).
```ini
COLLEGE_ID="psg-tech"
COLLEGE_NAME="PSG College of Technology"
COLLEGE_EMAIL_DOMAIN="psgtech.ac.in"
DATABASE_URL="sqlite+aiosqlite:///./velai.db"
MOCK_OTP=True
DEFAULT_TEST_OTP="123456"
```

### 3. Run Database Migrations & Load Seed Data
From the `backend/` directory:
```powershell
# Run migrations
.\.venv\Scripts\alembic.exe -c alembic.ini upgrade head

# Load seed data (5 organisations, 30 users, 15 gigs across lifecycle states) with one command:
.\.venv\Scripts\python.exe -m app.scripts.seed
```

### 4. Start the FastAPI Development Server
From the `backend/` directory:
```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000
```
Interactive API documentation will be available at:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Step-by-Step API Testing Flow

### 1. Request an Email OTP
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "student@psgtech.ac.in"}'
```
*Note: In development (`MOCK_OTP=True`), the code is logged directly to the server console and accepts `123456`.*

### 2. Verify OTP & Obtain JWT
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@psgtech.ac.in",
    "otp_code": "123456",
    "name": "Kavitha Raman",
    "department": "Computer Science",
    "year": 3,
    "role": "student"
  }'
```
Use the returned `access_token` in `Authorization: Bearer <TOKEN>` header.

### 3. Run the Automated Verification Script
To run the automated end-to-end check testing the entire gig lifecycle, invalid state transition rejection, and revision limit boundary:
```powershell
cd backend
.\.venv\Scripts\python.exe verify_step1.py
```
