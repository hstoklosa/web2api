import os

import pytest

from app.core.exceptions import SchemaValidationError
from app.core.processes import run_in_process

pytestmark = pytest.mark.anyio


def _raise_app_error(message: str) -> None:
    raise SchemaValidationError(message)


async def test_runs_in_another_process() -> None:
    assert await run_in_process(os.getpid) != os.getpid()


async def test_passes_app_errors_back() -> None:
    with pytest.raises(SchemaValidationError, match="no match"):
        await run_in_process(_raise_app_error, "no match")
