from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Endpoint
from app.services.schema_service import (
    generate_endpoint_plan,
)
from app.services.scrape_service import fetch_clean_html
from app.services.validation_service import validate_schema


async def create_endpoint(
    session: AsyncSession,
    user_id: int,
    url: str,
    prompt: str,
) -> Endpoint:
    html = await fetch_clean_html(url)
    plan = await generate_endpoint_plan(html, prompt)

    validate_schema(html, plan.extraction)

    endpoint = Endpoint(
        user_id=user_id,
        name=plan.name,
        url=url,
        description=plan.description,
        extraction_schema=plan.extraction.model_dump(mode="json"),
    )

    session.add(endpoint)
    await session.commit()
    await session.refresh(endpoint)

    return endpoint


async def get_endpoint_by_id(
    session: AsyncSession,
    id: UUID,
    user_id: int,
) -> Endpoint:
    endpoint = await session.scalar(
        select(Endpoint).where(Endpoint.id == id, Endpoint.user_id == user_id)
    )
    if not endpoint:
        raise NotFoundError("Endpoint not found")
    return endpoint


async def get_endpoints_by_user(
    session: AsyncSession,
    user_id: int,
) -> Sequence[Endpoint]:
    result = await session.scalars(
        select(Endpoint)
        .where(Endpoint.user_id == user_id)
        # Newest first, with the id breaking ties so the order is stable.
        .order_by(Endpoint.created_at.desc(), Endpoint.id)
    )
    return result.all()


async def delete_endpoint(
    session: AsyncSession,
    id: UUID,
    user_id: int,
) -> None:
    deleted_id = await session.scalar(
        delete(Endpoint)
        .where(Endpoint.id == id, Endpoint.user_id == user_id)
        .returning(Endpoint.id)
    )
    if deleted_id is None:
        raise NotFoundError("Endpoint not found")
    await session.commit()
