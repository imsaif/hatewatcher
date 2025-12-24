import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.types import Channel as TelegramChannel
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from config import config
from database.connection import async_session
from database.models import Channel, Post

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramScraper:
    def __init__(self):
        self.client = TelegramClient(
            "hatewatch_session",
            config.TELEGRAM_API_ID,
            config.TELEGRAM_API_HASH
        )
        self.channels_file = Path(__file__).parent / "channels.json"

    async def start(self):
        await self.client.start(phone=config.TELEGRAM_PHONE)
        logger.info("Telegram client started")

    async def stop(self):
        await self.client.disconnect()
        logger.info("Telegram client disconnected")

    def load_channels_config(self) -> list[dict]:
        with open(self.channels_file) as f:
            data = json.load(f)
        return data.get("channels", [])

    async def get_or_create_channel(self, session, entity: TelegramChannel, channel_config: dict) -> Channel:
        result = await session.execute(
            select(Channel).where(Channel.telegram_id == entity.id)
        )
        channel = result.scalar_one_or_none()

        if channel:
            channel.member_count = getattr(entity, "participants_count", None)
            channel.updated_at = datetime.utcnow()
        else:
            channel = Channel(
                telegram_id=entity.id,
                username=entity.username,
                title=entity.title,
                member_count=getattr(entity, "participants_count", None),
                country=channel_config.get("country"),
                language=channel_config.get("language"),
                category=channel_config.get("category"),
                is_active=True
            )
            session.add(channel)
            await session.flush()

        return channel

    async def scrape_channel(self, channel_username: str, channel_config: dict, limit: int = 100) -> int:
        try:
            entity = await self.client.get_entity(channel_username)
            if not isinstance(entity, TelegramChannel):
                logger.warning(f"{channel_username} is not a channel")
                return 0

            async with async_session() as session:
                channel = await self.get_or_create_channel(session, entity, channel_config)

                messages_saved = 0
                async for message in self.client.iter_messages(entity, limit=limit):
                    if not message.text:
                        continue

                    stmt = sqlite_insert(Post).values(
                        telegram_message_id=message.id,
                        channel_id=channel.id,
                        text=message.text,
                        posted_at=message.date,
                        views=message.views,
                        forwards=message.forwards,
                        scraped_at=datetime.utcnow()
                    ).on_conflict_do_nothing(
                        index_elements=["channel_id", "telegram_message_id"]
                    )

                    result = await session.execute(stmt)
                    if result.rowcount > 0:
                        messages_saved += 1

                await session.commit()
                logger.info(f"Scraped {messages_saved} new messages from {channel_username}")
                return messages_saved

        except Exception as e:
            logger.error(f"Error scraping {channel_username}: {e}")
            return 0

    async def scrape_all_channels(self, limit: int = 100) -> dict:
        channels_config = self.load_channels_config()
        results = {}

        for channel_config in channels_config:
            username = channel_config.get("username")
            if not username:
                continue

            count = await self.scrape_channel(username, channel_config, limit)
            results[username] = count
            await asyncio.sleep(2)

        return results

    async def run_continuous(self, interval_minutes: int = None):
        if interval_minutes is None:
            interval_minutes = config.SCRAPE_INTERVAL_MINUTES

        await self.start()
        logger.info(f"Starting continuous scraping every {interval_minutes} minutes")

        try:
            while True:
                logger.info("Starting scrape cycle...")
                results = await self.scrape_all_channels()
                total = sum(results.values())
                logger.info(f"Scrape cycle complete. Total new messages: {total}")

                await asyncio.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            logger.info("Stopping scraper...")
        finally:
            await self.stop()


async def main():
    from database.connection import init_db
    await init_db()

    scraper = TelegramScraper()
    await scraper.run_continuous()


if __name__ == "__main__":
    asyncio.run(main())
