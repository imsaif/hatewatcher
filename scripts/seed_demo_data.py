#!/usr/bin/env python3
"""Seed demo data for testing the dashboard."""

import asyncio
import random
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import init_db, async_session
from database.models import Channel, Post, Spike, SpikePost


async def seed_demo_data():
    await init_db()

    async with async_session() as session:
        # Create demo channels
        channels = [
            Channel(
                telegram_id=1001,
                username="demo_politics_channel",
                title="Political Discussion",
                country="India",
                language="en",
                category="political",
                member_count=15000,
                is_active=True
            ),
            Channel(
                telegram_id=1002,
                username="demo_news_channel",
                title="Breaking News",
                country="India",
                language="hi",
                category="news",
                member_count=8500,
                is_active=True
            ),
            Channel(
                telegram_id=1003,
                username="demo_community",
                title="Community Forum",
                country="USA",
                language="en",
                category="community",
                member_count=3200,
                is_active=True
            ),
        ]

        for ch in channels:
            session.add(ch)
        await session.flush()

        print(f"Created {len(channels)} demo channels")

        # Create demo posts over the last 7 days
        posts = []
        now = datetime.utcnow()

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

        post_id = 1
        for day in range(7):
            for hour in range(0, 24, 2):
                for channel in channels:
                    # More posts on recent days, simulate a spike
                    num_posts = random.randint(2, 5)
                    if day <= 1 and channel.telegram_id == 1001:
                        num_posts = random.randint(8, 15)  # Spike!

                    for _ in range(num_posts):
                        text, base_toxicity = random.choice(sample_texts)

                        # Add variation and increase toxicity during spike
                        toxicity = base_toxicity + random.uniform(-0.1, 0.1)
                        if day <= 1 and channel.telegram_id == 1001:
                            toxicity = min(0.95, toxicity + 0.2)  # Higher during spike
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
        print(f"Created {len(posts)} demo posts")

        # Create a demo spike
        spike = Spike(
            channel_id=1,  # demo_politics_channel
            country="India",
            spike_start=now - timedelta(hours=36),
            baseline_avg=0.25,
            spike_avg=0.72,
            spike_percentage=188.0,
            post_count=127,
            severity="high",
            is_active=True,
        )
        session.add(spike)
        await session.flush()

        # Link some high-toxicity posts to the spike
        high_tox_posts = [p for p in posts if p.toxicity_score and p.toxicity_score >= 0.7 and p.channel_id == 1]
        for post in high_tox_posts[:50]:
            session.add(SpikePost(spike_id=spike.id, post_id=post.id))

        print(f"Created 1 demo spike with {min(50, len(high_tox_posts))} linked posts")

        await session.commit()
        print("\nDemo data seeded successfully!")
        print("Refresh your dashboard at http://localhost:4000")


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
