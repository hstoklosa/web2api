from app.deps import DbSession
from app.schemas.endpoint import CreateEndpointRequest, CreateEndpointResponse
from app.services.endpoint_service import create_endpoint as create_endpoint_service
from fastapi import APIRouter, status

router = APIRouter(prefix="/endpoints", tags=["endpoints"])


@router.post(
    "/",
    response_model=CreateEndpointResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_endpoint(
    request: CreateEndpointRequest,
    session: DbSession,
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
