import socket
from collections.abc import Iterable
from ipaddress import IPv4Address, IPv6Address, IPv6Network, ip_address

import anyio
import httpcore
import httpx

from app.core.exceptions import BlockedURLError

# NAT64 gateways translate this prefix to the IPv4 address in its last 32 bits,
# so those addresses are only as public as the IPv4 address they embed.
_NAT64_NETWORK = IPv6Network("64:ff9b::/96")

# Loading the CA bundle is slow, so every transport shares one context.
_SSL_CONTEXT = httpx.create_ssl_context(trust_env=False)


def is_public_address(ip: IPv4Address | IPv6Address) -> bool:
    if isinstance(ip, IPv6Address):
        if ip.ipv4_mapped is not None:
            ip = ip.ipv4_mapped
        elif ip in _NAT64_NETWORK:
            ip = IPv4Address(int(ip) & 0xFFFFFFFF)
    return ip.is_global and not ip.is_multicast


class PublicOnlyBackend(httpcore.AsyncNetworkBackend):
    """Opens TCP connections only to public IP addresses.

    The host is resolved here and the connection is made to the checked
    address, so a DNS answer that changes between check and connect cannot
    redirect it. TLS still verifies the certificate against the hostname,
    since httpcore passes the origin host to start_tls after connecting.
    """

    def __init__(self) -> None:
        self._backend = httpcore.AnyIOBackend()

    async def connect_tcp(
        self,
        host: str,
        port: int,
        timeout: float | None = None,
        local_address: str | None = None,
        socket_options: Iterable[httpcore.SOCKET_OPTION] | None = None,
    ) -> httpcore.AsyncNetworkStream:
        try:
            with anyio.fail_after(timeout):
                infos = await anyio.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        except TimeoutError as exc:
            raise httpcore.ConnectTimeout(f"Timed out resolving {host}") from exc
        except OSError as exc:
            raise httpcore.ConnectError(f"Could not resolve {host}: {exc}") from exc

        # Deduplicate while keeping the resolver's preferred order.
        addresses = list(dict.fromkeys(ip_address(info[4][0]) for info in infos))
        # Reject the host if any answer is private, since a mix of public and
        # private addresses is how DNS rebinding attacks usually look.
        if not addresses or not all(is_public_address(ip) for ip in addresses):
            raise BlockedURLError(
                "This URL points to a private or reserved network address"
            )

        last_error: Exception | None = None
        for ip in addresses:
            try:
                return await self._backend.connect_tcp(
                    str(ip),
                    port,
                    timeout=timeout,
                    local_address=local_address,
                    socket_options=socket_options,
                )
            except (httpcore.ConnectError, httpcore.ConnectTimeout) as exc:
                last_error = exc
        assert last_error is not None
        raise last_error

    async def connect_unix_socket(
        self,
        path: str,
        timeout: float | None = None,
        socket_options: Iterable[httpcore.SOCKET_OPTION] | None = None,
    ) -> httpcore.AsyncNetworkStream:
        raise BlockedURLError("Unix sockets are not allowed")

    async def sleep(self, seconds: float) -> None:
        await self._backend.sleep(seconds)


class PublicOnlyTransport(httpx.AsyncHTTPTransport):
    """An httpx transport whose every connection, including each redirect hop,
    goes through PublicOnlyBackend."""

    def __init__(self) -> None:
        super().__init__(verify=_SSL_CONTEXT, trust_env=False)
        # httpx does not expose httpcore's network_backend option, so replace
        # the pool it built. tests/test_safe_http.py fails if an httpx upgrade
        # stops routing requests through this pool.
        self._pool = httpcore.AsyncConnectionPool(
            ssl_context=_SSL_CONTEXT,
            network_backend=PublicOnlyBackend(),
        )
