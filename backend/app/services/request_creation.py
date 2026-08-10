"""Business logic for creating a request and its generated brief."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import BusinessRequest, StructuredBrief
from app.services.brief_generator import BriefGenerator
from app.services.duplicate_detection import has_similar_request, request_fingerprint


class RequestCreationError(Exception):
    """Raised when a request and brief cannot be saved together."""


class DuplicateRequestError(Exception):
    """Raised when an identical normalized request already exists."""

    def __init__(self, request_id: int) -> None:
        self.request_id = request_id


class SimilarRequestError(Exception):
    """Raised when local similarity finds a possible, non-exact duplicate."""


def create_business_request(
    session: Session,
    raw_request: str,
    generator: BriefGenerator,
    *,
    allow_similar: bool = False,
) -> BusinessRequest:
    """Generate and persist a request plus its brief as one transaction."""
    fingerprint = request_fingerprint(raw_request)
    existing_request_id = session.scalar(
        select(BusinessRequest.id).where(BusinessRequest.request_fingerprint == fingerprint)
    )
    if existing_request_id is not None:
        raise DuplicateRequestError(existing_request_id)
    if not allow_similar and has_similar_request(session, raw_request):
        raise SimilarRequestError

    generated_brief = generator.generate(raw_request)
    request = BusinessRequest(raw_request=raw_request, request_fingerprint=fingerprint)
    request.brief = StructuredBrief(**generated_brief.model_dump())
    session.add(request)

    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        existing_request_id = session.scalar(
            select(BusinessRequest.id).where(BusinessRequest.request_fingerprint == fingerprint)
        )
        if existing_request_id is not None:
            raise DuplicateRequestError(existing_request_id) from error
        raise RequestCreationError from error
    except SQLAlchemyError as error:
        session.rollback()
        raise RequestCreationError from error

    session.refresh(request)
    return request
