from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class CreateEndpointRequest(BaseModel):
    url: HttpUrl
    description: str = Field(min_length=1)


class EndpointResponse(BaseModel):
    id: UUID
    name: str
    url: str
    description: str
    schema_: dict = Field(serialization_alias="schema")
    created_at: datetime
    updated_at: datetime
