from uuid import UUID

from app.deps import CurrentUserDep, SessionDep
from app.schemas.endpoint import (
    CreateEndpointRequest,
    CreateEndpointResponse,
    GetEndpointResponse,
)
from app.schemas.extract import ExtractionSchema
from app.services.endpoint_service import create_endpoint as create_endpoint_service
from app.services.endpoint_service import get_endpoint_by_id
from app.services.extraction_service import extract_data
from app.services.scrape_service import fetch_clean_html
from fastapi import APIRouter, status

router = APIRouter(prefix="/endpoints", tags=["endpoints"])


@router.post(
    "",
    response_model=CreateEndpointResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_endpoint(
    request: CreateEndpointRequest,
    session: SessionDep,
    user: CurrentUserDep,
) -> CreateEndpointResponse:
    endpoint = await create_endpoint_service(
        session=session,
        user_id=user.id,
        url=str(request.url),
        description=request.description,
    )
    schema = ExtractionSchema.model_validate(endpoint.extraction_schema)

    return CreateEndpointResponse(
        id=endpoint.id,
        url=endpoint.url,
        description=endpoint.description,
        schema_=schema.to_json_schema(),
    )


@router.get(
    "/{id}",
    response_model=GetEndpointResponse,
    status_code=status.HTTP_200_OK,
)
async def get_endpoint(
    id: UUID,
    session: SessionDep,
    user: CurrentUserDep,
) -> GetEndpointResponse:
    endpoint = await get_endpoint_by_id(session, id, user.id)
    schema = ExtractionSchema.model_validate(endpoint.extraction_schema)

    return GetEndpointResponse(
        id=endpoint.id,
        url=endpoint.url,
        description=endpoint.description,
        schema_=schema.to_json_schema(),
    )


@router.get(
    "/{id}/data",
    status_code=status.HTTP_200_OK,
)
async def get_endpoint_data(
    id: UUID,
    session: SessionDep,
    user: CurrentUserDep,
) -> dict[str, object] | list[dict[str, object]]:
    endpoint = await get_endpoint_by_id(session, id, user.id)
    html = await fetch_clean_html(endpoint.url)
    data = extract_data(
        html, ExtractionSchema.model_validate(endpoint.extraction_schema)
    )
    return data
