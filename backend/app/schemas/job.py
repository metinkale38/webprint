from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class JobOptions(BaseModel):
    copies: int = 1
    duplex: Literal["one-sided", "two-sided-long-edge", "two-sided-short-edge"] = "one-sided"
    nup: Literal[1, 2, 4, 6, 9, 16] = 1
    color_mode: Literal["color", "monochrome"] = "monochrome"
    page_range: str = ""
    media: str = "A4"


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    printer_id: int
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
