from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyCookie, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AuthenticationError
from app.core.security import ACCESS_COOKIE_NAME, TokenType
from app.models import User
from app.services.api_key_service import get_user_from_api_key
from app.services.user_service import get_user_from_token

# Declared as security schemes so the OpenAPI docs mark protected routes. A
# missing credential raises AuthenticationError rather than FastAPI's own
# error, so every 401 has the same shape.
access_cookie_scheme = APIKeyCookie(name=ACCESS_COOKIE_NAME, auto_error=False)
api_key_scheme = HTTPBearer(
    auto_error=False,
    description="An API key created in the app, sent as `Bearer w2a_...`.",
)

SessionDep = Annotated[AsyncSession, Depends(get_db)]
AccessTokenDep = Annotated[str | None, Depends(access_cookie_scheme)]
ApiKeyDep = Annotated[HTTPAuthorizationCredentials | None, Depends(api_key_scheme)]


async def _get_user_from_cookie(token: str | None, session: AsyncSession) -> User:
    if token is None:
        raise AuthenticationError("Not authenticated")
    return await get_user_from_token(session, token, TokenType.ACCESS)


async def get_session_user(
    credentials: ApiKeyDep, token: AccessTokenDep, session: SessionDep
) -> User:
    """Authenticate a browser session only, never an API key."""
    # The browser never sends this header, so only an API client can get here
    # with it, and it should learn why its key was refused.
    if credentials is not None:
        raise AuthenticationError(
            "API keys can't be used for this, sign in to web2api instead"
        )
    return await _get_user_from_cookie(token, session)


async def get_current_user(
    credentials: ApiKeyDep, token: AccessTokenDep, session: SessionDep
) -> User:
    """Authenticate an API key, or else a browser session.

    A request that sends an API key is judged on it alone, so a wrong key
    fails loudly rather than passing on a session cookie sent alongside it.
    """
    if credentials is not None:
        return await get_user_from_api_key(session, credentials.credentials)
    return await _get_user_from_cookie(token, session)


CurrentUserDep = Annotated[User, Depends(get_current_user)]
# For routes a leaked API key must not reach, such as managing API keys.
SessionUserDep = Annotated[User, Depends(get_session_user)]
