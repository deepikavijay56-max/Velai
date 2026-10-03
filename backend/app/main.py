from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
import app.models  # Ensure all models are registered with Base.metadata

from app.api.v1.auth import router as auth_router
from app.api.v1.orgs import router as orgs_router
from app.api.v1.gigs import router as gigs_router
from app.api.v1.applications import router as apps_router
from app.api.v1.contracts import router as contracts_router
from app.api.v1.deliverables import router as deliverables_router
from app.api.v1.payments import router as payments_router
from app.api.v1.chat import router as chat_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Teardown
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Campus-only marketplace for college clubs, departments, and students.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "college_id": settings.COLLEGE_ID,
        "college_name": settings.COLLEGE_NAME,
        "environment": settings.ENVIRONMENT,
    }


# Include v1 routers
API_PREFIX = "/api/v1"
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(orgs_router, prefix=API_PREFIX)
app.include_router(gigs_router, prefix=API_PREFIX)
app.include_router(apps_router, prefix=API_PREFIX)
app.include_router(contracts_router, prefix=API_PREFIX)
app.include_router(deliverables_router, prefix=API_PREFIX)
app.include_router(payments_router, prefix=API_PREFIX)
app.include_router(chat_router, prefix=API_PREFIX)
app.include_router(reviews_router, prefix=API_PREFIX)
app.include_router(notifications_router, prefix=API_PREFIX)
app.include_router(admin_router, prefix=API_PREFIX)
