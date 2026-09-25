import logging

from bs4 import BeautifulSoup
from soupsieve.util import SelectorSyntaxError

from app.core.exceptions import SchemaValidationError
from app.schemas.extract import ExtractionSchema
from app.services.extraction_service import resolve_element

logger = logging.getLogger(__name__)

# The model returns no fields when it cannot see the requested data, and its
# selectors miss when it guessed at markup, so both usually mean the data is not
# in the fetched HTML, for example because the page renders it with JavaScript.
_DATA_NOT_FOUND = (
    "Could not find the requested data on this page, try describing it differently"
)


def _validate_selector_syntax(label: str, selector: str, issues: list[str]) -> None:
    try:
        BeautifulSoup("", "html.parser").select(selector)
    # soupsieve raises NotImplementedError for pseudo-elements such as ::before.
    except (SelectorSyntaxError, NotImplementedError) as exc:
        issues.append(
            f"{label} selector {selector!r} is not a valid CSS selector: {exc}"
        )


def _validate_structure(schema: ExtractionSchema) -> list[str]:
    issues: list[str] = []
    seen_names: set[str] = set()
    for field in schema.fields:
        if not field.name:
            issues.append("a field has an empty name")
        elif field.name in seen_names:
            issues.append(f"field name {field.name!r} is used more than once")
        else:
            seen_names.add(field.name)

        _validate_selector_syntax(f"field {field.name!r}", field.selector, issues)

    if schema.item_selector is not None:
        _validate_selector_syntax("item_selector", schema.item_selector, issues)

    return issues


def _validate_matches_html(
    html: str, schema: ExtractionSchema, issues: list[str]
) -> None:
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(schema.item_selector) if schema.item_selector else [soup]

    if schema.item_selector and not items:
        issues.append(
            f"item_selector {schema.item_selector!r} does not match any element"
        )
        return

    for field in schema.fields:
        if not any(resolve_element(item, field) is not None for item in items):
            issues.append(
                f"field {field.name!r} selector {field.selector!r} does not match any "
                "element in the fetched page"
            )


def validate_schema(html: str, schema: ExtractionSchema) -> None:
    # The issues describe selectors, which mean nothing to end users, so they
    # are only logged.
    if not schema.fields:
        logger.warning("Generated schema has no fields")
        raise SchemaValidationError(_DATA_NOT_FOUND)

    issues = _validate_structure(schema)
    if issues:
        logger.warning("Generated schema is invalid: %s", "; ".join(issues))
        raise SchemaValidationError("The AI model returned an invalid plan")

    _validate_matches_html(html, schema, issues)
    if issues:
        logger.warning(
            "Generated schema does not match the page: %s", "; ".join(issues)
        )
        raise SchemaValidationError(_DATA_NOT_FOUND)
