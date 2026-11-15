import csv
import io

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.user import User
from ..schemas.stats import StatsOverview, StatsRow
from ..services.stats import overview, by_printer, by_user
from .deps import require_admin

router = APIRouter()


@router.get("/overview", response_model=StatsOverview)
def get_overview(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> StatsOverview:
    return StatsOverview(**overview(db))


@router.get("/users", response_model=list[StatsRow])
def stats_users(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> list[StatsRow]:
    return by_user(db)


@router.get("/printers", response_model=list[StatsRow])
def stats_printers(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> list[StatsRow]:
    return by_printer(db)


@router.get("/export")
def export_csv(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> Response:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(["Nutzer", "Auftraege", "Seiten", "Kopien"])
    for row in by_user(db):
        writer.writerow([row.label, row.jobs, row.pages, row.copies])
    return Response(
        content="\ufeff" + buffer.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="printtool-statistik.csv"'},
    )
