from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import hash_password, verify_password
from app.models import User


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    return await session.scalar(select(User).where(User.email == email))


async def create_user(session: AsyncSession, email: str, password: str) -> User:
    if await get_user_by_email(session, email) is not None:
        raise ConflictError("A user with this email already exists")

    user = User(email=email, hashed_password=hash_password(password))
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
    if user is None or not verify_password(password, user.hashed_password):
        raise AuthenticationError("Incorrect email or password")
    return user
