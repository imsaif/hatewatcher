from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from database.connection import async_session
from database.models import Spike, SpikePost, Post, Channel
from api.schemas import AlertSchema, AlertDetailSchema, PostSchema

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertSchema])
async def get_alerts(active_only: bool = True, limit: int = 20, country: str | None = None):
    async with async_session() as session:
        query = select(Spike).options(
            selectinload(Spike.channel)
        ).order_by(Spike.created_at.desc()).limit(limit)

        if active_only:
            query = query.where(Spike.is_active == True)

        if country:
            query = query.where(Spike.country == country)

        result = await session.execute(query)
        spikes = result.scalars().all()

        alerts = []
        for spike in spikes:
            posts_result = await session.execute(
                select(Post)
                .join(SpikePost)
                .where(SpikePost.spike_id == spike.id)
                .order_by(Post.toxicity_score.desc())
                .limit(3)
            )
            sample_posts = posts_result.scalars().all()

            alerts.append(AlertSchema(
                id=spike.id,
                channel_id=spike.channel_id,
                channel_username=spike.channel.username if spike.channel else None,
                country=spike.country,
                target_group=spike.target_group,
                severity=spike.severity or "unknown",
                spike_percentage=spike.spike_percentage or 0,
                post_count=spike.post_count or 0,
                baseline_avg=spike.baseline_avg,
                spike_avg=spike.spike_avg,
                started_at=spike.spike_start,
                is_active=spike.is_active,
                sample_posts=[
                    PostSchema(
                        id=p.id,
                        text=p.text[:500],
                        toxicity_score=p.toxicity_score,
                        posted_at=p.posted_at
                    ) for p in sample_posts
                ]
            ))

        return alerts


@router.get("/{alert_id}", response_model=AlertDetailSchema)
async def get_alert(alert_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Spike)
            .options(selectinload(Spike.channel))
            .where(Spike.id == alert_id)
        )
        spike = result.scalar_one_or_none()

        if not spike:
            raise HTTPException(status_code=404, detail="Alert not found")

        posts_result = await session.execute(
            select(Post)
            .join(SpikePost)
            .where(SpikePost.spike_id == spike.id)
            .order_by(Post.toxicity_score.desc())
        )
        posts = posts_result.scalars().all()

        return AlertDetailSchema(
            id=spike.id,
            channel_id=spike.channel_id,
            channel_username=spike.channel.username if spike.channel else None,
            country=spike.country,
            target_group=spike.target_group,
            severity=spike.severity or "unknown",
            spike_percentage=spike.spike_percentage or 0,
            post_count=spike.post_count or 0,
            baseline_avg=spike.baseline_avg,
            spike_avg=spike.spike_avg,
            started_at=spike.spike_start,
            is_active=spike.is_active,
            posts=[
                PostSchema(
                    id=p.id,
                    text=p.text,
                    toxicity_score=p.toxicity_score,
                    posted_at=p.posted_at
                ) for p in posts
            ]
        )
