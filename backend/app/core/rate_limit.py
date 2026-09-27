import logging
import math
import time
from collections.abc import Awaitable, Callable

from coredis.retry import NoRetryPolicy
from limits import parse
from limits.aio.strategies import MovingWindowRateLimiter
from limits.errors import StorageError
from limits.storage import storage_from_string

from app.core.config import settings
from app.core.exceptions import RateLimitedError
from app.deps import CurrentUserDep

logger = logging.getLogger(__name__)

def create_limiter(redis_url: str) -> MovingWindowRateLimiter:
    """Build a limiter whose counters live in Redis, so every worker and
    instance shares them.

    The moving window counts the exact requests in the last period, so a user
    cannot burst twice the limit across a window boundary.

    The client waits forever by default, so a Redis that stops answering
    without refusing the connection would hang every limited request, each
    holding a database connection from get_current_user. Short timeouts turn
    that into a StorageError, which the dependency lets through. Healthy Redis
    answers in well under a millisecond. The client's own retries are off,
    since they would multiply that wait and could count a hit twice when only
    its reply was slow.
    """
    storage = storage_from_string(
        f"async+{redis_url}",
        wrap_exceptions=True,
        connect_timeout=0.5,
        stream_timeout=0.5,
        retry_policy=NoRetryPolicy(),
    )
    return MovingWindowRateLimiter(storage)


limiter = create_limiter(settings.REDIS_URL)


def _format_wait(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''}"
    minutes = math.ceil(seconds / 60)
    return f"{minutes} minute{'s' if minutes != 1 else ''}"


def rate_limit(
    scope: str, limit: str, message: str
) -> Callable[[CurrentUserDep], Awaitable[None]]:
    """Build a dependency that allows each user `limit` requests per `scope`.

    Routes sharing a scope share one budget. `message` tells the user what
    they did too often, and the wait until they can retry is appended to it.
    """
    item = parse(limit)

    async def dependency(user: CurrentUserDep) -> None:
        identifiers = (scope, str(user.id))
        try:
            if await limiter.hit(item, *identifiers):
                return
            stats = await limiter.get_window_stats(item, *identifiers)
        except StorageError as exc:
            # Fail open, so a Redis outage never takes the API down with it.
            logger.error("Rate limit storage failed, allowing request: %s", exc)
            return

        retry_after = max(1, math.ceil(stats.reset_time - time.time()))
        raise RateLimitedError(
            f"{message}, try again in {_format_wait(retry_after)}", retry_after
        )

    return dependency
