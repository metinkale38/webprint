import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.user import User
from ..schemas.stats import StatsOverview, StatsRow
from ..services.stats import by_printer, by_user, overview
from .deps import require_admin

router = APIRouter()


def _validate_period(start: date | None, end: date | None) -> None:
    if start is not None and end is not None and start > end:
        raise HTTPException(status_code=422, detail="Startdatum liegt nach dem Enddatum")


@router.get("/overview", response_model=StatsOverview)
def get_overview(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> StatsOverview:
    _validate_period(start, end)
    return StatsOverview(**overview(db, start, end))


@router.get("/users", response_model=list[StatsRow])
def stats_users(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> list[StatsRow]:
    _validate_period(start, end)
    return by_user(db, start, end)


@router.get("/printers", response_model=list[StatsRow])
def stats_printers(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> list[StatsRow]:
    _validate_period(start, end)
    return by_printer(db, start, end)


@router.get("/export")
def export_csv(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> Response:
    _validate_period(start, end)
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(["Nutzer", "Auftraege", "Seiten", "Kopien"])
    for row in by_user(db, start, end):
        writer.writerow([row.label, row.jobs, row.pages, row.copies])
    return Response(
        content="\ufeff" + buffer.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="printtool-statistik.csv"'},
    )
