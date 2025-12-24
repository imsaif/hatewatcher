#!/usr/bin/env python3
"""
Backfill historical data from Telegram channels.

Usage:
    python scripts/backfill.py --limit 500  # Fetch 500 messages per channel
"""

import asyncio
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import init_db
from scraper.telegram_scraper import TelegramScraper
from processing.pipeline import ProcessingPipeline


async def main():
    parser = argparse.ArgumentParser(description="Backfill historical data")
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=500,
        help="Number of messages to fetch per channel (default: 500)"
    )
    parser.add_argument(
        "--process", "-p",
        action="store_true",
        help="Also process messages after scraping"
    )
    args = parser.parse_args()

    await init_db()
    print("Database initialized")

    scraper = TelegramScraper()
    await scraper.start()

    try:
        print(f"\nBackfilling up to {args.limit} messages per channel...")
        results = await scraper.scrape_all_channels(limit=args.limit)
        total = sum(results.values())

        print(f"\nBackfill complete!")
        print(f"Total new messages: {total}")
        for channel, count in results.items():
            print(f"  {channel}: {count}")

        if args.process and total > 0:
            print("\nProcessing scraped messages...")
            pipeline = ProcessingPipeline()
            processed = await pipeline.process_all_unprocessed()
            print(f"Processed {processed} messages")

    finally:
        await scraper.stop()


if __name__ == "__main__":
    asyncio.run(main())
