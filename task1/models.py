from typing import Optional

from sqlmodel import SQLModel, Field
from pydantic import field_validator


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    title: str
    description: str
    category: str
    location: str
    reported_by: str
    status: str

    @field_validator("title", "description", "category", "location", "reported_by")
    @classmethod
    def validate_text(cls, value):
        if not value.strip():
            raise ValueError("Field must not be empty")
        return value.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        if len(value.strip()) < 5:
            raise ValueError("Description must contain meaningful text")
        return value.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        value = value.strip().capitalize()

        if value not in ["Lost", "Found", "Returned"]:
            raise ValueError("Status must be Lost, Found, or Returned")

        return value