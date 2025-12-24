import asyncio
import logging
from datetime import datetime

from sqlalchemy import select, update

from config import config
from database.connection import async_session
from database.models import Post
from processing.perspective import PerspectiveClient
from processing.language_detect import detect_language

logger = logging.getLogger(__name__)


class ProcessingPipeline:
    def __init__(self):
        self.toxicity_threshold = config.TOXICITY_THRESHOLD

    async def get_unprocessed_posts(self, batch_size: int = 50) -> list[Post]:
        async with async_session() as session:
            result = await session.execute(
                select(Post)
                .where(Post.processed_at.is_(None))
                .order_by(Post.scraped_at.asc())
                .limit(batch_size)
            )
            return result.scalars().all()

    async def process_post(self, post: Post, perspective: PerspectiveClient) -> dict:
        language = detect_language(post.text)

        scores = await perspective.score_text(post.text, language)

        toxicity = scores.get("toxicity")
        is_hate_speech = toxicity is not None and toxicity >= self.toxicity_threshold

        return {
            "text_language": language,
            "toxicity_score": scores.get("toxicity"),
            "severe_toxicity_score": scores.get("severe_toxicity"),
            "identity_attack_score": scores.get("identity_attack"),
            "insult_score": scores.get("insult"),
            "threat_score": scores.get("threat"),
            "is_hate_speech": is_hate_speech,
            "processed_at": datetime.utcnow()
        }

    async def process_batch(self, batch_size: int = 50) -> int:
        posts = await self.get_unprocessed_posts(batch_size)

        if not posts:
            logger.info("No unprocessed posts found")
            return 0

        logger.info(f"Processing {len(posts)} posts...")

        async with PerspectiveClient() as perspective:
            async with async_session() as session:
                for post in posts:
                    try:
                        updates = await self.process_post(post, perspective)

                        await session.execute(
                            update(Post)
                            .where(Post.id == post.id)
                            .values(**updates)
                        )

                    except Exception as e:
                        logger.error(f"Error processing post {post.id}: {e}")
                        continue

                await session.commit()

        logger.info(f"Processed {len(posts)} posts")
        return len(posts)

    async def process_all_unprocessed(self, batch_size: int = 50):
        total = 0
        while True:
            processed = await self.process_batch(batch_size)
            total += processed
            if processed < batch_size:
                break
        logger.info(f"Total processed: {total}")
        return total

    async def run_continuous(self, interval_seconds: int = 30):
        logger.info(f"Starting continuous processing every {interval_seconds} seconds")

        try:
            while True:
                processed = await self.process_batch()
                if processed == 0:
                    await asyncio.sleep(interval_seconds)
                else:
                    await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping processor...")


async def main():
    from database.connection import init_db
    await init_db()

    pipeline = ProcessingPipeline()
    await pipeline.run_continuous()


if __name__ == "__main__":
    asyncio.run(main())
