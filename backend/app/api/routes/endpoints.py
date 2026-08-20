from app.deps import DbSession
from app.schemas.endpoint import CreateEndpointRequest, EndpointResponse
from app.services.endpoint_service import (
    EndpointPersistenceError,
    EndpointSchemaGenerationError,
    SourceFetchError,
)
from app.services.endpoint_service import (
    create_endpoint as create_endpoint_service,
)
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/endpoints", tags=["endpoints"])


@router.post(
    "",
    response_model=EndpointResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_endpoint(
    request: CreateEndpointRequest,
    db: DbSession,
) -> EndpointResponse:
    try:
        endpoint = await create_endpoint_service(
            db=db,
            url=str(request.url),
            description=request.description,
        )
    except SourceFetchError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch the given URL",
        ) from exc
    except EndpointSchemaGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate schema from the given HTML",
        ) from exc
    except EndpointPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist endpoint",
        ) from exc

    return EndpointResponse(
        id=endpoint.id,
        url=request.url,
        description=endpoint.description,
        schema_=endpoint.schema,
    )
