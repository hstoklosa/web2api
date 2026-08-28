from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Endpoint
from app.services.schema_service import (
    generate_schema,
)
from app.services.scrape_service import fetch_clean_html
from app.services.validation_service import validate_schema


async def create_endpoint(
    session: AsyncSession,
    url: str,
    description: str,
) -> Endpoint:
    html = await fetch_clean_html(url)
    schema = await generate_schema(html, description)

    validate_schema(html, schema)

    endpoint = Endpoint(
        url=url,
        description=description,
        extraction_schema=schema.model_dump(mode="json"),
    )

    session.add(endpoint)
    await session.commit()
    await session.refresh(endpoint)

    return endpoint


async def get_endpoint_by_id(session: AsyncSession, id: UUID) -> Endpoint:
    endpoint = await session.get(Endpoint, id)
    if not endpoint:
        raise NotFoundError("Endpoint not found")
    return endpoint
