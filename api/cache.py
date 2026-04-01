import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()

_client: redis.Redis = None

DEFAULT_TTL = 300  # 5 minutes


def init_cache() -> None:
    global _client
    _client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )


def get(key: str):
    """Return the cached value for key, or None if missing/expired."""
    if _client is None:
        return None
    raw = _client.get(key)
    return json.loads(raw) if raw else None


def set(key: str, value, ttl: int = DEFAULT_TTL) -> None:
    """Cache value as JSON with a TTL (seconds)."""
    if _client is None:
        return
    _client.setex(key, ttl, json.dumps(value))


def invalidate(key: str) -> None:
    """Delete a single cache key."""
    if _client is None:
        return
    _client.delete(key)


def invalidate_pattern(pattern: str) -> None:
    """Delete all keys matching a glob pattern (e.g. 'courses:*')."""
    if _client is None:
        return
    for key in _client.scan_iter(pattern):
        _client.delete(key)
