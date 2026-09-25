import asyncio
import codecs

import httpx
from bs4 import BeautifulSoup, Comment

from app.core.exceptions import FetchError, FetchTimeoutError
from app.core.safe_http import PublicOnlyTransport

MAX_RESPONSE_BYTES = 5 * 1024 * 1024
MAX_REDIRECTS = 5
REQUEST_TIMEOUT = httpx.Timeout(10.0, connect=5.0)
TOTAL_TIMEOUT_SECONDS = 20

# Many sites turn away clients that don't look like a browser.
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

_HTML_MEDIA_TYPES = frozenset({"text/html", "application/xhtml+xml"})

_NOISE_TAGS = frozenset(
    {
        "script",
        "style",
        "noscript",
        "iframe",
        "embed",
        "object",
        "applet",
        "svg",
        "canvas",
        "template",
        "link",
        "meta",
        "base",
    }
)


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # drop noise tags
    for tag in soup.find_all(_NOISE_TAGS):
        tag.decompose()

    # drop comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # drop inline CSS and JS event handlers
    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr == "style" or attr.startswith("on"):
                del tag.attrs[attr]

    root = soup.body or soup
    return root.decode_contents().strip()


def _check_content_type(response: httpx.Response) -> None:
    content_type = response.headers.get("content-type", "")
    media_type = content_type.split(";")[0].strip().lower()
    if media_type and media_type not in _HTML_MEDIA_TYPES:
        raise FetchError(f"The page is not HTML (it is {media_type})")


async def _read_limited(response: httpx.Response) -> bytes:
    too_large = FetchError(
        f"The page is larger than {MAX_RESPONSE_BYTES // (1024 * 1024)} MB"
    )
    content_length = response.headers.get("content-length", "")
    if content_length.isdigit() and int(content_length) > MAX_RESPONSE_BYTES:
        raise too_large

    # Count the decompressed bytes, so a small compressed body cannot expand
    # past the limit.
    body = bytearray()
    async for chunk in response.aiter_bytes():
        body += chunk
        if len(body) > MAX_RESPONSE_BYTES:
            raise too_large
    return bytes(body)


def _decode(body: bytes, charset: str | None) -> str:
    try:
        encoding = codecs.lookup(charset or "utf-8").name
    except LookupError:
        encoding = "utf-8"
    return body.decode(encoding, errors="replace")


async def fetch_html(
    url: str, transport: httpx.AsyncBaseTransport | None = None
) -> str:
    try:
        # The read timeout applies per chunk, so this also bounds servers that
        # trickle the body out slowly.
        async with asyncio.timeout(TOTAL_TIMEOUT_SECONDS):
            async with httpx.AsyncClient(
                transport=transport or PublicOnlyTransport(),
                headers=REQUEST_HEADERS,
                timeout=REQUEST_TIMEOUT,
                follow_redirects=True,
                max_redirects=MAX_REDIRECTS,
                trust_env=False,
            ) as client:
                async with client.stream("GET", url) as response:
                    response.raise_for_status()
                    _check_content_type(response)
                    body = await _read_limited(response)
                    return _decode(body, response.charset_encoding)
    except (TimeoutError, httpx.TimeoutException) as exc:
        raise FetchTimeoutError("The page took too long to respond") from exc
    except httpx.HTTPStatusError as exc:
        raise FetchError(
            f"The page responded with HTTP {exc.response.status_code}"
        ) from exc
    except httpx.TooManyRedirects as exc:
        raise FetchError("The page redirected too many times") from exc
    except httpx.UnsupportedProtocol as exc:
        raise FetchError("The page redirected to an unsupported URL") from exc
    except httpx.RequestError as exc:
        raise FetchError("Could not connect to the page's server") from exc


async def fetch_clean_html(url: str) -> str:
    raw_html = await fetch_html(url)
    return clean_html(raw_html)
