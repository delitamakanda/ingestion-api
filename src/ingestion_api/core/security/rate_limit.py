from dataclasses import dataclass

from redis.asyncio import Redis


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after: int


SCRIPT = """
local current = redis.call("INCR", KEYS[1])
if current == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[1])
end

local ttl = redis.call("TTL", KEYS[1])
return {current, ttl}
"""


class RedisRateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def is_allowed(
        self, *, key: str, limit: int, window_seconds: int
    ) -> RateLimitResult:
        if limit < 1 or window_seconds < 1:
            raise ValueError("Invalid rate limit policy")

        current, ttl = await self.redis_client.eval(SCRIPT, 1, key, window_seconds)

        allowed = current <= limit

        remaining = max(0, limit - current)
        retry_after = max(1, ttl) if not allowed else 0

        return RateLimitResult(
            allowed=allowed, remaining=remaining, retry_after=retry_after
        )
