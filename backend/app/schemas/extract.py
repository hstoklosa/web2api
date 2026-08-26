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
    type: Literal["string", "integer", "number", "boolean"] = "string"


class ExtractionSchema(BaseModel):
    item_selector: str | None = (
        None  # use to handle lists/repeated items relative to some item
    )
    fields: list[ExtractionSchemaField]

    def to_json_schema(self) -> dict:
        properties = {field.name: {"type": field.type} for field in self.fields}
        object_schema = {"type": "object", "properties": properties}

        if self.item_selector is not None:
            return {"type": "array", "items": object_schema}
        return object_schema
