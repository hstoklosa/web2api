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
    # html = await fetch_clean_html(str(request.url))
    # schema = await generate_schema(html, request.description)

    # schema_json = schema.model_dump(mode="json")
    # schema_fields = schema_json.get("fields", [])

    # print(schema_json)

    # for field in schema_fields:
    #     selector = field.get("css_selector", "")
    #     if selector:
    #         data = extract_text_with_selector(html, selector)
    #         print(data)

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

    # return EndpointResponse(
    #     id=endpoint.id,
    #     url=request.url,
    #     description=endpoint.description,
    #     schema_=endpoint.schema,
    # )
