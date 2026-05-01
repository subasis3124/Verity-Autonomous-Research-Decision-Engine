"""
Query routes — submit, list, detail, and delete research queries.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db, SYNC_DATABASE_URL
from models import User, Query, QueryStatus
from schemas import QueryCreate, QueryListResponse, QueryDetailResponse
from auth import get_current_user
from services.research_pipeline import run_research_pipeline

router = APIRouter(prefix="/queries", tags=["Queries"])


@router.post("/", response_model=QueryListResponse, status_code=status.HTTP_201_CREATED)
async def submit_query(
    query_data: QueryCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a new research query. Triggers the AI pipeline in the background."""
    new_query = Query(
        user_id=current_user.id,
        raw_query=query_data.raw_query,
        status=QueryStatus.PENDING,
    )
    db.add(new_query)
    await db.flush()
    await db.refresh(new_query)

    # Trigger the background research pipeline
    background_tasks.add_task(run_research_pipeline, str(new_query.id))

    return new_query


@router.get("/", response_model=list[QueryListResponse])
async def list_queries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all queries for the logged-in user, ordered by newest first."""
    result = await db.execute(
        select(Query)
        .where(Query.user_id == current_user.id)
        .order_by(Query.created_at.desc())
    )
    queries = result.scalars().all()
    return queries


@router.get("/{query_id}", response_model=QueryDetailResponse)
async def get_query_detail(
    query_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full detail of a query including sub-questions, research steps, and report."""
    result = await db.execute(
        select(Query)
        .where(Query.id == query_id, Query.user_id == current_user.id)
        .options(
            selectinload(Query.sub_questions),
            selectinload(Query.research_steps),
            selectinload(Query.final_report),
        )
    )
    query = result.scalar_one_or_none()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found.",
        )

    return query


@router.delete("/{query_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_query(
    query_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a query and all its associated data (cascade)."""
    result = await db.execute(
        select(Query).where(Query.id == query_id, Query.user_id == current_user.id)
    )
    query = result.scalar_one_or_none()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found.",
        )

    await db.delete(query)
