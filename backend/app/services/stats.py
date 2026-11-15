from datetime import date, datetime, time

from sqlalchemy import func
from sqlalchemy.orm import Query, Session

from ..models.job import PrintJob
from ..models.printer import Printer
from ..models.user import User
from ..schemas.stats import StatsRow

_PAGES = func.coalesce(func.sum(PrintJob.pages * PrintJob.copies), 0)
_COPIES = func.coalesce(func.sum(PrintJob.copies), 0)


def _period_filters(start: date | None, end: date | None) -> list:
    filters = []
    if start is not None:
        filters.append(PrintJob.created_at >= datetime.combine(start, time.min))
    if end is not None:
        filters.append(PrintJob.created_at <= datetime.combine(end, time.max))
    return filters


def _apply(query: Query, filters: list) -> Query:
    return query.filter(*filters) if filters else query


def overview(db: Session, start: date | None = None, end: date | None = None) -> dict:
    filters = _period_filters(start, end)
    return {
        "jobs": int(_apply(db.query(func.count(PrintJob.id)), filters).scalar() or 0),
        "pages": int(_apply(db.query(_PAGES), filters).scalar() or 0),
        "copies": int(_apply(db.query(_COPIES), filters).scalar() or 0),
        "color_jobs": int(
            _apply(
                db.query(func.count(PrintJob.id)).filter(PrintJob.color_mode == "color"),
                filters,
            ).scalar()
            or 0
        ),
        "monochrome_jobs": int(
            _apply(
                db.query(func.count(PrintJob.id)).filter(PrintJob.color_mode == "monochrome"),
                filters,
            ).scalar()
            or 0
        ),
        "printers": int(db.query(func.count(Printer.id)).scalar() or 0),
        "users": int(db.query(func.count(User.id)).scalar() or 0),
    }


def by_user(
    db: Session, start: date | None = None, end: date | None = None
) -> list[StatsRow]:
    filters = _period_filters(start, end)
    query = (
        db.query(
            User.username.label("label"),
            func.count(PrintJob.id).label("jobs"),
            _PAGES.label("pages"),
            _COPIES.label("copies"),
        )
        .join(PrintJob, PrintJob.user_id == User.id)
        .group_by(User.id, User.username)
        .order_by(User.username)
    )
    rows = _apply(query, filters).all()
    return [
        StatsRow(label=row.label, jobs=int(row.jobs), pages=int(row.pages), copies=int(row.copies))
        for row in rows
    ]


def by_printer(
    db: Session, start: date | None = None, end: date | None = None
) -> list[StatsRow]:
    filters = _period_filters(start, end)
    query = (
        db.query(
            Printer.name.label("label"),
            func.count(PrintJob.id).label("jobs"),
            _PAGES.label("pages"),
            _COPIES.label("copies"),
        )
        .join(PrintJob, PrintJob.printer_id == Printer.id)
        .group_by(Printer.id, Printer.name)
        .order_by(Printer.name)
    )
    rows = _apply(query, filters).all()
    return [
        StatsRow(label=row.label, jobs=int(row.jobs), pages=int(row.pages), copies=int(row.copies))
        for row in rows
    ]
