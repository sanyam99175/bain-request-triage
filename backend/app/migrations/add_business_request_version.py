"""Add optimistic-lock versions to existing SQLite business-request tables."""

from sqlalchemy import inspect, text

from app.database import engine


def upgrade() -> None:
    """Add the version column once, leaving new databases unchanged."""
    if engine.dialect.name != "sqlite":
        raise RuntimeError("This prototype migration supports SQLite only.")

    columns = {column["name"] for column in inspect(engine).get_columns("business_requests")}
    if "version" in columns:
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE business_requests "
                "ADD COLUMN version INTEGER NOT NULL DEFAULT 1"
            )
        )


if __name__ == "__main__":
    upgrade()
