import asyncio
import string
import uuid

from db import collection, redis_client
from models import URLModel

BASE_62_ALPHABET = string.ascii_letters + string.digits         # A-Z, a-z, 0-9 -> 62 characters


def base_62_encode(num: int) -> str:
    """Encodes an integer into BASE62 string for short URLS """
    if num == 0:
        return BASE_62_ALPHABET[0]

    encoded = ""
    while num:
        num, rem = divmod(num, 62)
        encoded = BASE_62_ALPHABET[rem] + encoded
    return encoded


def generate_short_url():
    """Generates a BASE62 short URL from a UUID"""
    unique_id = uuid.uuid4().int
    return base_62_encode(unique_id)[:8]


async def save_url_to_db(long_url: str) -> str:
    """Saves the long URL in MongoDB and generates the short_url"""
    short_url = generate_short_url()
    url_data = URLModel(short_url=short_url, long_url=long_url)
    await collection.insert_one(url_data.model_dump(by_alias=True, exclude_none=True))
    return short_url


async def get_or_cache_short_url(short_url: str) -> str | None:
    """Fetch short URL from Redis if it exists; if not found, query MongoDB and cache frequently accessed URLs."""

    long_url = await redis_client.get(f"url:{short_url}")

    if long_url:
        print("Cache Hit")
        return long_url.decode() if isinstance(long_url, bytes) else long_url  # Handle bytes if needed

    # If not found in cache, check MongoDB
    url_entry = await collection.find_one({"_id": short_url})
    print("@@@", url_entry)

    if url_entry:
        long_url = url_entry["long_url"]

        # Use a separate key for tracking accesses
        access_count = await redis_client.get(f"access:{short_url}")
        access_count = int(access_count) if access_count else 0  # Default to 0 if not found

        # Increment access count (in a separate key!)
        await redis_client.incr(f"access:{short_url}")

        # Cache only if accessed at least 5 times
        if access_count >= 5:
            await redis_client.set(f"url:{short_url}", long_url, ex=86400)

        return long_url

    return None


async def track_clicks(short_url: str):
    """Tracks the number of clicks on the short URL"""
    await redis_client.incr(short_url)


async def get_clicks(short_url: str) -> int:
    """Returns the number of times a short URL was accessed."""
    return int(await redis_client.get(f"clicks:{short_url}") or 0)
