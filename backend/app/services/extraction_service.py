from bs4 import BeautifulSoup

from app.schemas.extract import ExtractionSchema


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
                row[field.name] = text_content
            else:
                attribute_content = (
                    element.attrs.get(field.source.name)
                    if element is not None
                    else None
                )
                row[field.name] = attribute_content

        data.append(row)

    if not schema.item_selector:
        return data[0]

    return data
