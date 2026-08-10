"""Pydantic schemas for submitting and returning business requests."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RequestStatus(str, Enum):
    NEW = "new"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    DEFERRED = "deferred"
    COMPLETED = "completed"


class RequestPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class GenerationMode(str, Enum):
    MOCK = "mock"
    AI = "ai"


class RequestSubmission(BaseModel):
    """Validated input for a new unstructured business request."""

    raw_request: str = Field(max_length=10_000)
    generation_mode: GenerationMode = GenerationMode.MOCK
    allow_similar: bool = False

    @field_validator("raw_request")
    @classmethod
    def raw_request_must_contain_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("raw_request must contain non-whitespace text")
        return value


class GeneratedBrief(BaseModel):
    """The generated fields saved as a structured brief."""

    problem_summary: str
    likely_users: list[str]
    recommended_solution_type: str
    clarifying_questions: list[str]
    risks: list[str]
    suggested_next_action: str


class StructuredBriefResponse(GeneratedBrief):
    """Structured brief fields returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: int
    created_at: datetime


class BusinessRequestResponse(BaseModel):
    """A submitted request and its generated brief."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    raw_request: str
    status: str
    priority: str
    version: int
    owner: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    brief: StructuredBriefResponse
    triage_updates: list["TriageUpdateResponse"]
    generation_notice: str | None = None


class TriageUpdateResponse(BaseModel):
    """An immutable record of one triage decision."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    request_id: int
    status: str
    priority: str
    owner: str | None
    notes: str | None
    created_at: datetime


class TriageUpdateSubmission(BaseModel):
    """The triage fields a reviewer may change in one update."""

    status: RequestStatus | None = None
    priority: RequestPriority | None = None
    notes: str | None = Field(default=None, max_length=5_000)
    version: int = Field(ge=1)

    @field_validator("notes")
    @classmethod
    def trim_notes(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @model_validator(mode="after")
    def includes_a_change(self) -> "TriageUpdateSubmission":
        if (
            self.status is None
            and self.priority is None
            and "notes" not in self.model_fields_set
        ):
            raise ValueError("At least one triage field must be provided")
        return self


class BusinessRequestQueueItem(BaseModel):
    """Compact request data shown in the reviewer queue."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    raw_request: str
    status: str
    priority: str
    owner: str | None
    created_at: datetime
    suggested_next_action: str


class BusinessRequestQueuePage(BaseModel):
    """One cursor-paginated page of reviewer-queue items."""

    items: list[BusinessRequestQueueItem]
    next_cursor: str | None
