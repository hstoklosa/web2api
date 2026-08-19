import httpx
from app.services.scrape_service import fetch_html
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

router = APIRouter(prefix="/build", tags=["build"])


class BuildSchemaRequest(BaseModel):
    url: HttpUrl
    description: str


class BuildSchemaResponse(BaseModel):
    html: str


@router.post("/")
async def build_schema(request: BuildSchemaRequest):
    try:
        html = await fetch_html(str(request.url))
    except httpx.HTTPError:
        raise HTTPException(status_code=500, detail="Failed to fetch the given URL")

    return BuildSchemaResponse(html=html)
