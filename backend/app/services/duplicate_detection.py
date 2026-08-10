"""Deterministic helpers for duplicate business-request detection."""

import hashlib
import re
import unicodedata

from sqlalchemy import select
from sqlalchemy.orm import Session


SIMILARITY_THRESHOLD = 0.7
MIN_SHARED_TOKENS = 3
MAX_COMPARISON_CANDIDATES = 200


def normalize_request_text(raw_request: str) -> str:
    """Return a comparison form insensitive to case, spacing, and punctuation."""
    normalized = unicodedata.normalize("NFKC", raw_request).casefold()
    return re.sub(r"[\W_]+", " ", normalized).strip()


def request_fingerprint(raw_request: str) -> str:
    """Return the stable SHA-256 fingerprint used for exact-duplicate checks."""
    return hashlib.sha256(normalize_request_text(raw_request).encode()).hexdigest()


def request_tokens(raw_request: str) -> set[str]:
    """Return the normalized unique words used for local similarity scoring."""
    return set(normalize_request_text(raw_request).split())


def has_similar_request(session: Session, raw_request: str) -> bool:
    """Check the newest requests for a high, deterministic token-set overlap."""
    from app.models.business_request import BusinessRequest

    candidate_tokens = request_tokens(raw_request)
    if not candidate_tokens:
        return False

    requests = session.scalars(
        select(BusinessRequest)
        .order_by(BusinessRequest.created_at.desc(), BusinessRequest.id.desc())
        .limit(MAX_COMPARISON_CANDIDATES)
    ).all()
    for request in requests:
        existing_tokens = request_tokens(request.raw_request)
        shared_tokens = candidate_tokens & existing_tokens
        if len(shared_tokens) < MIN_SHARED_TOKENS:
            continue
        similarity = len(shared_tokens) / len(candidate_tokens | existing_tokens)
        if similarity >= SIMILARITY_THRESHOLD:
            return True
    return False
