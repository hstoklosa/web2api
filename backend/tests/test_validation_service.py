import pytest

from app.core.exceptions import SchemaValidationError
from app.schemas.extract import ExtractionSchema
from app.services.validation_service import validate_schema

HTML = "<ul><li><a href='/a'>A</a></li><li><a href='/b'>B</a></li></ul>"


def schema(fields: list[dict], item_selector: str | None = None) -> ExtractionSchema:
    return ExtractionSchema.model_validate(
        {"item_selector": item_selector, "fields": fields}
    )


def test_accepts_matching_schema() -> None:
    validate_schema(HTML, schema([{"name": "title", "selector": "a"}], "li"))


@pytest.mark.parametrize(
    ("extraction", "message"),
    [
        (schema([]), "Could not find the requested data"),
        (schema([{"name": "price", "selector": ".price"}]), "Could not find"),
        (schema([{"name": "title", "selector": "a"}], "tr"), "Could not find"),
        (schema([{"name": "title", "selector": "a["}]), "invalid plan"),
        (schema([{"name": "title", "selector": "a::before"}]), "invalid plan"),
        (
            schema(
                [{"name": "title", "selector": "a"}, {"name": "title", "selector": "a"}]
            ),
            "invalid plan",
        ),
    ],
)
def test_rejects_unusable_schema(extraction: ExtractionSchema, message: str) -> None:
    with pytest.raises(SchemaValidationError, match=message):
        validate_schema(HTML, extraction)
