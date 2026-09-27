import threading
import time

import anyio
import pytest

from app.core import security
from app.core.security import hash_password, password_hash_limiter, verify_password

pytestmark = pytest.mark.anyio


async def test_verifies_the_password_it_hashed() -> None:
    hashed = await hash_password("correct horse battery")

    assert await verify_password("correct horse battery", hashed)
    assert not await verify_password("wrong password", hashed)


async def test_hashes_off_the_event_loop_thread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    threads: list[threading.Thread] = []

    def record_thread(password: str) -> str:
        threads.append(threading.current_thread())
        return "hashed"

    monkeypatch.setattr(security.password_hash, "hash", record_thread)

    await hash_password("pw")

    assert threads
    assert threads[0] is not threading.current_thread()


async def test_caps_concurrent_hashes_at_the_limiter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lock = threading.Lock()
    running = 0
    peak = 0

    def slow_verify(password: str, hashed: str) -> bool:
        nonlocal running, peak
        with lock:
            running += 1
            peak = max(peak, running)
        time.sleep(0.02)
        with lock:
            running -= 1
        return True

    monkeypatch.setattr(security.password_hash, "verify", slow_verify)

    async with anyio.create_task_group() as tg:
        for _ in range(int(password_hash_limiter.total_tokens) * 3):
            tg.start_soon(verify_password, "pw", "hashed")

    assert peak == password_hash_limiter.total_tokens
