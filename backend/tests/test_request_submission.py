from fastapi.testclient import TestClient
from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import BusinessRequest, StructuredBrief, TriageUpdate, User
from app.services.authorization import get_current_user


def authorize_as(role: str) -> None:
    app.dependency_overrides[get_current_user] = lambda: User(
        id=1, email=f"{role}@test.local", password_hash="unused", role=role
    )


def test_submit_request_generates_and_persists_brief() -> None:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session_factory = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    authorize_as("requestor")

    try:
        response = TestClient(app).post(
            "/requests",
            json={"raw_request": "  Create a way to triage software requests.  "},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    body = response.json()
    assert body["raw_request"] == "Create a way to triage software requests."
    assert body["status"] == "new"
    assert body["priority"] == "medium"
    assert body["brief"]["problem_summary"] == (
        "The requester needs support with: Create a way to triage software requests."
    )
    assert body["brief"]["recommended_solution_type"] == (
        "Request intake and triage workflow"
    )
    assert len(body["brief"]["clarifying_questions"]) == 2

    with Session(test_engine) as session:
        saved_request = session.scalar(select(BusinessRequest))
        assert saved_request is not None
        assert saved_request.brief is not None
        assert saved_request.brief.suggested_next_action == (
            "Assign a reviewer to validate scope and priority."
        )


def test_submit_request_rejects_an_exact_normalized_duplicate() -> None:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session_factory = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    authorize_as("requestor")
    try:
        client = TestClient(app)
        first_response = client.post(
            "/requests", json={"raw_request": "Create a dashboard for sales."}
        )
        duplicate_response = client.post(
            "/requests", json={"raw_request": "  create a dashboard FOR sales!  "}
        )
    finally:
        app.dependency_overrides.clear()

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == {
        "code": "exact_duplicate",
        "message": "An identical request already exists (request #1).",
    }

    with Session(test_engine) as session:
        assert len(session.scalars(select(BusinessRequest)).all()) == 1


def test_submit_request_warns_about_a_similar_request_until_confirmed() -> None:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session_factory = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    authorize_as("requestor")
    try:
        client = TestClient(app)
        first_response = client.post(
            "/requests",
            json={"raw_request": "Automate approval routing across finance teams."},
        )
        warning_response = client.post(
            "/requests",
            json={"raw_request": "Automate approval routing across finance departments."},
        )
        confirmed_response = client.post(
            "/requests",
            json={
                "raw_request": "Automate approval routing across finance departments.",
                "allow_similar": True,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert first_response.status_code == 201
    assert warning_response.status_code == 409
    assert warning_response.json()["detail"]["code"] == "similar_request"
    assert confirmed_response.status_code == 201


def test_submit_request_uses_mock_and_returns_notice_when_ai_is_unavailable(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session_factory = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    authorize_as("requestor")
    try:
        response = TestClient(app).post(
            "/requests",
            json={
                "raw_request": "Automate internal approvals.",
                "generation_mode": "ai",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["generation_notice"] == (
        "AI generation is unavailable, so this brief was generated using the mock service."
    )
    assert response.json()["brief"]["recommended_solution_type"] == "Workflow automation"


def test_get_request_returns_saved_structured_brief() -> None:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session_factory = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    with Session(test_engine) as session:
        request = BusinessRequest(raw_request="Review our internal request intake process.")
        request.brief = StructuredBrief(
            problem_summary="Review the intake process.",
            likely_users=["Internal reviewer"],
            recommended_solution_type="Workflow triage application",
            clarifying_questions=["Who owns intake?"],
            risks=["Scope is unclear."],
            suggested_next_action="Assign a reviewer.",
        )
        session.add(request)
        session.commit()
        request_id = request.id

    def override_get_db():
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    authorize_as("reviewer")
    try:
        response = TestClient(app).get(f"/requests/{request_id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["brief"]["suggested_next_action"] == "Assign a reviewer."


def test_list_requests_returns_newest_queue_items() -> None:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session_factory = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    with Session(test_engine) as session:
        older_request = BusinessRequest(raw_request="Older request")
        older_request.brief = StructuredBrief(
            problem_summary="Older summary",
            likely_users=["Reviewer"],
            recommended_solution_type="Business process improvement",
            clarifying_questions=["Question"],
            risks=["Risk"],
            suggested_next_action="Review the older request.",
        )
        newer_request = BusinessRequest(raw_request="Newer request")
        newer_request.brief = StructuredBrief(
            problem_summary="Newer summary",
            likely_users=["Reviewer"],
            recommended_solution_type="Business process improvement",
            clarifying_questions=["Question"],
            risks=["Risk"],
            suggested_next_action="Review the newer request.",
        )
        session.add_all([older_request, newer_request])
        session.commit()

    def override_get_db():
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    authorize_as("reviewer")
    try:
        response = TestClient(app).get("/requests")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert [item["raw_request"] for item in response.json()["items"]] == [
        "Newer request",
        "Older request",
    ]
    assert response.json()["items"][0]["suggested_next_action"] == "Review the newer request."


def test_list_requests_returns_following_cursor_page() -> None:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session_factory = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    with Session(test_engine) as session:
        for day in range(1, 4):
            request = BusinessRequest(
                raw_request=f"Request {day}",
                created_at=datetime(2026, 8, day, tzinfo=timezone.utc),
                updated_at=datetime(2026, 8, day, tzinfo=timezone.utc),
            )
            request.brief = StructuredBrief(
                problem_summary=f"Summary {day}",
                likely_users=["Reviewer"],
                recommended_solution_type="Business process improvement",
                clarifying_questions=["Question"],
                risks=["Risk"],
                suggested_next_action=f"Review request {day}.",
            )
            session.add(request)
        session.commit()

    def override_get_db():
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    authorize_as("reviewer")
    try:
        first_page = TestClient(app).get("/requests?limit=2")
        next_cursor = first_page.json()["next_cursor"]
        second_page = TestClient(app).get(f"/requests?limit=2&cursor={next_cursor}")
    finally:
        app.dependency_overrides.clear()

    assert [item["raw_request"] for item in first_page.json()["items"]] == [
        "Request 3",
        "Request 2",
    ]
    assert first_page.json()["next_cursor"] is not None
    assert [item["raw_request"] for item in second_page.json()["items"]] == ["Request 1"]
    assert second_page.json()["next_cursor"] is None


def test_update_triage_changes_request_and_persists_history() -> None:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session_factory = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    with Session(test_engine) as session:
        request = BusinessRequest(raw_request="Triage this request")
        request.brief = StructuredBrief(
            problem_summary="Triage this request.",
            likely_users=["Reviewer"],
            recommended_solution_type="Business process improvement",
            clarifying_questions=["Question"],
            risks=["Risk"],
            suggested_next_action="Review the request.",
        )
        session.add(request)
        session.commit()
        request_id = request.id

    def override_get_db():
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    authorize_as("reviewer")
    try:
        response = TestClient(app).patch(
            f"/requests/{request_id}/triage",
            json={
                "status": "in_review",
                "priority": "high",
                "notes": "  Confirm access requirements.  ",
                "version": 1,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "in_review"
    assert body["priority"] == "high"
    assert body["version"] == 2
    assert body["notes"] == "Confirm access requirements."
    assert len(body["triage_updates"]) == 1
    assert body["triage_updates"][0]["status"] == "in_review"
    assert body["triage_updates"][0]["priority"] == "high"
    assert body["triage_updates"][0]["notes"] == "Confirm access requirements."

    with Session(test_engine) as session:
        saved_request = session.get(BusinessRequest, request_id)
        assert saved_request.status == "in_review"
        assert saved_request.priority == "high"
        assert saved_request.notes == "Confirm access requirements."


def test_update_triage_rejects_a_stale_version_without_creating_history() -> None:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session_factory = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    with Session(test_engine) as session:
        request = BusinessRequest(raw_request="Prevent concurrent triage overwrites")
        request.brief = StructuredBrief(
            problem_summary="Prevent concurrent triage overwrites.",
            likely_users=["Reviewer"],
            recommended_solution_type="Business process improvement",
            clarifying_questions=["Question"],
            risks=["Risk"],
            suggested_next_action="Review the request.",
        )
        session.add(request)
        session.commit()
        request_id = request.id

    def override_get_db():
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    authorize_as("reviewer")
    try:
        client = TestClient(app)
        first_update = client.patch(
            f"/requests/{request_id}/triage",
            json={"status": "in_review", "version": 1},
        )
        stale_update = client.patch(
            f"/requests/{request_id}/triage",
            json={"priority": "high", "version": 1},
        )
    finally:
        app.dependency_overrides.clear()

    assert first_update.status_code == 200
    assert stale_update.status_code == 409
    assert stale_update.json()["detail"] == (
        "This request changed while you were reviewing it. Refresh and try again."
    )

    with Session(test_engine) as session:
        saved_request = session.get(BusinessRequest, request_id)
        assert saved_request.status == "in_review"
        assert saved_request.priority == "medium"
        assert saved_request.version == 2
        assert session.scalars(select(TriageUpdate)).all()
        assert len(session.scalars(select(TriageUpdate)).all()) == 1


def test_list_triage_history_returns_all_updates_newest_first() -> None:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session_factory = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    with Session(test_engine) as session:
        request = BusinessRequest(raw_request="Show complete history")
        request.brief = StructuredBrief(
            problem_summary="History request.",
            likely_users=["Reviewer"],
            recommended_solution_type="Business process improvement",
            clarifying_questions=["Question"],
            risks=["Risk"],
            suggested_next_action="Review history.",
        )
        session.add(request)
        session.flush()
        session.add_all(
            [
                TriageUpdate(
                    request_id=request.id,
                    status="new",
                    priority="medium",
                    created_at=datetime(2026, 8, 7, tzinfo=timezone.utc),
                ),
                TriageUpdate(
                    request_id=request.id,
                    status="in_review",
                    priority="high",
                    created_at=datetime(2026, 8, 8, tzinfo=timezone.utc),
                ),
            ]
        )
        session.commit()
        request_id = request.id

    def override_get_db():
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    authorize_as("reviewer")
    try:
        response = TestClient(app).get(f"/requests/{request_id}/triage-history")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert [update["status"] for update in response.json()] == ["in_review", "new"]
