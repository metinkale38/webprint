from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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
    slug: str | None = None
    device_uri: str = Field(min_length=1, max_length=512)
    protocol: str = "ipp"
    model: str = ""
    location: str = ""
    driver_mode: str = "everywhere"
    auto_discovered: bool = False
    enabled: bool = True


class PrinterUpdate(BaseModel):
    name: str | None = None
    device_uri: str | None = None
    protocol: str | None = None
    model: str | None = None
    location: str | None = None
    driver_mode: str | None = None
    enabled: bool | None = None
