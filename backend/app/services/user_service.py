import jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import (
    TokenType,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import User


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    return await session.scalar(select(User).where(User.email == email))


async def create_user(session: AsyncSession, email: str, password: str) -> User:
    # Hash before touching the database, since hashing can wait in a queue
    # behind other logins, and a transaction open meanwhile would hold a pooled
    # connection. The unique index on email catches duplicates.
    user = User(email=email, hashed_password=await hash_password(password))
    session.add(user)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise ConflictError("A user with this email already exists") from exc

    await session.refresh(user)
    return user


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User:
    user = await get_user_by_email(session, email)
    # Return the connection to the pool before verifying, which can wait in a
    # queue behind other logins.
    await session.commit()
    if user is None or not await verify_password(password, user.hashed_password):
        raise AuthenticationError("Incorrect email or password")
    return user


async def get_user_from_token(
    session: AsyncSession, token: str, token_type: TokenType
) -> User:
    try:
        payload = decode_token(token, token_type)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise AuthenticationError("Could not validate credentials") from exc

    user = await session.get(User, user_id)
    if user is None:
        raise AuthenticationError("Could not validate credentials")
    return user
