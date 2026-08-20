from dataclasses import dataclass
from uuid import UUID

import httpx
from openai import OpenAIError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Endpoint
from app.services.schema_service import (
    Schema,
    SchemaGenerationException,
    generate_schema,
)
from app.services.scrape_service import get_html_content


class SourceFetchError(Exception):
    pass


class EndpointSchemaGenerationError(Exception):
    pass


class EndpointPersistenceError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class CreatedEndpoint:
    id: UUID
    url: str
    description: str
    schema: Schema


async def create_endpoint(
    db: AsyncSession,
    url: str,
    description: str,
) -> CreatedEndpoint:
    try:
        html = await get_html_content(url)
    except httpx.HTTPError as exc:
        raise SourceFetchError from exc

    try:
        schema = await generate_schema(html, description)
    except (OpenAIError, SchemaGenerationException) as exc:
        raise EndpointSchemaGenerationError from exc

    endpoint = Endpoint(
        url=url,
        description=description,
        json_schema=schema.model_dump(mode="json"),
    )

    try:
        db.add(endpoint)
        await db.commit()
    except SQLAlchemyError as exc:
        await db.rollback()
        raise EndpointPersistenceError from exc

    return CreatedEndpoint(
        id=endpoint.id,
        url=endpoint.url,
        description=endpoint.description,
        schema=schema,
    )
