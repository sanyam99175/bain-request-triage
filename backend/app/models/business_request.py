"""Persistence model for an unstructured business request."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.services.duplicate_detection import request_fingerprint

if TYPE_CHECKING:
    from app.models.structured_brief import StructuredBrief
    from app.models.triage_update import TriageUpdate


class BusinessRequest(Base):
    """The original request text submitted for review."""

    __tablename__ = "business_requests"
    __table_args__ = (
        Index("ix_business_requests_created_at_id", "created_at", "id"),
        Index("ix_business_requests_request_fingerprint", "request_fingerprint", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    raw_request: Mapped[str] = mapped_column(Text, nullable=False)
    request_fingerprint: Mapped[str] = mapped_column(
        String(64),
        default=lambda context: request_fingerprint(
            context.get_current_parameters()["raw_request"]
        ),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(50), default="new", nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="medium", nullable=False)
    version: Mapped[int] = mapped_column(default=1, nullable=False)
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
