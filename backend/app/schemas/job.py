import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

_PAGE_RANGE_RE = re.compile(r"^(\d+(-\d*)?)(,\s*\d+(-\d*)?)*$")


class JobOptions(BaseModel):
    copies: int = Field(default=1, ge=1, le=99)
    duplex: Literal["one-sided", "two-sided-long-edge", "two-sided-short-edge"] = "one-sided"
    nup: Literal[1, 2, 4, 6, 9, 16] = 1
    color_mode: Literal["color", "monochrome"] = "monochrome"
    page_range: str = ""
    media: str = Field(default="A4", pattern=r"^[A-Za-z0-9._-]+$")

    @field_validator("page_range")
    @classmethod
    def validate_page_range(cls, value: str) -> str:
        value = value.strip()
        if value and not _PAGE_RANGE_RE.match(value):
            raise ValueError("Seitenbereich muss z. B. '1-5,8' sein")
        return value


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    printer_id: int
    user_name: str = ""
    printer_name: str = ""
    filename: str
    options: dict
    pages: int
    copies: int
    color_mode: str
    duplex: str
    status: str
    cups_job_id: str | None = None
    error: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
