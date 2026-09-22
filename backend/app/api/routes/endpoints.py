from uuid import UUID

from app.deps import CurrentUserDep, SessionDep
from app.models import Endpoint
from app.schemas.endpoint import CreateEndpointRequest, EndpointResponse
from app.schemas.extract import ExtractionSchema
from app.services.endpoint_service import create_endpoint as create_endpoint_service
from app.services.endpoint_service import get_endpoint_by_id, get_endpoints_by_user
from app.services.extraction_service import extract_data
from app.services.scrape_service import fetch_clean_html
from fastapi import APIRouter, status

router = APIRouter(prefix="/endpoints", tags=["endpoints"])


def to_response(endpoint: Endpoint) -> EndpointResponse:
    extraction = ExtractionSchema.model_validate(endpoint.extraction_schema)

    return EndpointResponse(
        id=endpoint.id,
        name=endpoint.name,
        url=endpoint.url,
        description=endpoint.description,
        schema_=extraction.to_json_schema(),
    )


@router.post(
    "",
    response_model=EndpointResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_endpoint(
    request: CreateEndpointRequest,
    session: SessionDep,
    user: CurrentUserDep,
) -> EndpointResponse:
    endpoint = await create_endpoint_service(
        session=session,
        user_id=user.id,
        url=str(request.url),
        prompt=request.description,
    )
    return to_response(endpoint)


@router.get(
    "",
    response_model=list[EndpointResponse],
    status_code=status.HTTP_200_OK,
)
async def get_endpoints(
    session: SessionDep,
    user: CurrentUserDep,
) -> list[EndpointResponse]:
    endpoints = await get_endpoints_by_user(session, user.id)
    return [to_response(endpoint) for endpoint in endpoints]


@router.get(
    "/{id}",
    response_model=EndpointResponse,
    status_code=status.HTTP_200_OK,
)
async def get_endpoint(
    id: UUID,
    session: SessionDep,
    user: CurrentUserDep,
) -> EndpointResponse:
    endpoint = await get_endpoint_by_id(session, id, user.id)
    return to_response(endpoint)


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
