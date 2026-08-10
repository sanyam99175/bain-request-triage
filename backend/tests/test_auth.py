from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.services.auth import seed_demo_users


def test_demo_requestor_can_log_in_and_receives_bearer_token() -> None:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session_factory = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        session = test_session_factory()
        seed_demo_users(session)
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).post(
            "/auth/login",
            json={"email": "requestor@demo.local", "password": "requestor-demo"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]
    assert response.json()["user"]["role"] == "requestor"


def test_login_rejects_invalid_password() -> None:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session_factory = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        session = test_session_factory()
        seed_demo_users(session)
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).post(
            "/auth/login",
            json={"email": "requestor@demo.local", "password": "incorrect-password"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_signup_creates_a_role_specific_account_and_rejects_duplicate_email() -> None:
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
    try:
        client = TestClient(app)
        signup_response = client.post(
            "/auth/signup",
            json={
                "email": "new.reviewer@example.com",
                "password": "a-secure-password",
                "role": "reviewer",
            },
        )
        duplicate_response = client.post(
            "/auth/signup",
            json={
                "email": "new.reviewer@example.com",
                "password": "another-secure-password",
                "role": "reviewer",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert signup_response.status_code == 201
    assert signup_response.json()["access_token"]
    assert signup_response.json()["user"] == {
        "id": 1,
        "email": "new.reviewer@example.com",
        "role": "reviewer",
    }
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == "An account with this email already exists."


def test_request_endpoints_enforce_requestor_and_reviewer_roles() -> None:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session_factory = sessionmaker(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        session = test_session_factory()
        seed_demo_users(session)
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        client = TestClient(app)
        unauthenticated_response = client.get("/requests")
        requestor_login = client.post(
            "/auth/login",
            json={"email": "requestor@demo.local", "password": "requestor-demo"},
        )
        reviewer_login = client.post(
            "/auth/login",
            json={"email": "reviewer@demo.local", "password": "reviewer-demo"},
        )
        requestor_headers = {
            "Authorization": f"Bearer {requestor_login.json()['access_token']}"
        }
        reviewer_headers = {
            "Authorization": f"Bearer {reviewer_login.json()['access_token']}"
        }
        forbidden_queue_response = client.get("/requests", headers=requestor_headers)
        reviewer_queue_response = client.get("/requests", headers=reviewer_headers)
        requestor_submission = client.post(
            "/requests",
            headers=requestor_headers,
            json={"raw_request": "Create a secure request workflow."},
        )
        forbidden_submission = client.post(
            "/requests",
            headers=reviewer_headers,
            json={"raw_request": "This reviewer should not submit requests."},
        )
    finally:
        app.dependency_overrides.clear()

    assert unauthenticated_response.status_code == 401
    assert forbidden_queue_response.status_code == 403
    assert reviewer_queue_response.status_code == 200
    assert requestor_submission.status_code == 201
    assert forbidden_submission.status_code == 403
