from fastapi import FastAPI


app = FastAPI(title="Business Request Triage API")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a lightweight signal that the API process is available."""
    return {"status": "ok"}
