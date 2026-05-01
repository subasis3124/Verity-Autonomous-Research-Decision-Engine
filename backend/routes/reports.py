"""
Report routes — fetch the final report for a query.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User, Query, FinalReport
from schemas import FinalReportResponse
from auth import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{query_id}", response_model=FinalReportResponse)
async def get_report(
    query_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch the final synthesized report for a given query."""
    # Verify the query belongs to the current user
    query_result = await db.execute(
        select(Query).where(Query.id == query_id, Query.user_id == current_user.id)
    )
    query = query_result.scalar_one_or_none()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found.",
        )

    # Fetch the report
    report_result = await db.execute(
        select(FinalReport).where(FinalReport.query_id == query_id)
    )
    report = report_result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not yet available. The query may still be processing.",
        )

    return report
