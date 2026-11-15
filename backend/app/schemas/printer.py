from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

_DEVICE_URI_PATTERN = r"^(ipp|ipps|lpd|socket|dnssd)://|^cups-pdf:/"
_SLUG_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._-]*$"

Protocol = Literal["ipp", "ipps", "lpd", "socket", "dnssd", "cups-pdf"]


class PrinterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    device_uri: str
    protocol: str
    model: str
    location: str
    driver_mode: str
    auto_discovered: bool
    enabled: bool
    status: str
    capabilities: dict
    last_seen: datetime | None = None


class PrinterCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    slug: str | None = Field(default=None, min_length=1, max_length=127, pattern=_SLUG_PATTERN)
    device_uri: str = Field(min_length=1, max_length=512, pattern=_DEVICE_URI_PATTERN)
    protocol: Protocol = "ipp"
    model: str = Field(default="", max_length=128)
    location: str = Field(default="", max_length=128)
    driver_mode: str = Field(default="everywhere", min_length=1, max_length=64)
    auto_discovered: bool = False
    enabled: bool = True


class PrinterUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    device_uri: str | None = Field(
        default=None, min_length=1, max_length=512, pattern=_DEVICE_URI_PATTERN
    )
    protocol: Protocol | None = None
    model: str | None = Field(default=None, max_length=128)
    location: str | None = Field(default=None, max_length=128)
    driver_mode: str | None = Field(default=None, min_length=1, max_length=64)
    enabled: bool | None = None
