"""Persistence model for the generated structured brief."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.business_request import BusinessRequest


class StructuredBrief(Base):
    """One generated brief associated with one business request."""

    __tablename__ = "structured_briefs"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(
        ForeignKey("business_requests.id"), unique=True, nullable=False
    )
    problem_summary: Mapped[str] = mapped_column(Text, nullable=False)
    likely_users: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    recommended_solution_type: Mapped[str] = mapped_column(String(255), nullable=False)
    clarifying_questions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    risks: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    suggested_next_action: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    request: Mapped["BusinessRequest"] = relationship(back_populates="brief")
