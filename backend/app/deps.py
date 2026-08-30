from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

SessionDep = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(token: TokenDep, session: SessionDep) -> User:
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise AuthenticationError("Could not validate credentials") from exc

    user = await session.get(User, user_id)
    if user is None:
        raise AuthenticationError("Could not validate credentials")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
