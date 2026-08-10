"""Swappable mock and optional Gemini brief generation."""

from abc import ABC, abstractmethod
import logging
import os

import httpx
from dotenv import load_dotenv

from app.schemas.requests import GeneratedBrief, GenerationMode


logger = logging.getLogger(__name__)
load_dotenv()
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
BRIEF_SCHEMA = {
    "type": "object",
    "properties": {
        "problem_summary": {"type": "string"},
        "likely_users": {"type": "array", "items": {"type": "string"}},
        "recommended_solution_type": {"type": "string"},
        "clarifying_questions": {"type": "array", "items": {"type": "string"}},
        "risks": {"type": "array", "items": {"type": "string"}},
        "suggested_next_action": {"type": "string"},
    },
    "required": [
        "problem_summary",
        "likely_users",
        "recommended_solution_type",
        "clarifying_questions",
        "risks",
        "suggested_next_action",
    ],
}


class BriefGenerator(ABC):
    """Contract implemented by any service that turns text into a brief."""

    @abstractmethod
    def generate(self, raw_request: str) -> GeneratedBrief:
        """Generate the required structured brief fields."""


class AIGenerationError(Exception):
    """Raised when the optional live AI provider cannot generate a brief."""


class LiveMockBriefGenerator(BriefGenerator):
    """Input-sensitive local generator that simulates a brief-generation service."""

    def generate(self, raw_request: str) -> GeneratedBrief:
        normalized_request = " ".join(raw_request.split())
        request_terms = normalized_request.casefold()
        solution_type = self._solution_type_for(request_terms)

        return GeneratedBrief(
            problem_summary=(
                f"The requester needs support with: {normalized_request}"
            ),
            likely_users=self._likely_users_for(request_terms),
            recommended_solution_type=solution_type,
            clarifying_questions=self._questions_for(solution_type),
            risks=self._risks_for(normalized_request),
            suggested_next_action=self._next_action_for(solution_type),
        )

    @staticmethod
    def _solution_type_for(request_terms: str) -> str:
        if any(term in request_terms for term in ("dashboard", "report", "analytics")):
            return "Analytics dashboard"
        if any(term in request_terms for term in ("automate", "automation", "workflow")):
            return "Workflow automation"
        if any(term in request_terms for term in ("request", "intake", "triage", "prioritize")):
            return "Request intake and triage workflow"
        return "Business process improvement"

    @staticmethod
    def _likely_users_for(request_terms: str) -> list[str]:
        users = ["Business request sponsor", "Internal reviewer"]
        if any(term in request_terms for term in ("client", "customer")):
            users.append("Client-facing team")
        if any(term in request_terms for term in ("manager", "leadership", "executive")):
            users.append("Business leadership")
        return users

    @staticmethod
    def _questions_for(solution_type: str) -> list[str]:
        questions = [
            "What outcome would define success?",
            "Which team should own this request?",
        ]
        if solution_type == "Analytics dashboard":
            questions.append("Which metrics and source systems are required?")
        elif solution_type == "Workflow automation":
            questions.append("Which manual steps should be automated first?")
        return questions

    @staticmethod
    def _risks_for(normalized_request: str) -> list[str]:
        risks = ["The request may not include enough implementation detail."]
        if len(normalized_request.split()) < 12:
            risks.append("The short description may conceal important scope constraints.")
        else:
            risks.append("The scope may change after reviewer feedback.")
        return risks

    @staticmethod
    def _next_action_for(solution_type: str) -> str:
        if solution_type == "Analytics dashboard":
            return "Assign a data reviewer to confirm metrics and source-system access."
        if solution_type == "Workflow automation":
            return "Assign an operations reviewer to map the current manual workflow."
        return "Assign a reviewer to validate scope and priority."


class GeminiBriefGenerator(BriefGenerator):
    """Gemini REST implementation that requests the application's brief JSON shape."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL") or "gemini-3.6-flash"

    def generate(self, raw_request: str) -> GeneratedBrief:
        if not self.api_key:
            raise AIGenerationError("GEMINI_API_KEY is not configured")

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "Create a concise business-request brief from the text below. "
                                "Return only JSON matching the requested schema. Do not invent "
                                "confidential facts.\n\n"
                                f"Business request: {raw_request}"
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseJsonSchema": BRIEF_SCHEMA,
            },
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    GEMINI_API_URL.format(model=self.model),
                    headers={"x-goog-api-key": self.api_key},
                    json=payload,
                )
                response.raise_for_status()
            generated_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return GeneratedBrief.model_validate_json(generated_text)
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as error:
            raise AIGenerationError("Gemini did not return a usable brief") from error


class FallbackBriefGenerator(BriefGenerator):
    """Uses the mock generator when an optional live generator is unavailable."""

    def __init__(self, primary: BriefGenerator, fallback: BriefGenerator) -> None:
        self.primary = primary
        self.fallback = fallback
        self.notice: str | None = None

    def generate(self, raw_request: str) -> GeneratedBrief:
        try:
            return self.primary.generate(raw_request)
        except Exception as error:
            logger.warning("AI brief generation failed; using mock fallback: %s", type(error).__name__)
            self.notice = "AI generation is unavailable, so this brief was generated using the mock service."
            return self.fallback.generate(raw_request)


def get_brief_generator(mode: GenerationMode = GenerationMode.MOCK) -> BriefGenerator:
    """Select mock by default, or an AI generator with a safe mock fallback."""
    mock_generator = LiveMockBriefGenerator()
    if mode == GenerationMode.AI:
        return FallbackBriefGenerator(GeminiBriefGenerator(), mock_generator)
    return mock_generator
