from collections.abc import Callable

import anyio.to_process


async def run_in_process[*Ts, R](func: Callable[[*Ts], R], *args: *Ts) -> R:
    """Run CPU-bound pure Python, such as HTML parsing, in a worker process.

    Parsing a large page takes seconds, which would stall every other request
    if it ran on the event loop. A worker thread does not help much, since the
    parser holds the GIL, so the loop would still wait tens of milliseconds
    per step and parses would still run one at a time.

    anyio keeps up to one idle worker per CPU alive for a few minutes, so only
    the first call after a quiet spell pays the process start. `func` must be
    a module-level function, and its arguments, return value and exceptions
    must pickle. Keep logging out of `func`, since worker processes do not
    share the app's logging setup.
    """
    return await anyio.to_process.run_sync(func, *args)
