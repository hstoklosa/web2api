from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, StringConstraints, UrlConstraints

EndpointUrl = Annotated[HttpUrl, UrlConstraints(max_length=2048)]
EndpointDescription = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)
]


class CreateEndpointRequest(BaseModel):
    url: EndpointUrl
    description: EndpointDescription


class EndpointResponse(BaseModel):
    id: UUID
    name: str
    url: str
    description: str
    schema_: dict = Field(serialization_alias="schema")
    created_at: datetime
    updated_at: datetime
