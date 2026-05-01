"""
SQLAlchemy ORM models for Verity.
Defines all 5 database tables: users, queries, sub_questions, research_steps, final_reports.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, DateTime, ForeignKey, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from database import Base


class QueryStatus(str, enum.Enum):
    """Enum for query processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    queries = relationship("Query", back_populates="user", cascade="all, delete-orphan")


class Query(Base):
    """Research query submitted by a user."""
    __tablename__ = "queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    raw_query = Column(Text, nullable=False)
    status = Column(
        SAEnum(QueryStatus, name="query_status", create_constraint=True, values_callable=lambda x: [e.value for e in x]),
        default=QueryStatus.PENDING,
        nullable=False,
    )
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="queries")
    sub_questions = relationship("SubQuestion", back_populates="query", cascade="all, delete-orphan", order_by="SubQuestion.order_index")
    research_steps = relationship("ResearchStep", back_populates="query", cascade="all, delete-orphan", order_by="ResearchStep.step_number")
    final_report = relationship("FinalReport", back_populates="query", uselist=False, cascade="all, delete-orphan")


class SubQuestion(Base):
    """A sub-question decomposed from the main query."""
    __tablename__ = "sub_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("queries.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False)

    # Relationships
    query = relationship("Query", back_populates="sub_questions")
    research_steps = relationship("ResearchStep", back_populates="sub_question", cascade="all, delete-orphan")


class ResearchStep(Base):
    """Research step — an LLM response for a specific sub-question."""
    __tablename__ = "research_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("queries.id", ondelete="CASCADE"), nullable=False)
    sub_question_id = Column(UUID(as_uuid=True), ForeignKey("sub_questions.id", ondelete="CASCADE"), nullable=False)
    llm_prompt = Column(Text, nullable=False)
    llm_response = Column(Text, nullable=False)
    step_number = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    query = relationship("Query", back_populates="research_steps")
    sub_question = relationship("SubQuestion", back_populates="research_steps")


class FinalReport(Base):
    """Synthesized final report for a query."""
    __tablename__ = "final_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("queries.id", ondelete="CASCADE"), nullable=False, unique=True)
    summary = Column(Text, nullable=False)
    structured_output = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    query = relationship("Query", back_populates="final_report")
