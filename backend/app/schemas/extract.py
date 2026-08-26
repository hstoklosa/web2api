from typing import Literal

from pydantic import BaseModel


class TextSource(BaseModel):
    kind: Literal["text"] = "text"


class AttributeSource(BaseModel):
    kind: Literal["attribute"] = "attribute"
    name: str


class ExtractionSchemaField(BaseModel):
    name: str
    selector: str
    relative_to: Literal["item", "next_sibling"] = "item"
    source: TextSource | AttributeSource = TextSource()


class ExtractionSchema(BaseModel):
    item_selector: str | None = (
        None  # use to handle lists/repeated items relative to some item
    )
    fields: list[ExtractionSchemaField]
