from uuid import UUID

from app.deps import SessionDep
from app.schemas.endpoint import (
    CreateEndpointRequest,
    CreateEndpointResponse,
    GetEndpointResponse,
)
from app.services.endpoint_service import create_endpoint as create_endpoint_service
from app.services.endpoint_service import get_endpoint_by_id
from fastapi import APIRouter, status

router = APIRouter(prefix="/endpoints", tags=["endpoints"])


@router.post(
    "/",
    response_model=CreateEndpointResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_endpoint(
    request: CreateEndpointRequest,
    session: SessionDep,
) -> CreateEndpointResponse:
    endpoint = await create_endpoint_service(
        session=session,
        url=str(request.url),
        description=request.description,
    )

    return CreateEndpointResponse(
        id=endpoint.id,
        url=endpoint.url,
        description=endpoint.description,
        schema_=endpoint.json_schema,
    )


@router.get(
    "/{id}",
    response_model=GetEndpointResponse,
    status_code=status.HTTP_200_OK,
)
async def get_endpoint(
    id: UUID,
    session: SessionDep,
) -> GetEndpointResponse:
    endpoint = await get_endpoint_by_id(session, id)
    return GetEndpointResponse(
        id=endpoint.id,
        url=endpoint.url,
        description=endpoint.description,
        schema_=endpoint.json_schema,
    )
