from app.database import SessionLocal, engine


def test_session_factory_uses_configured_engine() -> None:
    session = SessionLocal()

    try:
        assert session.bind is engine
    finally:
        session.close()
