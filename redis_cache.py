import os
import redis.asyncio as redis
import json
import hashlib
from utils import MusicItem
import config


redis_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=0,
    decode_responses=True,  # строки вместо bytes
)


def make_cache_key(query: str, limit: int, provider) -> str:
    raw = f"mailru:search:{query}:{limit}:{provider}"
    digest = hashlib.sha256(raw.encode()).hexdigest()
    return f"search:{digest}"


async def cache_get(key: str) -> list[dict] | None:
    data = await redis_client.get(key)
    if not data:
        return None
    return json.loads(data)


async def cache_set(key: str, value: list[MusicItem]) -> None:
    await redis_client.set(
        key,
        json.dumps(value, ensure_ascii=False),
        ex=config.CACHE_TTL,
    )