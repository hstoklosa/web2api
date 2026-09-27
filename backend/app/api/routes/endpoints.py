from uuid import UUID

from app.core.rate_limit import rate_limit
from app.deps import CurrentUserDep, SessionDep
from app.models import Endpoint
from app.schemas.endpoint import CreateEndpointRequest, EndpointResponse
from app.schemas.extract import ExtractionSchema
from app.services.endpoint_service import create_endpoint as create_endpoint_service
from app.services.endpoint_service import delete_endpoint as delete_endpoint_service
from app.services.endpoint_service import get_endpoint_by_id, get_endpoints_by_user
from app.services.extraction_service import extract_data
from app.services.scrape_service import fetch_clean_html
from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/endpoints", tags=["endpoints"])

# Creating an endpoint fetches a page and calls the AI model, and reading its
# data fetches the page again, so those get their own, tighter budgets.
create_limit = Depends(
    rate_limit(
        "endpoint-create", "10/hour", "You've created too many endpoints recently"
    )
)
data_limit = Depends(
    rate_limit(
        "endpoint-data", "60/minute", "You've requested endpoint data too often"
    )
)
read_limit = Depends(
    rate_limit("endpoint-read", "120/minute", "You've made too many requests")
)


def to_response(endpoint: Endpoint) -> EndpointResponse:
    extraction = ExtractionSchema.model_validate(endpoint.extraction_schema)

    return EndpointResponse(
        id=endpoint.id,
        name=endpoint.name,
        url=endpoint.url,
        description=endpoint.description,
        schema_=extraction.to_json_schema(),
        created_at=endpoint.created_at,
        updated_at=endpoint.updated_at,
    )


@router.post(
    "",
    response_model=EndpointResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[create_limit],
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
    dependencies=[read_limit],
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
    dependencies=[read_limit],
)
async def get_endpoint(
    id: UUID,
    session: SessionDep,
    user: CurrentUserDep,
) -> EndpointResponse:
    endpoint = await get_endpoint_by_id(session, id, user.id)
    return to_response(endpoint)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[read_limit],
)
async def delete_endpoint(
    id: UUID,
    session: SessionDep,
    user: CurrentUserDep,
) -> None:
    await delete_endpoint_service(session, id, user.id)


@router.get(
    "/{id}/data",
    status_code=status.HTTP_200_OK,
    dependencies=[data_limit],
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
