from datetime import datetime, timedelta
import random

from fastapi import APIRouter, Query
from sqlalchemy import select, func

from database.connection import async_session
from database.models import Post, Channel, Spike, SpikePost
from api.schemas import PostSchema, StatsSchema, TimelineSchema, TimelinePointSchema

router = APIRouter(prefix="/api", tags=["posts"])


@router.post("/seed-demo")
async def seed_demo_data():
    """Seed demo data for testing. Only works if database is empty."""
    async with async_session() as session:
        # Check if already seeded
        result = await session.execute(select(func.count(Channel.id)))
        if result.scalar() > 0:
            return {"message": "Database already has data", "seeded": False}

        # Create demo channels
        channels = [
            Channel(telegram_id=1001, username="demo_politics", title="Political Discussion",
                    country="India", language="en", category="political", member_count=15000, is_active=True),
            Channel(telegram_id=1002, username="demo_news", title="Breaking News",
                    country="India", language="hi", category="news", member_count=8500, is_active=True),
            Channel(telegram_id=1003, username="demo_usa", title="USA Forum",
                    country="USA", language="en", category="community", member_count=3200, is_active=True),
        ]
        for ch in channels:
            session.add(ch)
        await session.flush()

        # Create demo posts
        now = datetime.utcnow()
        sample_texts = [
            ("Normal policy discussion.", 0.15), ("Breaking news update.", 0.08),
            ("These people are ruining everything!", 0.72), ("Hateful content here.", 0.89),
            ("Community event tomorrow.", 0.05), ("They should all leave.", 0.78),
        ]

        post_id = 1
        for day in range(7):
            for hour in range(0, 24, 4):
                for channel in channels:
                    num_posts = random.randint(3, 8)
                    if day <= 1 and channel.telegram_id == 1001:
                        num_posts = random.randint(10, 20)

                    for _ in range(num_posts):
                        text, base_tox = random.choice(sample_texts)
                        toxicity = max(0, min(1, base_tox + random.uniform(-0.1, 0.1)))
                        if day <= 1 and channel.telegram_id == 1001:
                            toxicity = min(0.95, toxicity + 0.2)

                        post = Post(
                            telegram_message_id=post_id, channel_id=channel.id, text=text,
                            posted_at=now - timedelta(days=day, hours=hour, minutes=random.randint(0, 59)),
                            views=random.randint(100, 5000), toxicity_score=toxicity,
                            is_hate_speech=toxicity >= 0.7, processed_at=now,
                            scraped_at=now - timedelta(days=day, hours=hour),
                        )
                        session.add(post)
                        post_id += 1

        await session.flush()

        # Create a spike
        spike = Spike(channel_id=1, country="India", spike_start=now - timedelta(hours=36),
                      baseline_avg=0.25, spike_avg=0.72, spike_percentage=188.0,
                      post_count=127, severity="high", is_active=True)
        session.add(spike)
        await session.commit()

        return {"message": "Demo data seeded!", "seeded": True, "channels": 3, "posts": post_id - 1}


@router.get("/countries")
async def get_countries():
    """Get list of all countries with monitored channels."""
    async with async_session() as session:
        result = await session.execute(
            select(Channel.country)
            .distinct()
            .where(Channel.country.isnot(None))
            .where(Channel.is_active == True)
            .order_by(Channel.country)
        )
        countries = [row[0] for row in result.all()]
        return {"countries": countries}


@router.get("/stats", response_model=StatsSchema)
async def get_stats(country: str | None = None):
    cutoff = datetime.utcnow() - timedelta(hours=24)

    async with async_session() as session:
        # Posts count
        posts_query = select(func.count(Post.id)).where(Post.posted_at >= cutoff)
        if country:
            posts_query = posts_query.select_from(Post).join(Channel).where(Channel.country == country)
        posts_result = await session.execute(posts_query)
        total_posts = posts_result.scalar() or 0

        # Toxicity average
        tox_query = (
            select(func.avg(Post.toxicity_score))
            .where(Post.posted_at >= cutoff)
            .where(Post.toxicity_score.isnot(None))
        )
        if country:
            tox_query = tox_query.select_from(Post).join(Channel).where(Channel.country == country)
        toxicity_result = await session.execute(tox_query)
        avg_toxicity = toxicity_result.scalar()

        # Active spikes
        from database.models import Spike
        spikes_query = select(func.count(Spike.id)).where(Spike.is_active == True)
        if country:
            spikes_query = spikes_query.where(Spike.country == country)
        spikes_result = await session.execute(spikes_query)
        active_spikes = spikes_result.scalar() or 0

        # Channels count
        channels_query = select(func.count(Channel.id)).where(Channel.is_active == True)
        if country:
            channels_query = channels_query.where(Channel.country == country)
        channels_result = await session.execute(channels_query)
        channels_count = channels_result.scalar() or 0

        return StatsSchema(
            total_posts_24h=total_posts,
            avg_toxicity_24h=round(avg_toxicity, 3) if avg_toxicity else None,
            active_spikes=active_spikes,
            channels_monitored=channels_count
        )


@router.get("/timeline", response_model=TimelineSchema)
async def get_timeline(
    channel_id: int | None = None,
    country: str | None = None,
    days: int = Query(default=7, le=30)
):
    cutoff = datetime.utcnow() - timedelta(days=days)

    async with async_session() as session:
        from sqlalchemy import extract

        query = select(
            func.date(Post.posted_at).label("date"),
            func.avg(Post.toxicity_score).label("avg_toxicity"),
            func.count(Post.id).label("post_count")
        ).where(
            Post.posted_at >= cutoff
        ).where(
            Post.toxicity_score.isnot(None)
        ).group_by(
            func.date(Post.posted_at)
        ).order_by(
            func.date(Post.posted_at)
        )

        if channel_id:
            query = query.where(Post.channel_id == channel_id)
        elif country:
            query = query.select_from(Post).join(Channel).where(Channel.country == country)

        result = await session.execute(query)
        rows = result.all()

        timeline = []
        for row in rows:
            # SQLite returns date as string, parse it
            if isinstance(row.date, str):
                date_obj = datetime.strptime(row.date, "%Y-%m-%d")
            else:
                date_obj = datetime.combine(row.date, datetime.min.time())

            timeline.append(TimelinePointSchema(
                timestamp=date_obj,
                avg_toxicity=round(row.avg_toxicity, 3) if row.avg_toxicity else None,
                post_count=row.post_count
            ))

        return TimelineSchema(timeline=timeline)


@router.get("/posts", response_model=list[PostSchema])
async def get_posts(
    channel_id: int | None = None,
    hate_speech_only: bool = False,
    limit: int = Query(default=50, le=200),
    offset: int = 0
):
    async with async_session() as session:
        query = select(Post).options(
            # selectinload for channel if needed
        ).order_by(Post.posted_at.desc()).limit(limit).offset(offset)

        if channel_id:
            query = query.where(Post.channel_id == channel_id)

        if hate_speech_only:
            query = query.where(Post.is_hate_speech == True)

        result = await session.execute(query)
        posts = result.scalars().all()

        return [
            PostSchema(
                id=p.id,
                text=p.text[:500],
                toxicity_score=p.toxicity_score,
                posted_at=p.posted_at
            ) for p in posts
        ]
