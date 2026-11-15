import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models.job import PrintJob
from . import cups

logger = logging.getLogger(__name__)

_ACTIVE_STATUSES = ("queued", "processing")


def sync_jobs(db: Session) -> int:
    jobs = db.query(PrintJob).filter(PrintJob.status.in_(_ACTIVE_STATUSES)).all()
    if not jobs:
        return 0

    active = cups.active_job_ids()
    completed = cups.completed_job_ids()
    now = datetime.now(timezone.utc)
    changed = 0

    for job in jobs:
        if not job.cups_job_id:
            continue
        if job.cups_job_id in active:
            if job.status != "processing":
                job.status = "processing"
                changed += 1
            if job.started_at is None:
                job.started_at = now
        elif job.cups_job_id in completed:
            job.status = "completed"
            job.finished_at = now
            changed += 1

    db.commit()
    return changed


def refresh_job(db: Session, job: PrintJob) -> PrintJob:
    if not job.cups_job_id or job.status not in _ACTIVE_STATUSES:
        return job

    status = cups.job_status(job.cups_job_id)
    now = datetime.now(timezone.utc)

    if status == "processing":
        if job.status != "processing":
            job.status = "processing"
        if job.started_at is None:
            job.started_at = now
        db.commit()
        db.refresh(job)
    elif status == "completed":
        job.status = "completed"
        job.finished_at = now
        db.commit()
        db.refresh(job)
    return job


async def job_sync_loop(interval: int) -> None:
    from ..db import SessionLocal

    while True:
        try:
            with SessionLocal() as db:
                changed = sync_jobs(db)
                if changed:
                    logger.info("Job-Sync: %d Status aktualisiert", changed)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Job-Sync fehlgeschlagen")
        await asyncio.sleep(max(5, interval))
