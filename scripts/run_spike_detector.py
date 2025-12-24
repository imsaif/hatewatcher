#!/usr/bin/env python3
"""
Run spike detection to find unusual increases in hate speech.

Usage:
    python scripts/run_spike_detector.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import init_db
from analysis.spike_detector import SpikeDetector


async def main():
    await init_db()
    print("Database initialized")

    detector = SpikeDetector()

    print("\nClosing inactive spikes...")
    await detector.close_inactive_spikes()

    print("Detecting new spikes...")
    spikes = await detector.detect_and_save_spikes()

    if spikes:
        print(f"\nDetected {len(spikes)} new spike(s):")
        for spike in spikes:
            print(f"  - Channel ID {spike.channel_id}: {spike.severity} ({spike.spike_percentage:.1f}% increase)")
    else:
        print("\nNo new spikes detected")


if __name__ == "__main__":
    asyncio.run(main())
