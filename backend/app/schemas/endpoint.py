from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class CreateEndpointRequest(BaseModel):
    url: HttpUrl
    description: str = Field(min_length=1)


class CreateEndpointResponse(BaseModel):
    id: UUID
    url: str
    description: str
    schema_: dict
