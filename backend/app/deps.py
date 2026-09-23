from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import TokenType
from app.models import User
from app.services.user_service import get_user_from_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

SessionDep = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(token: TokenDep, session: SessionDep) -> User:
    return await get_user_from_token(session, token, TokenType.ACCESS)


CurrentUserDep = Annotated[User, Depends(get_current_user)]
