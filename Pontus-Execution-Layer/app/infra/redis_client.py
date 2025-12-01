import redis.asyncio as redis
from app.config import settings
import json
from typing import Optional, Any

_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = await init_redis()
    return _redis_client


async def init_redis() -> redis.Redis:
    try:
        client = redis.from_url(settings.redis_url, decode_responses=True)
        # Test connection
        await client.ping()
        print("✅ Redis connected successfully")
        return client
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        print("   App will continue but caching features may not work")
        print("   Make sure Redis is running and REDIS_URL is correct")
        # Return a mock client that won't crash
        return None


async def close_redis():
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def cache_set(key: str, value: Any, ttl: int = None):
    try:
        client = await get_redis()
        if client is None:
            return  # Skip caching if Redis not available
        ttl = ttl or settings.redis_ttl
        await client.setex(key, ttl, json.dumps(value, default=str))
    except Exception:
        pass  # Fail silently if caching fails


async def cache_get(key: str) -> Optional[Any]:
    try:
        client = await get_redis()
        if client is None:
            return None
        value = await client.get(key)
        if value:
            return json.loads(value)
    except Exception:
        pass
    return None

