from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.job import PrintJob
from ..models.printer import Printer
from ..models.user import User
from ..schemas.stats import StatsRow

_PAGES = func.coalesce(func.sum(PrintJob.pages * PrintJob.copies), 0)
_COPIES = func.coalesce(func.sum(PrintJob.copies), 0)


def overview(db: Session) -> dict:
    return {
        "jobs": int(db.query(func.count(PrintJob.id)).scalar() or 0),
        "pages": int(db.query(_PAGES).scalar() or 0),
        "copies": int(db.query(_COPIES).scalar() or 0),
        "color_jobs": int(
            db.query(func.count(PrintJob.id)).filter(PrintJob.color_mode == "color").scalar() or 0
        ),
        "monochrome_jobs": int(
            db.query(func.count(PrintJob.id))
            .filter(PrintJob.color_mode == "monochrome")
            .scalar()
            or 0
        ),
        "printers": int(db.query(func.count(Printer.id)).scalar() or 0),
        "users": int(db.query(func.count(User.id)).scalar() or 0),
    }


def by_user(db: Session) -> list[StatsRow]:
    rows = (
        db.query(
            User.username.label("label"),
            func.count(PrintJob.id).label("jobs"),
            _PAGES.label("pages"),
            _COPIES.label("copies"),
        )
        .join(PrintJob, PrintJob.user_id == User.id)
        .group_by(User.id, User.username)
        .order_by(User.username)
        .all()
    )
    return [
        StatsRow(label=row.label, jobs=int(row.jobs), pages=int(row.pages), copies=int(row.copies))
        for row in rows
    ]


def by_printer(db: Session) -> list[StatsRow]:
    rows = (
        db.query(
            Printer.name.label("label"),
            func.count(PrintJob.id).label("jobs"),
            _PAGES.label("pages"),
            _COPIES.label("copies"),
        )
        .join(PrintJob, PrintJob.printer_id == Printer.id)
        .group_by(Printer.id, Printer.name)
        .order_by(Printer.name)
        .all()
    )
    return [
        StatsRow(label=row.label, jobs=int(row.jobs), pages=int(row.pages), copies=int(row.copies))
        for row in rows
    ]
