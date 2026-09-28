from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.rate_limit import rate_limit
from app.deps import SessionDep, SessionUserDep
from app.schemas.api_key import (
    ApiKeyResponse,
    CreateApiKeyRequest,
    CreatedApiKeyResponse,
)
from app.services.api_key_service import create_api_key as create_api_key_service
from app.services.api_key_service import delete_api_key as delete_api_key_service
from app.services.api_key_service import get_api_keys_by_user

# Every route takes the browser session only, so a leaked key can neither mint
# more keys nor revoke the owner's others.
router = APIRouter(prefix="/api-keys", tags=["api-keys"])

create_limit = Depends(
    rate_limit("api-key-create", "20/hour", "You've created too many API keys recently")
)


@router.post(
    "",
    response_model=CreatedApiKeyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[create_limit],
)
async def create_api_key(
    request: CreateApiKeyRequest,
    session: SessionDep,
    user: SessionUserDep,
) -> CreatedApiKeyResponse:
    api_key, key = await create_api_key_service(session, user.id, request.name)
    return CreatedApiKeyResponse(
        **ApiKeyResponse.model_validate(api_key).model_dump(), key=key
    )


@router.get("", response_model=list[ApiKeyResponse])
async def get_api_keys(
    session: SessionDep,
    user: SessionUserDep,
) -> list[ApiKeyResponse]:
    api_keys = await get_api_keys_by_user(session, user.id)
    return [ApiKeyResponse.model_validate(api_key) for api_key in api_keys]


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    id: UUID,
    session: SessionDep,
    user: SessionUserDep,
) -> None:
    await delete_api_key_service(session, id, user.id)
