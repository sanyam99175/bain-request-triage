"""HTTP endpoints for submitting business requests."""

import base64
import json
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import BusinessRequest, TriageUpdate, User
from app.schemas.requests import (
    BusinessRequestQueueItem,
    BusinessRequestQueuePage,
    BusinessRequestResponse,
    RequestSubmission,
    TriageUpdateResponse,
    TriageUpdateSubmission,
)
from app.services.brief_generator import get_brief_generator
from app.services.request_creation import (
    DuplicateRequestError,
    RequestCreationError,
    SimilarRequestError,
    create_business_request,
)
from app.services.triage import (
    StaleTriageUpdateError,
    TriageUpdateError,
    apply_triage_update,
)
from app.services.authorization import require_role


router = APIRouter(prefix="/requests", tags=["requests"])


def encode_cursor(request: BusinessRequest) -> str:
    """Create an opaque cursor from the final row of a queue page."""
    value = json.dumps([request.created_at.isoformat(), request.id]).encode()
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def decode_cursor(cursor: str) -> tuple[datetime, int]:
    """Parse the timestamp and ID needed for the next keyset page."""
    try:
        padded_cursor = cursor + "=" * (-len(cursor) % 4)
        created_at_value, request_id = json.loads(base64.urlsafe_b64decode(padded_cursor))
        return datetime.fromisoformat(created_at_value), int(request_id)
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="cursor is invalid.",
        ) from error


@router.get("", response_model=BusinessRequestQueuePage)
def list_requests(
    session: Annotated[Session, Depends(get_db)],
    _reviewer: Annotated[User, Depends(require_role("reviewer"))],
    limit: Annotated[int, Query(ge=1, le=100)] = 5,
    cursor: str | None = None,
) -> BusinessRequestQueuePage:
    """Return one newest-first cursor page for the reviewer queue."""
    statement = (
        select(BusinessRequest)
        .options(selectinload(BusinessRequest.brief))
        .order_by(BusinessRequest.created_at.desc(), BusinessRequest.id.desc())
        .limit(limit + 1)
    )
    if cursor:
        cursor_created_at, cursor_id = decode_cursor(cursor)
        statement = statement.where(
            or_(
                BusinessRequest.created_at < cursor_created_at,
                and_(
                    BusinessRequest.created_at == cursor_created_at,
                    BusinessRequest.id < cursor_id,
                ),
            )
        )

    requests = session.scalars(statement).all()
    page_requests = requests[:limit]
    items = [
        BusinessRequestQueueItem(
            id=request.id,
            raw_request=request.raw_request,
            status=request.status,
            priority=request.priority,
            owner=request.owner,
            created_at=request.created_at,
            suggested_next_action=request.brief.suggested_next_action,
        )
        for request in page_requests
    ]
    next_cursor = encode_cursor(page_requests[-1]) if len(requests) > limit else None
    return BusinessRequestQueuePage(items=items, next_cursor=next_cursor)


@router.get("/{request_id}", response_model=BusinessRequestResponse)
def get_request(
    request_id: int,
    session: Annotated[Session, Depends(get_db)],
    _reviewer: Annotated[User, Depends(require_role("reviewer"))],
) -> BusinessRequestResponse:
    """Return one saved request and its structured brief for review."""
    request = session.scalar(
        select(BusinessRequest)
        .options(selectinload(BusinessRequest.brief))
        .where(BusinessRequest.id == request_id)
    )
    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found.",
        )
    return request


@router.get("/{request_id}/triage-history", response_model=list[TriageUpdateResponse])
def list_triage_history(
    request_id: int,
    session: Annotated[Session, Depends(get_db)],
    _reviewer: Annotated[User, Depends(require_role("reviewer"))],
) -> list[TriageUpdateResponse]:
    """Return the complete triage audit history, newest update first."""
    request_exists = session.get(BusinessRequest, request_id)
    if request_exists is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found.",
        )
    return session.scalars(
        select(TriageUpdate)
        .where(TriageUpdate.request_id == request_id)
        .order_by(TriageUpdate.created_at.desc())
    ).all()


@router.patch("/{request_id}/triage", response_model=BusinessRequestResponse)
def update_triage(
    request_id: int,
    payload: TriageUpdateSubmission,
    session: Annotated[Session, Depends(get_db)],
    _reviewer: Annotated[User, Depends(require_role("reviewer"))],
) -> BusinessRequestResponse:
    """Persist a reviewer status or priority decision and its audit entry."""
    request = session.scalar(
        select(BusinessRequest)
        .options(
            selectinload(BusinessRequest.brief),
            selectinload(BusinessRequest.triage_updates),
        )
        .where(BusinessRequest.id == request_id)
    )
    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found.",
        )
    try:
        return apply_triage_update(session, request, payload)
    except StaleTriageUpdateError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This request changed while you were reviewing it. Refresh and try again.",
        ) from error
    except TriageUpdateError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the triage update.",
        ) from error


@router.post("", response_model=BusinessRequestResponse, status_code=status.HTTP_201_CREATED)
def submit_request(
    payload: RequestSubmission,
    session: Annotated[Session, Depends(get_db)],
    _requestor: Annotated[User, Depends(require_role("requestor"))],
) -> BusinessRequestResponse:
    """Save a submitted request with its generated structured brief."""
    generator = get_brief_generator(payload.generation_mode)
    try:
        response = BusinessRequestResponse.model_validate(
            create_business_request(
                session,
                payload.raw_request,
                generator,
                allow_similar=payload.allow_similar,
            )
        )
        response.generation_notice = getattr(generator, "notice", None)
        return response
    except DuplicateRequestError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "exact_duplicate",
                "message": f"An identical request already exists (request #{error.request_id}).",
            },
        ) from error
    except SimilarRequestError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "similar_request",
                "message": "A potentially similar request exists. Review it or submit anyway.",
            },
        ) from error
    except RequestCreationError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the request.",
        ) from error
