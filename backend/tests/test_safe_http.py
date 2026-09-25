import socket
from ipaddress import ip_address

import httpcore
import httpx
import pytest

from app.core import safe_http
from app.core.exceptions import BlockedURLError
from app.core.safe_http import PublicOnlyBackend, PublicOnlyTransport, is_public_address

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize(
    "address",
    ["93.184.215.14", "1.1.1.1", "2606:4700:4700::1111", "64:ff9b::101:101"],
)
def test_public_addresses_are_allowed(address: str) -> None:
    assert is_public_address(ip_address(address))


@pytest.mark.parametrize(
    "address",
    [
        "127.0.0.1",
        "10.0.0.1",
        "172.16.0.1",
        "192.168.1.1",
        "169.254.169.254",
        "100.64.0.1",
        "0.0.0.0",
        "224.0.0.1",
        "255.255.255.255",
        "::1",
        "::",
        "fe80::1",
        "fc00::1",
        "ff02::1",
        "::ffff:127.0.0.1",
        "::ffff:169.254.169.254",
        "64:ff9b::7f00:1",
        "2002:7f00:1::",
    ],
)
def test_private_and_reserved_addresses_are_rejected(address: str) -> None:
    assert not is_public_address(ip_address(address))


def _fake_resolver(*addresses: str):
    async def getaddrinfo(host, port, **kwargs):
        return [
            (
                socket.AF_INET6 if ":" in a else socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                (a, port),
            )
            for a in addresses
        ]

    return getaddrinfo


@pytest.mark.parametrize("answer", [("10.0.0.5",), ("93.184.215.14", "127.0.0.1"), ()])
async def test_connect_rejects_hosts_with_any_non_public_answer(
    monkeypatch: pytest.MonkeyPatch, answer: tuple[str, ...]
) -> None:
    monkeypatch.setattr(safe_http.anyio, "getaddrinfo", _fake_resolver(*answer))

    with pytest.raises(BlockedURLError):
        await PublicOnlyBackend().connect_tcp("example.com", 80)


async def test_connect_uses_the_checked_address(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(safe_http.anyio, "getaddrinfo", _fake_resolver("93.184.215.14"))
    backend = PublicOnlyBackend()
    connected_to: list[str] = []

    async def connect_tcp(host, port, **kwargs):
        connected_to.append(host)
        return object()

    monkeypatch.setattr(backend._backend, "connect_tcp", connect_tcp)

    await backend.connect_tcp("example.com", 80)

    # The connection goes to the IP that passed the check, not back through a
    # second DNS lookup that could return something else.
    assert connected_to == ["93.184.215.14"]


async def test_resolver_failure_becomes_connect_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def getaddrinfo(host, port, **kwargs):
        raise socket.gaierror(socket.EAI_NONAME, "Name or service not known")

    monkeypatch.setattr(safe_http.anyio, "getaddrinfo", getaddrinfo)

    with pytest.raises(httpcore.ConnectError):
        await PublicOnlyBackend().connect_tcp("nope.invalid", 80)


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8000/",
        "http://localhost/",
        "http://[::1]/",
        "http://2130706433/",
        "https://169.254.169.254/latest/meta-data/",
    ],
)
async def test_transport_blocks_private_urls(url: str) -> None:
    # Goes through a real client, so this fails if an httpx upgrade stops
    # routing requests through the pool PublicOnlyTransport installs.
    async with httpx.AsyncClient(transport=PublicOnlyTransport()) as client:
        with pytest.raises(BlockedURLError):
            await client.get(url)
