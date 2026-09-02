import json
import logging
from typing import Optional, Any
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheClient:
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._enabled = settings.CACHE_ENABLED
        self._init_connection()

    def _init_connection(self):
        if not self._enabled:
            return
        try:
            self._redis = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=1.0,
                socket_timeout=1.0
            )
            # Test ping
            self._redis.ping()
            logger.info("Connected to Redis cache at %s", settings.REDIS_URL)
        except Exception as e:
            logger.warning("Redis is unavailable (%s). Falling back to non-cached mode.", e)
            self._redis = None

    @property
    def is_available(self) -> bool:
        return self._redis is not None

    def get(self, key: str) -> Optional[Any]:
        if not self._redis:
            return None
        try:
            val = self._redis.get(key)
            if val is not None:
                return json.loads(val)
        except Exception as e:
            logger.warning("Redis GET error for key '%s': %s", key, e)
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if not self._redis:
            return False
        try:
            exp = ttl if ttl is not None else settings.CACHE_TTL_SECONDS
            self._redis.set(key, json.dumps(value), ex=exp)
            return True
        except Exception as e:
            logger.warning("Redis SET error for key '%s': %s", key, e)
            return False

    def delete(self, *keys: str) -> bool:
        if not self._redis or not keys:
            return False
        try:
            self._redis.delete(*keys)
            return True
        except Exception as e:
            logger.warning("Redis DELETE error: %s", e)
            return False

    def delete_prefix(self, prefix: str) -> int:
        """Invalidate all keys starting with prefix."""
        if not self._redis:
            return 0
        try:
            count = 0
            cursor = 0
            while True:
                cursor, keys = self._redis.scan(cursor=cursor, match=f"{prefix}*", count=100)
                if keys:
                    self._redis.delete(*keys)
                    count += len(keys)
                if cursor == 0:
                    break
            return count
        except Exception as e:
            logger.warning("Redis delete_prefix error for '%s': %s", prefix, e)
            return 0


# Global cache client instance
cache_client = CacheClient()
