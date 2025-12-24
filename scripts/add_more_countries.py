#!/usr/bin/env python3
"""Add more countries to the demo data."""

import asyncio
import random
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import init_db, async_session
from database.models import Channel, Post, Spike, SpikePost


async def add_countries():
    await init_db()

    async with async_session() as session:
        # New channels for more countries
        new_channels = [
            Channel(
                telegram_id=2001,
                username="demo_brazil_politics",
                title="Brazil Political Forum",
                country="Brazil",
                language="pt",
                category="political",
                member_count=12000,
                is_active=True
            ),
            Channel(
                telegram_id=2002,
                username="demo_nigeria_news",
                title="Nigeria News Network",
                country="Nigeria",
                language="en",
                category="news",
                member_count=9500,
                is_active=True
            ),
            Channel(
                telegram_id=2003,
                username="demo_germany_community",
                title="Germany Discussion",
                country="Germany",
                language="de",
                category="community",
                member_count=7800,
                is_active=True
            ),
            Channel(
                telegram_id=2004,
                username="demo_indonesia_forum",
                title="Indonesia Forum",
                country="Indonesia",
                language="id",
                category="political",
                member_count=18000,
                is_active=True
            ),
            Channel(
                telegram_id=2005,
                username="demo_uk_politics",
                title="UK Political Watch",
                country="United Kingdom",
                language="en",
                category="political",
                member_count=11000,
                is_active=True
            ),
            Channel(
                telegram_id=2006,
                username="demo_kenya_news",
                title="Kenya Daily",
                country="Kenya",
                language="en",
                category="news",
                member_count=6500,
                is_active=True
            ),
            Channel(
                telegram_id=2007,
                username="demo_philippines_talk",
                title="Philippines Talk",
                country="Philippines",
                language="en",
                category="community",
                member_count=14000,
                is_active=True
            ),
            Channel(
                telegram_id=2008,
                username="demo_mexico_politica",
                title="Mexico Politica",
                country="Mexico",
                language="es",
                category="political",
                member_count=10500,
                is_active=True
            ),
        ]

        for ch in new_channels:
            session.add(ch)
        await session.flush()

        print(f"Created {len(new_channels)} new channels")

        # Sample texts
        sample_texts = [
            ("This is a normal discussion about policy changes.", 0.15),
            ("I disagree with the government's approach.", 0.22),
            ("These people are ruining our country!", 0.72),
            ("We need to take action against them.", 0.65),
            ("Hateful content targeting minorities.", 0.89),
            ("Breaking: New legislation passed today.", 0.08),
            ("Community event this weekend!", 0.05),
            ("They should all be removed from here.", 0.78),
            ("Dangerous rhetoric spreading online.", 0.71),
            ("Peaceful protest organized for tomorrow.", 0.12),
            ("This group is destroying everything.", 0.68),
            ("Violence is the only answer now.", 0.92),
            ("Let's have a civil discussion.", 0.10),
            ("These outsiders need to leave.", 0.75),
            ("Threatening messages toward community.", 0.85),
        ]

        now = datetime.utcnow()
        posts = []
        post_id = 10000  # Start from high number to avoid conflicts

        for channel in new_channels:
            for day in range(7):
                for hour in range(0, 24, 3):
                    num_posts = random.randint(3, 8)

                    # Create a spike for Brazil (recent)
                    if day <= 1 and channel.country == "Brazil":
                        num_posts = random.randint(10, 18)

                    for _ in range(num_posts):
                        text, base_toxicity = random.choice(sample_texts)
                        toxicity = base_toxicity + random.uniform(-0.1, 0.1)

                        # Higher toxicity during Brazil spike
                        if day <= 1 and channel.country == "Brazil":
                            toxicity = min(0.95, toxicity + 0.25)

                        toxicity = max(0.0, min(1.0, toxicity))

                        post = Post(
                            telegram_message_id=post_id,
                            channel_id=channel.id,
                            text=text,
                            text_language=channel.language,
                            posted_at=now - timedelta(days=day, hours=hour, minutes=random.randint(0, 59)),
                            views=random.randint(100, 5000),
                            forwards=random.randint(0, 50),
                            toxicity_score=toxicity,
                            severe_toxicity_score=toxicity * 0.7,
                            identity_attack_score=toxicity * 0.6,
                            insult_score=toxicity * 0.8,
                            threat_score=toxicity * 0.5,
                            is_hate_speech=toxicity >= 0.7,
                            processed_at=now,
                            scraped_at=now - timedelta(days=day, hours=hour),
                        )
                        posts.append(post)
                        session.add(post)
                        post_id += 1

        await session.flush()
        print(f"Created {len(posts)} new posts")

        # Create spikes for Brazil and Nigeria
        brazil_channel = next(ch for ch in new_channels if ch.country == "Brazil")
        spike1 = Spike(
            channel_id=brazil_channel.id,
            country="Brazil",
            spike_start=now - timedelta(hours=24),
            baseline_avg=0.28,
            spike_avg=0.81,
            spike_percentage=189.0,
            post_count=156,
            severity="high",
            is_active=True,
        )
        session.add(spike1)

        nigeria_channel = next(ch for ch in new_channels if ch.country == "Nigeria")
        spike2 = Spike(
            channel_id=nigeria_channel.id,
            country="Nigeria",
            spike_start=now - timedelta(hours=48),
            baseline_avg=0.22,
            spike_avg=0.45,
            spike_percentage=104.0,
            post_count=67,
            severity="medium",
            is_active=True,
        )
        session.add(spike2)

        await session.flush()

        # Link posts to spikes
        brazil_posts = [p for p in posts if p.channel_id == brazil_channel.id and p.toxicity_score >= 0.7]
        for post in brazil_posts[:60]:
            session.add(SpikePost(spike_id=spike1.id, post_id=post.id))

        nigeria_posts = [p for p in posts if p.channel_id == nigeria_channel.id and p.toxicity_score >= 0.5]
        for post in nigeria_posts[:30]:
            session.add(SpikePost(spike_id=spike2.id, post_id=post.id))

        print("Created 2 new spikes (Brazil: high, Nigeria: medium)")

        await session.commit()
        print("\nNew countries added successfully!")
        print("Countries now available: India, USA, Brazil, Nigeria, Germany, Indonesia, UK, Kenya, Philippines, Mexico")
        print("\nRefresh your dashboard at http://localhost:4000")


if __name__ == "__main__":
    asyncio.run(add_countries())
