"""Add and backfill exact-duplicate fingerprints in the SQLite prototype DB."""

from sqlalchemy import inspect, text

from app.database import engine
from app.services.duplicate_detection import request_fingerprint


def upgrade() -> None:
    """Add the fingerprint column and unique index without discarding existing data."""
    if engine.dialect.name != "sqlite":
        raise RuntimeError("This prototype migration supports SQLite only.")
    if "business_requests" not in inspect(engine).get_table_names():
        return

    columns = {column["name"] for column in inspect(engine).get_columns("business_requests")}
    with engine.begin() as connection:
        if "request_fingerprint" not in columns:
            connection.execute(text("ALTER TABLE business_requests ADD COLUMN request_fingerprint TEXT"))

        requests = connection.execute(
            text("SELECT id, raw_request FROM business_requests ORDER BY id")
        ).mappings()
        fingerprints: set[str] = set()
        for request in requests:
            fingerprint = request_fingerprint(request["raw_request"])
            if fingerprint in fingerprints:
                fingerprint = request_fingerprint(
                    f"legacy duplicate {request['id']} {fingerprint}"
                )
            fingerprints.add(fingerprint)
            connection.execute(
                text(
                    "UPDATE business_requests "
                    "SET request_fingerprint = :fingerprint WHERE id = :request_id"
                ),
                {"fingerprint": fingerprint, "request_id": request["id"]},
            )

        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_business_requests_request_fingerprint "
                "ON business_requests (request_fingerprint)"
            )
        )


if __name__ == "__main__":
    upgrade()
