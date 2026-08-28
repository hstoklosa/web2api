from bs4 import BeautifulSoup
from soupsieve.util import SelectorSyntaxError

from app.core.exceptions import SchemaValidationError
from app.schemas.extract import ExtractionSchema
from app.services.extraction_service import resolve_element


def _validate_selector_syntax(label: str, selector: str, issues: list[str]) -> None:
    try:
        BeautifulSoup("", "html.parser").select(selector)
    except SelectorSyntaxError as exc:
        issues.append(f"{label} selector {selector!r} is not a valid CSS selector: {exc}")


def _validate_structure(schema: ExtractionSchema) -> list[str]:
    issues: list[str] = []

    if not schema.fields:
        issues.append("schema has no fields")
        return issues

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


def _validate_matches_html(html: str, schema: ExtractionSchema, issues: list[str]) -> None:
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(schema.item_selector) if schema.item_selector else [soup]

    if schema.item_selector and not items:
        issues.append(f"item_selector {schema.item_selector!r} does not match any element")
        return

    for field in schema.fields:
        if not any(resolve_element(item, field) is not None for item in items):
            issues.append(
                f"field {field.name!r} selector {field.selector!r} does not match any "
                "element in the fetched page"
            )


def validate_schema(html: str, schema: ExtractionSchema) -> None:
    issues = _validate_structure(schema)

    if not issues:
        _validate_matches_html(html, schema, issues)

    if issues:
        raise SchemaValidationError("; ".join(issues))
