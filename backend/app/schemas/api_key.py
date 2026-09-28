from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints

ApiKeyName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]


class CreateApiKeyRequest(BaseModel):
    name: ApiKeyName


class ApiKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    prefix: str
    created_at: datetime
    last_used_at: datetime | None


class CreatedApiKeyResponse(ApiKeyResponse):
    # The only time the key leaves the server, since it is stored as a hash.
    key: str
