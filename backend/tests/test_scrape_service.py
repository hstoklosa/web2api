import asyncio
from collections.abc import AsyncIterator, Callable

import httpx
import pytest

from app.core.exceptions import FetchError, FetchTimeoutError
from app.services import scrape_service
from app.services.scrape_service import MAX_RESPONSE_BYTES, fetch_html

pytestmark = pytest.mark.anyio

HTML = {"content-type": "text/html; charset=utf-8"}


async def fetch(
    handler: Callable[[httpx.Request], httpx.Response],
    url: str = "https://example.com/",
) -> str:
    return await fetch_html(url, transport=httpx.MockTransport(handler))


async def test_follows_redirects() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/old":
            return httpx.Response(301, headers={"location": "https://example.com/new"})
        return httpx.Response(200, headers=HTML, text="<p>moved</p>")

    assert await fetch(handler, "http://example.com/old") == "<p>moved</p>"


async def test_too_many_redirects() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        hop = int(request.url.path.strip("/") or 0)
        return httpx.Response(302, headers={"location": f"/{hop + 1}"})

    with pytest.raises(FetchError, match="redirected too many times"):
        await fetch(handler)


async def test_redirect_to_unsupported_scheme() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        # The real transport rejects schemes it cannot speak.
        if request.url.scheme not in ("http", "https"):
            raise httpx.UnsupportedProtocol("unsupported", request=request)
        return httpx.Response(302, headers={"location": "ftp://example.com/"})

    with pytest.raises(FetchError, match="unsupported URL"):
        await fetch(handler)


async def test_error_status() -> None:
    with pytest.raises(FetchError, match="HTTP 404"):
        await fetch(lambda request: httpx.Response(404, headers=HTML))


async def test_rejects_non_html() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, headers={"content-type": "application/pdf"}, content=b"%PDF"
        )

    with pytest.raises(FetchError, match="not HTML"):
        await fetch(handler)


async def test_accepts_missing_content_type() -> None:
    assert (
        await fetch(lambda request: httpx.Response(200, content=b"<p>hi</p>"))
        == "<p>hi</p>"
    )


async def test_rejects_large_content_length() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, headers=HTML, content=b"a" * (MAX_RESPONSE_BYTES + 1)
        )

    with pytest.raises(FetchError, match="larger than"):
        await fetch(handler)


async def test_rejects_large_streamed_body() -> None:
    async def body() -> AsyncIterator[bytes]:
        for _ in range(6):
            yield b"a" * (1024 * 1024)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers=HTML, content=body())

    with pytest.raises(FetchError, match="larger than"):
        await fetch(handler)


async def test_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(scrape_service, "TOTAL_TIMEOUT_SECONDS", 0.05)

    async def handler(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(1)
        return httpx.Response(200, headers=HTML)

    with pytest.raises(FetchTimeoutError):
        await fetch(handler)


async def test_connection_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    with pytest.raises(FetchError, match="Could not connect"):
        await fetch(handler)


@pytest.mark.parametrize(
    ("content_type", "body", "expected"),
    [
        ("text/html; charset=iso-8859-2", "zażółć".encode("iso-8859-2"), "zażółć"),
        ("text/html", "zażółć".encode(), "zażółć"),
        ("text/html; charset=bogus", "zażółć".encode(), "zażółć"),
    ],
)
async def test_decoding(content_type: str, body: bytes, expected: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": content_type}, content=body)

    assert await fetch(handler) == expected


async def test_sends_browser_headers() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, headers=HTML)

    await fetch(handler)

    assert "Chrome/" in seen[0].headers["user-agent"]
    assert seen[0].headers["accept"].startswith("text/html")
