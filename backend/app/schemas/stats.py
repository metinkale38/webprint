from pydantic import BaseModel


class StatsRow(BaseModel):
    label: str
    jobs: int
    pages: int
    copies: int


class StatsOverview(BaseModel):
    jobs: int
    pages: int
    copies: int
    color_jobs: int
    monochrome_jobs: int
    printers: int
    users: int
