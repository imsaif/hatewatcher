#!/usr/bin/env python3
"""
Run the Telegram scraper.

Usage:
    python scripts/run_scraper.py              # Run once
    python scripts/run_scraper.py --continuous # Run continuously
"""

import asyncio
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import init_db
from scraper.telegram_scraper import TelegramScraper
from config import config


async def main():
    parser = argparse.ArgumentParser(description="Run the Telegram scraper")
    parser.add_argument(
        "--continuous", "-c",
        action="store_true",
        help="Run continuously with interval"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=100,
        help="Number of messages to fetch per channel (default: 100)"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=config.SCRAPE_INTERVAL_MINUTES,
        help=f"Interval in minutes for continuous mode (default: {config.SCRAPE_INTERVAL_MINUTES})"
    )
    args = parser.parse_args()

    await init_db()
    print("Database initialized")

    scraper = TelegramScraper()

    if args.continuous:
        await scraper.run_continuous(interval_minutes=args.interval)
    else:
        await scraper.start()
        try:
            results = await scraper.scrape_all_channels(limit=args.limit)
            total = sum(results.values())
            print(f"\nScraping complete!")
            print(f"Total new messages: {total}")
            for channel, count in results.items():
                print(f"  {channel}: {count}")
        finally:
            await scraper.stop()


if __name__ == "__main__":
    asyncio.run(main())
