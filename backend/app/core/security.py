import os
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

import anyio
import anyio.to_thread
import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"


# Argon2 takes tens of milliseconds of CPU per call, which would stall every
# other request if it ran on the event loop, so it runs in worker threads.
# Each call already spreads over 4 lanes and allocates 64 MiB, so a burst of
# logins beyond one call per 4 CPUs only adds memory without adding throughput.
# The dedicated limiter makes that burst queue here rather than take the
# threads FastAPI shares with sync dependencies.
password_hash_limiter = anyio.CapacityLimiter(
    max(1, (os.process_cpu_count() or 1) // 4)
)


async def hash_password(password: str) -> str:
    return await anyio.to_thread.run_sync(
        password_hash.hash, password, limiter=password_hash_limiter
    )


async def verify_password(password: str, hashed_password: str) -> bool:
    return await anyio.to_thread.run_sync(
        password_hash.verify,
        password,
        hashed_password,
        limiter=password_hash_limiter,
    )


def _create_token(
    subject: str,
    token_type: TokenType,
    expires_delta: timedelta,
) -> str:
    expire = datetime.now(UTC) + expires_delta
    claims = {"sub": subject, "exp": expire, "type": token_type.value}
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    return _create_token(
        subject,
        TokenType.ACCESS,
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    return _create_token(
        subject,
        TokenType.REFRESH,
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str, expected_type: TokenType) -> dict[str, Any]:
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={"require": ["exp", "sub", "type"]},
    )
    if payload["type"] != expected_type:
        raise jwt.InvalidTokenError("Unexpected token type")
    return payload
