from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.models import BusinessRequest  # noqa: F401 - registers model metadata


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create prototype tables when the application starts."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Business Request Triage API", lifespan=lifespan)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a lightweight signal that the API process is available."""
    return {"status": "ok"}
