import logging
from datetime import datetime, timedelta

from sqlalchemy import select, func

from config import config
from database.connection import async_session
from database.models import Post, Channel, Spike, SpikePost
from analysis.baseline import BaselineCalculator
from analysis.severity import calculate_severity

logger = logging.getLogger(__name__)


class SpikeDetector:
    def __init__(self, threshold: float = None, lookback_hours: int = 24):
        self.threshold = threshold or config.SPIKE_THRESHOLD
        self.lookback_hours = lookback_hours
        self.baseline_calc = BaselineCalculator()

    async def detect_channel_spikes(self) -> list[dict]:
        spikes = []

        async with async_session() as session:
            result = await session.execute(
                select(Channel).where(Channel.is_active == True)
            )
            channels = result.scalars().all()

        for channel in channels:
            spike = await self._check_channel_spike(channel)
            if spike:
                spikes.append(spike)

        return spikes

    async def _check_channel_spike(self, channel: Channel) -> dict | None:
        baseline = await self.baseline_calc.calculate_channel_baseline(channel.id)
        if baseline is None or baseline == 0:
            return None

        current_avg, post_count = await self.baseline_calc.get_current_average(
            channel_id=channel.id,
            hours=self.lookback_hours
        )

        if current_avg is None or post_count < 5:
            return None

        if current_avg >= baseline * self.threshold:
            spike_percentage = ((current_avg - baseline) / baseline) * 100
            severity = calculate_severity(baseline, current_avg)

            return {
                "channel_id": channel.id,
                "channel_username": channel.username,
                "country": channel.country,
                "baseline_avg": baseline,
                "spike_avg": current_avg,
                "spike_percentage": spike_percentage,
                "post_count": post_count,
                "severity": severity
            }

        return None

    async def detect_country_spikes(self) -> list[dict]:
        spikes = []

        async with async_session() as session:
            result = await session.execute(
                select(Channel.country).distinct().where(Channel.country.isnot(None))
            )
            countries = [row[0] for row in result.all()]

        for country in countries:
            spike = await self._check_country_spike(country)
            if spike:
                spikes.append(spike)

        return spikes

    async def _check_country_spike(self, country: str) -> dict | None:
        baseline = await self.baseline_calc.calculate_country_baseline(country)
        if baseline is None or baseline == 0:
            return None

        current_avg, post_count = await self.baseline_calc.get_current_average(
            country=country,
            hours=self.lookback_hours
        )

        if current_avg is None or post_count < 10:
            return None

        if current_avg >= baseline * self.threshold:
            spike_percentage = ((current_avg - baseline) / baseline) * 100
            severity = calculate_severity(baseline, current_avg)

            return {
                "country": country,
                "baseline_avg": baseline,
                "spike_avg": current_avg,
                "spike_percentage": spike_percentage,
                "post_count": post_count,
                "severity": severity
            }

        return None

    async def detect_and_save_spikes(self) -> list[Spike]:
        channel_spikes = await self.detect_channel_spikes()
        saved_spikes = []

        async with async_session() as session:
            for spike_data in channel_spikes:
                existing = await session.execute(
                    select(Spike)
                    .where(Spike.channel_id == spike_data["channel_id"])
                    .where(Spike.is_active == True)
                )
                if existing.scalar_one_or_none():
                    continue

                spike = Spike(
                    channel_id=spike_data["channel_id"],
                    country=spike_data.get("country"),
                    spike_start=datetime.utcnow() - timedelta(hours=self.lookback_hours),
                    baseline_avg=spike_data["baseline_avg"],
                    spike_avg=spike_data["spike_avg"],
                    spike_percentage=spike_data["spike_percentage"],
                    post_count=spike_data["post_count"],
                    severity=spike_data["severity"],
                    is_active=True
                )
                session.add(spike)
                await session.flush()

                cutoff = datetime.utcnow() - timedelta(hours=self.lookback_hours)
                posts_result = await session.execute(
                    select(Post.id)
                    .where(Post.channel_id == spike_data["channel_id"])
                    .where(Post.posted_at >= cutoff)
                    .where(Post.toxicity_score >= config.TOXICITY_THRESHOLD)
                )
                post_ids = [row[0] for row in posts_result.all()]

                for post_id in post_ids:
                    session.add(SpikePost(spike_id=spike.id, post_id=post_id))

                saved_spikes.append(spike)
                logger.info(f"Created spike alert for channel {spike_data['channel_username']}: {spike_data['severity']}")

            await session.commit()

        return saved_spikes

    async def close_inactive_spikes(self):
        async with async_session() as session:
            result = await session.execute(
                select(Spike).where(Spike.is_active == True)
            )
            active_spikes = result.scalars().all()

            for spike in active_spikes:
                current_avg, _ = await self.baseline_calc.get_current_average(
                    channel_id=spike.channel_id,
                    hours=self.lookback_hours
                )

                if current_avg is None or (spike.baseline_avg and current_avg < spike.baseline_avg * self.threshold):
                    spike.is_active = False
                    spike.spike_end = datetime.utcnow()
                    logger.info(f"Closed spike {spike.id}")

            await session.commit()


async def main():
    from database.connection import init_db
    await init_db()

    detector = SpikeDetector()
    spikes = await detector.detect_and_save_spikes()
    print(f"Detected {len(spikes)} new spikes")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
