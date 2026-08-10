"""HTTP endpoint for local demo-account login."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    AuthenticatedUserResponse,
    LoginRequest,
    LoginResponse,
    SignupRequest,
)
from app.services.auth import authenticate_user, create_session, register_user


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def signup(
    payload: SignupRequest, session: Annotated[Session, Depends(get_db)]
) -> LoginResponse:
    """Register a local account and return a new opaque bearer token."""
    user = register_user(session, payload.email, payload.password, payload.role)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    return LoginResponse(
        access_token=create_session(session, user),
        user=AuthenticatedUserResponse(id=user.id, email=user.email, role=user.role),
    )


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest, session: Annotated[Session, Depends(get_db)]
) -> LoginResponse:
    """Authenticate a local account and return a new opaque bearer token."""
    user = authenticate_user(session, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    return LoginResponse(
        access_token=create_session(session, user),
        user=AuthenticatedUserResponse(id=user.id, email=user.email, role=user.role),
    )
