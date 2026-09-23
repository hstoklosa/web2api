from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyCookie
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AuthenticationError
from app.core.security import ACCESS_COOKIE_NAME, TokenType
from app.models import User
from app.services.user_service import get_user_from_token

# Declared as a security scheme so the OpenAPI docs mark protected routes. A
# missing cookie raises AuthenticationError rather than FastAPI's own error, so
# every 401 has the same shape.
access_cookie_scheme = APIKeyCookie(name=ACCESS_COOKIE_NAME, auto_error=False)

SessionDep = Annotated[AsyncSession, Depends(get_db)]
AccessTokenDep = Annotated[str | None, Depends(access_cookie_scheme)]


async def get_current_user(token: AccessTokenDep, session: SessionDep) -> User:
    if token is None:
        raise AuthenticationError("Not authenticated")
    return await get_user_from_token(session, token, TokenType.ACCESS)


CurrentUserDep = Annotated[User, Depends(get_current_user)]
