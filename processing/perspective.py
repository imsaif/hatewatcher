import asyncio
import logging
from typing import Optional

import httpx
from asyncio_throttle import Throttler

from config import config

logger = logging.getLogger(__name__)

TOXICITY_ATTRIBUTES = [
    "TOXICITY",
    "SEVERE_TOXICITY",
    "IDENTITY_ATTACK",
    "INSULT",
    "THREAT"
]


class PerspectiveClient:
    def __init__(self, api_key: str = None, qps: int = 1):
        self.api_key = api_key or config.PERSPECTIVE_API_KEY
        self.api_url = config.PERSPECTIVE_API_URL
        self.throttler = Throttler(rate_limit=qps, period=1.0)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    def _build_request(self, text: str, language: str = None) -> dict:
        request = {
            "comment": {"text": text[:20480]},
            "requestedAttributes": {attr: {} for attr in TOXICITY_ATTRIBUTES}
        }
        if language:
            request["languages"] = [language]
        return request

    def _parse_response(self, response: dict) -> dict:
        scores = {}
        attribute_scores = response.get("attributeScores", {})

        for attr in TOXICITY_ATTRIBUTES:
            if attr in attribute_scores:
                scores[attr.lower()] = attribute_scores[attr]["summaryScore"]["value"]
            else:
                scores[attr.lower()] = None

        return scores

    async def score_text(self, text: str, language: str = None) -> dict:
        if not text or not text.strip():
            return {attr.lower(): None for attr in TOXICITY_ATTRIBUTES}

        async with self.throttler:
            try:
                request_body = self._build_request(text, language)
                response = await self._client.post(
                    f"{self.api_url}?key={self.api_key}",
                    json=request_body
                )
                response.raise_for_status()
                return self._parse_response(response.json())

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    logger.warning("Rate limited, waiting...")
                    await asyncio.sleep(5)
                    return await self.score_text(text, language)
                logger.error(f"API error: {e.response.status_code} - {e.response.text}")
                return {attr.lower(): None for attr in TOXICITY_ATTRIBUTES}

            except Exception as e:
                logger.error(f"Error scoring text: {e}")
                return {attr.lower(): None for attr in TOXICITY_ATTRIBUTES}

    async def score_batch(self, texts: list[tuple[int, str, str]]) -> list[tuple[int, dict]]:
        results = []
        for post_id, text, language in texts:
            scores = await self.score_text(text, language)
            results.append((post_id, scores))
        return results
