from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, SessionLocal, engine
from app import models  # noqa: F401 - registers all model metadata
from app.routes.auth import router as auth_router
from app.routes.requests import router as requests_router
from app.services.auth import seed_demo_users


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create prototype tables when the application starts."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_demo_users(session)
    yield


app = FastAPI(title="Business Request Triage API", lifespan=lifespan)
@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "PATCH", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
app.include_router(requests_router)
app.include_router(auth_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a lightweight signal that the API process is available."""
    return {"status": "ok"}
