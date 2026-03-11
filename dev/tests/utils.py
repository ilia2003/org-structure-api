from typing import Any

from httpx import Response


def assert_api_contains_orm(api_items: list[dict[str, Any]], orm_items: list[Any], fields: tuple[str, ...]) -> None:
    for orm_item in orm_items:
        match = next(
            (item for item in api_items if item.get("id") == str(orm_item.id)),
            None,
        )
        assert match is not None

        for field in fields:
            expected = getattr(orm_item, field)
            if expected is not None:
                expected = str(expected) if field.endswith("_id") else expected
            assert match.get(field) == expected


def assert_http_error(response: Response, status_code: int, detail: str) -> None:
    assert response.status_code == status_code, response.text
    assert response.json().get("detail") == detail
