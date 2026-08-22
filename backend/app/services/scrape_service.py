import httpx
from bs4 import BeautifulSoup, Comment

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


async def fetch_html(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


async def fetch_clean_html(url: str) -> str:
    raw_html = await fetch_html(url)
    return clean_html(raw_html)
