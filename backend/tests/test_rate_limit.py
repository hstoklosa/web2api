import asyncio
import time
from types import SimpleNamespace

import httpx
import pytest
from fastapi import Depends, FastAPI
from limits.aio.strategies import MovingWindowRateLimiter
from limits.errors import StorageError
from limits.storage import storage_from_string

from app.core import rate_limit as rate_limit_module
from app.core.error_handlers import register_exception_handlers
from app.core.rate_limit import create_limiter, rate_limit
from app.deps import get_current_user


@pytest.fixture
def limiter(monkeypatch: pytest.MonkeyPatch) -> MovingWindowRateLimiter:
    limiter = MovingWindowRateLimiter(storage_from_string("async+memory://"))
    monkeypatch.setattr(rate_limit_module, "limiter", limiter)
    return limiter


def make_client(user_id: int = 1) -> httpx.AsyncClient:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get(
        "/limited",
        dependencies=[Depends(rate_limit("test", "2/minute", "Too many tries"))],
    )
    async def limited() -> None:
        return None

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=user_id)
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    )


@pytest.mark.anyio
async def test_rejects_requests_over_the_limit(limiter: MovingWindowRateLimiter):
    async with make_client() as client:
        assert (await client.get("/limited")).status_code == 200
        assert (await client.get("/limited")).status_code == 200
        response = await client.get("/limited")

    assert response.status_code == 429
    assert response.json()["detail"].startswith("Too many tries, try again in ")
    assert 1 <= int(response.headers["Retry-After"]) <= 60


@pytest.mark.anyio
async def test_counts_each_user_separately(limiter: MovingWindowRateLimiter):
    async with make_client(user_id=1) as client:
        for _ in range(2):
            await client.get("/limited")
        assert (await client.get("/limited")).status_code == 429

    async with make_client(user_id=2) as client:
        assert (await client.get("/limited")).status_code == 200


@pytest.mark.anyio
async def test_allows_requests_when_storage_fails(
    limiter: MovingWindowRateLimiter, monkeypatch: pytest.MonkeyPatch
):
    async def failing_hit(*args: object) -> bool:
        raise StorageError(ConnectionError("Redis is down"))

    monkeypatch.setattr(limiter, "hit", failing_hit)

    async with make_client() as client:
        for _ in range(3):
            assert (await client.get("/limited")).status_code == 200


@pytest.mark.anyio
async def test_allows_requests_when_redis_stops_answering(
    monkeypatch: pytest.MonkeyPatch,
):
    # A server that accepts connections but never replies, like a paused or
    # partitioned Redis.
    async def never_answer(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        await reader.read()

    server = await asyncio.start_server(never_answer, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    monkeypatch.setattr(
        rate_limit_module,
        "limiter",
        create_limiter(f"redis://127.0.0.1:{port}"),
    )

    async with server, make_client() as client:
        started = time.monotonic()
        response = await client.get("/limited")
        elapsed = time.monotonic() - started

    assert response.status_code == 200
    assert elapsed < 2
