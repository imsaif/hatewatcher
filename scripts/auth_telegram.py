#!/usr/bin/env python3
"""Authenticate with Telegram - run this once to create session."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from telethon import TelegramClient
from config import config


async def main():
    print("Authenticating with Telegram...")
    print(f"Phone: {config.TELEGRAM_PHONE}")

    client = TelegramClient(
        "hatewatch_session",
        config.TELEGRAM_API_ID,
        config.TELEGRAM_API_HASH
    )

    await client.start(phone=config.TELEGRAM_PHONE)

    me = await client.get_me()
    print(f"\nSuccess! Logged in as: {me.first_name} (@{me.username})")
    print("Session saved. You can now run the scraper.")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
