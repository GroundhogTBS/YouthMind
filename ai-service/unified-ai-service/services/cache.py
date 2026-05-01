import redis
import json
import logging
from typing import Optional, Any, Dict
from datetime import timedelta

from core.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    def __init__(self):
        self.client = None
        self.enabled = False
        self._connect()

    def _connect(self):
        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.client.ping()
            self.enabled = True
            logger.info(f"Redis connected: {settings.REDIS_URL}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using in-memory fallback")
            self.enabled = False
            self._memory_cache: Dict[str, Any] = {}
            self._memory_ttl: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        try:
            if self.enabled and self.client:
                value = self.client.get(key)
                if value:
                    return json.loads(value)
                return None
            else:
                import time
                if key in self._memory_cache:
                    if key in self._memory_ttl and self._memory_ttl[key] < time.time():
                        del self._memory_cache[key]
                        del self._memory_ttl[key]
                        return None
                    return self._memory_cache[key]
                return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        try:
            if self.enabled and self.client:
                self.client.setex(key, ttl, json.dumps(value, ensure_ascii=False))
                return True
            else:
                import time
                self._memory_cache[key] = value
                self._memory_ttl[key] = time.time() + ttl
                return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        try:
            if self.enabled and self.client:
                self.client.delete(key)
                return True
            else:
                if key in self._memory_cache:
                    del self._memory_cache[key]
                if key in self._memory_ttl:
                    del self._memory_ttl[key]
                return True
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    def incr(self, key: str) -> int:
        try:
            if self.enabled and self.client:
                return self.client.incr(key)
            else:
                current = self._memory_cache.get(key, 0)
                if isinstance(current, int):
                    self._memory_cache[key] = current + 1
                    return current + 1
                return 1
        except Exception as e:
            logger.error(f"Redis incr error: {e}")
            return 0

    def expire(self, key: str, ttl: int) -> bool:
        try:
            if self.enabled and self.client:
                self.client.expire(key, ttl)
                return True
            else:
                import time
                if key in self._memory_cache:
                    self._memory_ttl[key] = time.time() + ttl
                    return True
                return False
        except Exception as e:
            logger.error(f"Redis expire error: {e}")
            return False

    def ttl(self, key: str) -> int:
        try:
            if self.enabled and self.client:
                return self.client.ttl(key)
            else:
                import time
                if key in self._memory_ttl:
                    remaining = int(self._memory_ttl[key] - time.time())
                    return max(0, remaining)
                return -1
        except Exception as e:
            logger.error(f"Redis ttl error: {e}")
            return -1


class SessionCache:
    def __init__(self, redis_cache: RedisCache):
        self.redis = redis_cache
        self.prefix = "session:"

    def set_session(self, session_id: str, user_id: str, ttl: int = 86400) -> bool:
        key = f"{self.prefix}{session_id}"
        return self.redis.set(key, {"user_id": user_id, "created_at": str(ttl)}, ttl)

    def get_session(self, session_id: str) -> Optional[Dict]:
        key = f"{self.prefix}{session_id}"
        return self.redis.get(key)

    def delete_session(self, session_id: str) -> bool:
        key = f"{self.prefix}{session_id}"
        return self.redis.delete(key)


class VerificationCodeCache:
    def __init__(self, redis_cache: RedisCache):
        self.redis = redis_cache
        self.prefix = "verify:"

    def set_code(self, phone: str, code: str, ttl: int = 300) -> bool:
        key = f"{self.prefix}{phone}"
        return self.redis.set(key, {"code": code, "attempts": 0}, ttl)

    def get_code(self, phone: str) -> Optional[Dict]:
        key = f"{self.prefix}{phone}"
        return self.redis.get(key)

    def verify_code(self, phone: str, code: str) -> bool:
        data = self.get_code(phone)
        if not data:
            return False
        if data.get("attempts", 0) >= 5:
            return False
        if data.get("code") == code:
            self.redis.delete(f"{self.prefix}{phone}")
            return True
        data["attempts"] = data.get("attempts", 0) + 1
        self.redis.set(f"{self.prefix}{phone}", data, self.redis.ttl(f"{self.prefix}{phone}"))
        return False

    def increment_attempts(self, phone: str) -> int:
        key = f"{self.prefix}{phone}"
        data = self.redis.get(key)
        if data:
            data["attempts"] = data.get("attempts", 0) + 1
            ttl = self.redis.ttl(key)
            if ttl > 0:
                self.redis.set(key, data, ttl)
            return data["attempts"]
        return 0


class RateLimiter:
    def __init__(self, redis_cache: RedisCache):
        self.redis = redis_cache
        self.prefix = "rate:"

    def is_allowed(self, key: str, max_requests: int = 100, window: int = 60) -> bool:
        redis_key = f"{self.prefix}{key}"
        current = self.redis.incr(redis_key)
        if current == 1:
            self.redis.expire(redis_key, window)
        return current <= max_requests

    def get_remaining(self, key: str, max_requests: int = 100) -> int:
        redis_key = f"{self.prefix}{key}"
        current = self.redis.get(redis_key)
        if current is None:
            return max_requests
        return max(0, max_requests - int(current))


redis_cache = RedisCache()
session_cache = SessionCache(redis_cache)
verification_cache = VerificationCodeCache(redis_cache)
rate_limiter = RateLimiter(redis_cache)
