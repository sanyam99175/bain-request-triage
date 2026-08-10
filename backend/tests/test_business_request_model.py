from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import BusinessRequest, StructuredBrief, TriageUpdate  # noqa: F401


def test_persistence_tables_are_created_with_expected_relationships() -> None:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=test_engine)

    inspector = inspect(test_engine)
    request_columns = inspector.get_columns("business_requests")
    brief_foreign_keys = inspector.get_foreign_keys("structured_briefs")
    triage_foreign_keys = inspector.get_foreign_keys("triage_updates")
    brief_constraints = inspector.get_unique_constraints("structured_briefs")
    request_indexes = inspector.get_indexes("business_requests")

    assert set(inspector.get_table_names()) == {
        "auth_sessions",
        "business_requests",
        "structured_briefs",
        "triage_updates",
        "users",
    }
    assert {column["name"] for column in request_columns} == {
        "id",
        "raw_request",
        "request_fingerprint",
        "status",
        "priority",
        "version",
        "owner",
        "notes",
        "created_at",
        "updated_at",
    }
    assert brief_foreign_keys[0]["referred_table"] == "business_requests"
    assert triage_foreign_keys[0]["referred_table"] == "business_requests"
    assert any(constraint["column_names"] == ["request_id"] for constraint in brief_constraints)
    assert any(index["column_names"] == ["created_at", "id"] for index in request_indexes)
    assert any(
        index["column_names"] == ["request_fingerprint"] and index["unique"]
        for index in request_indexes
    )
