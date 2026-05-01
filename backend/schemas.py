"""
Pydantic schemas for request validation and response serialization.
"""

from datetime import datetime
from uuid import UUID
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field


# ──────────────────────────────────────────────
# Auth Schemas
# ──────────────────────────────────────────────

class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User info response."""
    id: UUID
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Query Schemas
# ──────────────────────────────────────────────

class QueryCreate(BaseModel):
    """Schema for submitting a new research query."""
    raw_query: str = Field(..., min_length=10, max_length=2000, description="The research question to investigate")


class QueryListResponse(BaseModel):
    """Schema for query list item."""
    id: UUID
    raw_query: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SubQuestionResponse(BaseModel):
    """Schema for a sub-question."""
    id: UUID
    question_text: str
    order_index: int

    model_config = {"from_attributes": True}


class ResearchStepResponse(BaseModel):
    """Schema for a research step."""
    id: UUID
    sub_question_id: UUID
    llm_prompt: str
    llm_response: str
    step_number: int
    created_at: datetime

    model_config = {"from_attributes": True}


class FinalReportResponse(BaseModel):
    """Schema for the final report."""
    id: UUID
    query_id: UUID
    summary: str
    structured_output: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class QueryDetailResponse(BaseModel):
    """Full detail response for a single query."""
    id: UUID
    raw_query: str
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    sub_questions: list[SubQuestionResponse] = []
    research_steps: list[ResearchStepResponse] = []
    final_report: Optional[FinalReportResponse] = None

    model_config = {"from_attributes": True}
