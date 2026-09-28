from collections.abc import Sequence
from datetime import timedelta
from uuid import UUID

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.core.security import (
    API_KEY_DISPLAY_LENGTH,
    API_KEY_PREFIX,
    generate_api_key,
    hash_api_key,
)
from app.models import ApiKey, User

MAX_API_KEYS_PER_USER = 25

# Recording every use would write to the database on every API request, so a
# key's last use is only kept to this resolution.
LAST_USED_RESOLUTION = timedelta(minutes=1)


async def create_api_key(
    session: AsyncSession,
    user_id: int,
    name: str,
) -> tuple[ApiKey, str]:
    """Create a key and return it with its plaintext, which is never stored."""
    count = await session.scalar(
        select(func.count()).select_from(ApiKey).where(ApiKey.user_id == user_id)
    )
    if count is not None and count >= MAX_API_KEYS_PER_USER:
        raise ConflictError(
            f"You can have at most {MAX_API_KEYS_PER_USER} API keys, "
            "revoke one you no longer use first"
        )

    key = generate_api_key()
    api_key = ApiKey(
        user_id=user_id,
        name=name,
        prefix=key[:API_KEY_DISPLAY_LENGTH],
        key_hash=hash_api_key(key),
    )
    session.add(api_key)
    await session.commit()
    await session.refresh(api_key)

    return api_key, key


async def get_api_keys_by_user(
    session: AsyncSession,
    user_id: int,
) -> Sequence[ApiKey]:
    result = await session.scalars(
        select(ApiKey)
        .where(ApiKey.user_id == user_id)
        # Newest first, with the id breaking ties so the order is stable.
        .order_by(ApiKey.created_at.desc(), ApiKey.id)
    )
    return result.all()


async def delete_api_key(
    session: AsyncSession,
    id: UUID,
    user_id: int,
) -> None:
    deleted_id = await session.scalar(
        delete(ApiKey)
        .where(ApiKey.id == id, ApiKey.user_id == user_id)
        .returning(ApiKey.id)
    )
    if deleted_id is None:
        raise NotFoundError("API key not found")
    await session.commit()


async def get_user_from_api_key(session: AsyncSession, key: str) -> User:
    if not key.startswith(API_KEY_PREFIX):
        raise AuthenticationError("Invalid API key")

    row = (
        await session.execute(
            select(ApiKey.id, User)
            .join(User, User.id == ApiKey.user_id)
            .where(ApiKey.key_hash == hash_api_key(key))
        )
    ).one_or_none()
    if row is None:
        raise AuthenticationError("Invalid API key")
    api_key_id, user = row

    now = func.now()
    await session.execute(
        update(ApiKey)
        .where(
            ApiKey.id == api_key_id,
            or_(
                ApiKey.last_used_at.is_(None),
                ApiKey.last_used_at < now - LAST_USED_RESOLUTION,
            ),
        )
        .values(last_used_at=now)
    )
    # Committing also returns the connection to the pool before the route
    # does any slow work.
    await session.commit()

    return user
