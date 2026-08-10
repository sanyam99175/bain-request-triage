from app.schemas.requests import GenerationMode
from app.services.brief_generator import GeminiBriefGenerator, get_brief_generator, LiveMockBriefGenerator


def test_live_mock_generator_adapts_to_analytics_request() -> None:
    brief = LiveMockBriefGenerator().generate(
        "Create a dashboard to report customer retention metrics."
    )

    assert brief.recommended_solution_type == "Analytics dashboard"
    assert "Client-facing team" in brief.likely_users
    assert "Which metrics and source systems are required?" in brief.clarifying_questions
    assert brief.suggested_next_action == (
        "Assign a data reviewer to confirm metrics and source-system access."
    )


def test_live_mock_generator_is_deterministic() -> None:
    generator = LiveMockBriefGenerator()
    request = "Automate the manual approval workflow for internal requests."

    assert generator.generate(request) == generator.generate(request)


def test_ai_mode_falls_back_to_mock_when_api_key_is_missing(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    generator = get_brief_generator(GenerationMode.AI)

    brief = generator.generate("Automate internal request approvals.")

    assert brief.recommended_solution_type == "Workflow automation"
    assert generator.notice == (
        "AI generation is unavailable, so this brief was generated using the mock service."
    )


def test_gemini_generator_uses_default_model_when_environment_value_is_blank(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_MODEL", "")

    generator = GeminiBriefGenerator(api_key="test-key")

    assert generator.model == "gemini-3.6-flash"
