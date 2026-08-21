from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Endpoint
from app.services.schema_service import (
    generate_schema,
)
from app.services.scrape_service import fetch_clean_html


async def create_endpoint(
    session: AsyncSession,
    url: str,
    description: str,
) -> Endpoint:
    html = await fetch_clean_html(url)
    schema = await generate_schema(html, description)

    endpoint = Endpoint(
        url=url,
        description=description,
        json_schema=schema.model_dump(mode="json"),
    )

    session.add(endpoint)
    await session.commit()
    await session.refresh(endpoint)

    return endpoint
