"""
Competitors endpoints for managing competitor intelligence
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth_utils import get_user_id_from_header
from app.models.competitor import Competitor
from app.schemas.competitor import (
    CompetitorCreate, CompetitorResponse, CompetitorUpdate
)

router = APIRouter()


@router.get("/", response_model=list[CompetitorResponse])
async def get_competitors(
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get all competitors for a user"""
    try:
        result = await db.execute(
            select(Competitor).where(Competitor.user_id == user_id)
        )
        competitors = result.scalars().all()
        return competitors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch competitors"
        )


@router.post("/", response_model=CompetitorResponse)
async def create_competitor(
    competitor_data: CompetitorCreate,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Create a new competitor"""
    try:
        competitor = Competitor(
            user_id=user_id,
            **competitor_data.dict()
        )
        db.add(competitor)
        await db.commit()
        await db.refresh(competitor)
        return competitor
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create competitor"
        )


@router.get("/{competitor_id}", response_model=CompetitorResponse)
async def get_competitor(
    competitor_id: str,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific competitor"""
    try:
        result = await db.execute(
            select(Competitor).where(
                Competitor.id == competitor_id,
                Competitor.user_id == user_id
            )
        )
        competitor = result.scalar_one_or_none()
        if not competitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Competitor not found"
            )
        return competitor
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch competitor"
        )


@router.put("/{competitor_id}", response_model=CompetitorResponse)
async def update_competitor(
    competitor_id: str,
    competitor_data: CompetitorUpdate,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Update a competitor"""
    try:
        result = await db.execute(
            select(Competitor).where(
                Competitor.id == competitor_id,
                Competitor.user_id == user_id
            )
        )
        competitor = result.scalar_one_or_none()
        if not competitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Competitor not found"
            )
        
        # Update fields
        for field, value in competitor_data.dict(exclude_unset=True).items():
            setattr(competitor, field, value)
        
        await db.commit()
        await db.refresh(competitor)
        return competitor
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update competitor"
        )


@router.delete("/{competitor_id}")
async def delete_competitor(
    competitor_id: str,
    user_id: str = Depends(get_user_id_from_header),
    db: AsyncSession = Depends(get_db)
):
    """Delete a competitor"""
    try:
        result = await db.execute(
            select(Competitor).where(
                Competitor.id == competitor_id,
                Competitor.user_id == user_id
            )
        )
        competitor = result.scalar_one_or_none()
        if not competitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Competitor not found"
            )
        
        await db.delete(competitor)
        await db.commit()
        return {"message": "Competitor deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete competitor"
        )


# (Removed competitor analysis endpoints due to missing models/schemas)
