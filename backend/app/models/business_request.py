"""Persistence model for an unstructured business request."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.structured_brief import StructuredBrief
    from app.models.triage_update import TriageUpdate


class BusinessRequest(Base):
    """The original request text submitted for review."""

    __tablename__ = "business_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    raw_request: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="new", nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="medium", nullable=False)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    brief: Mapped["StructuredBrief | None"] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
        uselist=False,
    )
    triage_updates: Mapped[list["TriageUpdate"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
        order_by="TriageUpdate.created_at",
    )
