#!/usr/bin/env python3
"""
Run the processing pipeline to score posts with Perspective API.

Usage:
    python scripts/run_processor.py              # Process all unprocessed
    python scripts/run_processor.py --continuous # Run continuously
"""

import asyncio
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import init_db
from processing.pipeline import ProcessingPipeline


async def main():
    parser = argparse.ArgumentParser(description="Run the processing pipeline")
    parser.add_argument(
        "--continuous", "-c",
        action="store_true",
        help="Run continuously"
    )
    parser.add_argument(
        "--batch-size", "-b",
        type=int,
        default=50,
        help="Batch size for processing (default: 50)"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=30,
        help="Interval in seconds for continuous mode (default: 30)"
    )
    args = parser.parse_args()

    await init_db()
    print("Database initialized")

    pipeline = ProcessingPipeline()

    if args.continuous:
        await pipeline.run_continuous(interval_seconds=args.interval)
    else:
        total = await pipeline.process_all_unprocessed(batch_size=args.batch_size)
        print(f"\nProcessing complete!")
        print(f"Total posts processed: {total}")


if __name__ == "__main__":
    asyncio.run(main())
