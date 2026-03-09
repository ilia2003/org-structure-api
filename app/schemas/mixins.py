from datetime import datetime

from pydantic import BaseModel


class CreateUpdateAt(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None

class StripTextFieldsMixin(BaseModel):
    @classmethod
    def strip_text_fields(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Field must not be empty")

        return value
