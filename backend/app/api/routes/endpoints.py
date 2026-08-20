import httpx
from app.services.schema_service import (
    Schema,
    SchemaGenerationException,
    generate_schema,
)
from app.services.scrape_service import get_html_content
from fastapi import APIRouter, HTTPException
from openai import OpenAIError
from pydantic import BaseModel, Field, HttpUrl

router = APIRouter(prefix="/endpoints", tags=["endpoints"])


class CreateEndpointRequest(BaseModel):
    url: HttpUrl
    description: str = Field(min_length=1)


@router.post("")
async def create_endpoint(request: CreateEndpointRequest) -> Schema:
    try:
        html = await get_html_content(str(request.url))
        schema = await generate_schema(html, request.description)
        return schema
    except httpx.HTTPError:
        raise HTTPException(status_code=500, detail="Failed to fetch the given URL")
    except (OpenAIError, SchemaGenerationException):
        raise HTTPException(
            status_code=502, detail="Failed to generate schema from the given HTML"
        )
