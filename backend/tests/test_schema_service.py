import asyncio
import json
from collections.abc import Awaitable, Callable

import httpx2
import pytest
from openai import AsyncOpenAI

from app.core.exceptions import (
    SchemaGenerationBusyError,
    SchemaGenerationError,
    SchemaGenerationTimeoutError,
)
from app.services import schema_service
from app.services.schema_service import generate_endpoint_plan

pytestmark = pytest.mark.anyio

Handler = Callable[[httpx2.Request], httpx2.Response | Awaitable[httpx2.Response]]

PLAN = {
    "extraction": {
        "item_selector": None,
        "fields": [{"name": "title", "selector": "h1"}],
    },
    "name": "page_title",
    "description": "The page title.",
}


def response(content: list[dict]) -> httpx2.Response:
    return httpx2.Response(
        200,
        json={
            "id": "resp_1",
            "object": "response",
            "created_at": 0,
            "model": "test",
            "status": "completed",
            "parallel_tool_calls": False,
            "tool_choice": "auto",
            "tools": [],
            "output": [
                {
                    "type": "message",
                    "id": "msg_1",
                    "role": "assistant",
                    "status": "completed",
                    "content": content,
                }
            ],
        },
    )


def text(value: str) -> httpx2.Response:
    return response([{"type": "output_text", "text": value, "annotations": []}])


def error(status_code: int) -> httpx2.Response:
    return httpx2.Response(
        status_code, json={"error": {"message": "failed", "type": "error"}}
    )


@pytest.fixture
def llm(monkeypatch: pytest.MonkeyPatch) -> Callable[[Handler], None]:
    def install(handler: Handler) -> None:
        client = AsyncOpenAI(
            base_url="https://llm.test/v1",
            api_key="test",
            max_retries=0,
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler)),
        )
        monkeypatch.setattr(schema_service, "openai_client", client)

    return install


async def test_returns_plan(llm: Callable[[Handler], None]) -> None:
    llm(lambda request: text(json.dumps(PLAN)))

    plan = await generate_endpoint_plan("<h1>Hi</h1>", "the title")

    assert plan.name == "page_title"


@pytest.mark.parametrize(
    ("status_code", "error_type", "message"),
    [
        (429, SchemaGenerationBusyError, "busy"),
        (401, SchemaGenerationError, "failed to generate"),
        (404, SchemaGenerationError, "failed to generate"),
        (500, SchemaGenerationError, "failed to generate"),
    ],
)
async def test_maps_error_statuses(
    llm: Callable[[Handler], None],
    status_code: int,
    error_type: type[Exception],
    message: str,
) -> None:
    llm(lambda request: error(status_code))

    with pytest.raises(error_type, match=message) as exc_info:
        await generate_endpoint_plan("<h1>Hi</h1>", "the title")

    assert type(exc_info.value) is error_type


async def test_connection_failure(llm: Callable[[Handler], None]) -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ConnectError("refused", request=request)

    llm(handler)

    with pytest.raises(SchemaGenerationError, match="Could not reach"):
        await generate_endpoint_plan("<h1>Hi</h1>", "the title")


async def test_request_timeout(llm: Callable[[Handler], None]) -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ReadTimeout("slow", request=request)

    llm(handler)

    with pytest.raises(SchemaGenerationTimeoutError):
        await generate_endpoint_plan("<h1>Hi</h1>", "the title")


async def test_total_deadline(
    llm: Callable[[Handler], None], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(schema_service, "TOTAL_TIMEOUT_SECONDS", 0.05)

    async def handler(request: httpx2.Request) -> httpx2.Response:
        await asyncio.sleep(1)
        return text(json.dumps(PLAN))

    llm(handler)

    with pytest.raises(SchemaGenerationTimeoutError):
        await generate_endpoint_plan("<h1>Hi</h1>", "the title")


@pytest.mark.parametrize("output", ['{"name": 1', '{"foo": 1}'])
async def test_invalid_plan(llm: Callable[[Handler], None], output: str) -> None:
    llm(lambda request: text(output))

    with pytest.raises(SchemaGenerationError, match="invalid plan"):
        await generate_endpoint_plan("<h1>Hi</h1>", "the title")


async def test_refusal(llm: Callable[[Handler], None]) -> None:
    llm(lambda request: response([{"type": "refusal", "refusal": "No"}]))

    with pytest.raises(SchemaGenerationError, match="did not return a plan"):
        await generate_endpoint_plan("<h1>Hi</h1>", "the title")
