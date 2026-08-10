"""Business logic for reviewer triage updates."""

from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import BusinessRequest, TriageUpdate
from app.schemas.requests import TriageUpdateSubmission


class TriageUpdateError(Exception):
    """Raised when a triage change cannot be saved."""


class StaleTriageUpdateError(Exception):
    """Raised when another reviewer has already changed the request."""


def apply_triage_update(
    session: Session, request: BusinessRequest, triage_update: TriageUpdateSubmission
) -> BusinessRequest:
    """Update current state and save its audit snapshot in one transaction."""
    next_status = (
        triage_update.status.value if triage_update.status is not None else request.status
    )
    next_priority = (
        triage_update.priority.value
        if triage_update.priority is not None
        else request.priority
    )
    next_notes = (
        triage_update.notes
        if "notes" in triage_update.model_fields_set
        else request.notes
    )

    result = session.execute(
        update(BusinessRequest)
        .where(
            BusinessRequest.id == request.id,
            BusinessRequest.version == triage_update.version,
        )
        .values(
            status=next_status,
            priority=next_priority,
            notes=next_notes,
            version=BusinessRequest.version + 1,
        )
    )
    if result.rowcount != 1:
        session.rollback()
        raise StaleTriageUpdateError

    session.add(
        TriageUpdate(
            request=request,
            status=next_status,
            priority=next_priority,
            owner=request.owner,
            notes=next_notes,
        )
    )

    try:
        session.commit()
    except SQLAlchemyError as error:
        session.rollback()
        raise TriageUpdateError from error

    session.refresh(request)
    return request
