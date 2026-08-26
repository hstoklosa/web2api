import re

from bs4 import BeautifulSoup

from app.schemas.extract import ExtractionSchema

_TRUE_TEXTS = {"true", "yes", "y", "in stock", "available", "checked", "1", "on"}
_FALSE_TEXTS = {"false", "no", "n", "out of stock", "unavailable", "unchecked", "0", "off"}
_NUMERIC_STRIP_RE = re.compile(r"[^0-9.\-]")


def _coerce(value: str | None, type_: str) -> object:
    if value is None or type_ == "string":
        return value

    cleaned = value.strip()
    if not cleaned:
        return value

    if type_ == "boolean":
        lowered = cleaned.lower()
        if lowered in _TRUE_TEXTS:
            return True
        if lowered in _FALSE_TEXTS:
            return False
        return value

    if type_ in ("integer", "number"):
        numeric = _NUMERIC_STRIP_RE.sub("", cleaned.replace(",", ""))
        if not numeric or numeric in ("-", "."):
            return value
        try:
            if type_ == "integer":
                return int(float(numeric))
            return float(numeric)
        except ValueError:
            return value

    return value


def extract_data(
    html: str, schema: ExtractionSchema
) -> dict[str, object] | list[dict[str, object]]:
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(schema.item_selector) if schema.item_selector else [soup]
    data = []

    for item in items:
        row = {}
        for field in schema.fields:
            if field.relative_to == "next_sibling":
                context = item.find_next_sibling()
            else:
                context = item

            element = (
                context.select_one(field.selector) if context is not None else None
            )

            if field.source.kind == "text":
                text_content = (
                    element.get_text(" ", strip=True) if element is not None else None
                )
                row[field.name] = _coerce(text_content, field.type)
            else:
                attribute_content = (
                    element.attrs.get(field.source.name)
                    if element is not None
                    else None
                )
                if isinstance(attribute_content, list):
                    attribute_content = " ".join(attribute_content)
                row[field.name] = _coerce(attribute_content, field.type)

        data.append(row)

    if not schema.item_selector:
        return data[0]

    return data
