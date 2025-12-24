#!/usr/bin/env python3
"""
Add or update channels to monitor from channels.json.

Usage:
    python scripts/seed_channels.py
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from database.connection import init_db, async_session
from database.models import Channel


async def main():
    await init_db()
    print("Database initialized")

    channels_file = Path(__file__).parent.parent / "scraper" / "channels.json"

    if not channels_file.exists():
        print(f"Error: {channels_file} not found")
        print("Please create the channels.json file with channels to monitor")
        return

    with open(channels_file) as f:
        data = json.load(f)

    channels = data.get("channels", [])

    if not channels:
        print("No channels found in channels.json")
        return

    async with async_session() as session:
        added = 0
        updated = 0

        for ch in channels:
            username = ch.get("username")
            if not username:
                continue

            result = await session.execute(
                select(Channel).where(Channel.username == username)
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.country = ch.get("country", existing.country)
                existing.language = ch.get("language", existing.language)
                existing.category = ch.get("category", existing.category)
                existing.is_active = True
                updated += 1
                print(f"  Updated: {username}")
            else:
                channel = Channel(
                    telegram_id=0,
                    username=username,
                    country=ch.get("country"),
                    language=ch.get("language"),
                    category=ch.get("category"),
                    is_active=True
                )
                session.add(channel)
                added += 1
                print(f"  Added: {username}")

        await session.commit()

    print(f"\nDone! Added: {added}, Updated: {updated}")
    print("\nNote: telegram_id will be populated when scraper runs")


if __name__ == "__main__":
    asyncio.run(main())
