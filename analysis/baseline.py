import logging
from datetime import datetime, timedelta

from sqlalchemy import select, func

from config import config
from database.connection import async_session
from database.models import Post, Channel

logger = logging.getLogger(__name__)


class BaselineCalculator:
    def __init__(self, days: int = None):
        self.days = days or config.BASELINE_DAYS

    async def calculate_channel_baseline(self, channel_id: int, days: int = None) -> float | None:
        days = days or self.days
        cutoff = datetime.utcnow() - timedelta(days=days)

        async with async_session() as session:
            result = await session.execute(
                select(func.avg(Post.toxicity_score))
                .where(Post.channel_id == channel_id)
                .where(Post.posted_at >= cutoff)
                .where(Post.toxicity_score.isnot(None))
            )
            avg = result.scalar()
            return float(avg) if avg else None

    async def calculate_country_baseline(self, country: str, days: int = None) -> float | None:
        days = days or self.days
        cutoff = datetime.utcnow() - timedelta(days=days)

        async with async_session() as session:
            result = await session.execute(
                select(func.avg(Post.toxicity_score))
                .select_from(Post)
                .join(Channel)
                .where(Channel.country == country)
                .where(Post.posted_at >= cutoff)
                .where(Post.toxicity_score.isnot(None))
            )
            avg = result.scalar()
            return float(avg) if avg else None

    async def calculate_global_baseline(self, days: int = None) -> float | None:
        days = days or self.days
        cutoff = datetime.utcnow() - timedelta(days=days)

        async with async_session() as session:
            result = await session.execute(
                select(func.avg(Post.toxicity_score))
                .where(Post.posted_at >= cutoff)
                .where(Post.toxicity_score.isnot(None))
            )
            avg = result.scalar()
            return float(avg) if avg else None

    async def get_current_average(self, channel_id: int = None, country: str = None, hours: int = 24) -> tuple[float | None, int]:
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        async with async_session() as session:
            query = select(
                func.avg(Post.toxicity_score),
                func.count(Post.id)
            ).where(
                Post.posted_at >= cutoff
            ).where(
                Post.toxicity_score.isnot(None)
            )

            if channel_id:
                query = query.where(Post.channel_id == channel_id)
            elif country:
                query = query.select_from(Post).join(Channel).where(Channel.country == country)

            result = await session.execute(query)
            row = result.one()
            avg, count = row
            return (float(avg) if avg else None, count)
