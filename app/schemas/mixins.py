from datetime import datetime
from typing import Any, get_args, get_origin

from pydantic import BaseModel, model_validator


class CreateUpdateAt(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None


class StripTextFieldsMixin(BaseModel):
    @staticmethod
    def _supports_text(annotation: Any) -> bool:
        if annotation is str:
            return True

        origin = get_origin(annotation)
        if origin is None:
            return False

        return str in get_args(annotation)

    @model_validator(mode="before")
    @classmethod
    def strip_text_fields(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values

        normalized_values = values.copy()
        for field_name, field_info in cls.model_fields.items():
            value = normalized_values.get(field_name)
            if value is None or not cls._supports_text(field_info.annotation):
                continue

            if not isinstance(value, str):
                continue

            stripped = value.strip()
            if not stripped:
                raise ValueError(f"{field_name} must not be empty")
            normalized_values[field_name] = stripped
        return normalized_values
