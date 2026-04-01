import os
import json
import redis
from dotenv import load_dotenv
from decimal import Decimal

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

def _json_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def set(key: str, value, ttl: int = DEFAULT_TTL) -> None:
    if _client is None:
        return
    _client.setex(key, ttl, json.dumps(value, default=_json_default))


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
