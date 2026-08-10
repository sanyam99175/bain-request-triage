"""Pydantic schemas for local authentication."""

from typing import Literal

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class SignupRequest(LoginRequest):
    role: Literal["requestor", "reviewer"]


class AuthenticatedUserResponse(BaseModel):
    id: int
    email: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthenticatedUserResponse
