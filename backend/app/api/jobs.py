from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models.job import PrintJob
from ..models.printer import Printer
from ..models.user import User
from ..schemas.job import JobOptions, JobOut
from ..services.cups import cancel_job, submit_job
from ..services.print_job import build_lp_options
from .deps import get_current_user

router = APIRouter()

_MAGIC_EXTENSIONS = (
    (b"%PDF", ".pdf"),
    (b"\xff\xd8\xff", ".jpg"),
    (b"\x89PNG\r\n\x1a\n", ".png"),
)


def _detect_extension(content: bytes) -> str | None:
    for magic, extension in _MAGIC_EXTENSIONS:
        if content.startswith(magic):
            return extension
    return None


def _count_pages(path: Path, extension: str) -> int:
    if extension != ".pdf":
        return 1
    try:
        from pypdf import PdfReader

        with path.open("rb") as handle:
            return max(1, len(PdfReader(handle).pages))
    except Exception:
        return 1


@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
async def create_job(
    file: UploadFile = File(...),
    printer_id: int = Form(...),
    copies: int = Form(1),
    duplex: str = Form("one-sided"),
    nup: int = Form(1),
    color_mode: str = Form("monochrome"),
    page_range: str = Form(""),
    media: str = Form("A4"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PrintJob:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Leere Datei")
    if len(content) > settings.upload_max_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Datei zu groß")
    extension = _detect_extension(content)
    if extension is None:
        raise HTTPException(status_code=415, detail="Nur PDF, JPEG und PNG erlaubt")

    printer = db.get(Printer, printer_id)
    if printer is None or not printer.enabled:
        raise HTTPException(status_code=404, detail="Drucker nicht verfügbar")

    try:
        options = JobOptions(
            copies=copies,
            duplex=duplex,
            nup=nup,
            color_mode=color_mode,
            page_range=page_range,
            media=media,
        )
    except ValidationError as exc:
        details = [
            {"loc": list(error["loc"]), "msg": error["msg"], "type": error["type"]}
            for error in exc.errors()
        ]
        raise HTTPException(status_code=422, detail=details) from exc

    stored_name = f"{uuid4().hex}{extension}"
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    stored_path = settings.upload_dir / stored_name
    stored_path.write_bytes(content)
    pages = _count_pages(stored_path, extension)

    job = PrintJob(
        user_id=user.id,
        printer_id=printer.id,
        filename=file.filename or f"upload{extension}",
        stored_name=stored_name,
        options=options.model_dump(),
        pages=pages,
        copies=options.copies,
        color_mode=options.color_mode,
        duplex=options.duplex,
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    cups_job_id = submit_job(printer.slug, stored_path, build_lp_options(options, printer))
    if cups_job_id:
        job.cups_job_id = cups_job_id
        job.status = "processing"
        job.started_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)
    return job


@router.get("", response_model=list[JobOut])
def list_jobs(
    all_jobs: bool = Query(False),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[PrintJob]:
    query = db.query(PrintJob).order_by(PrintJob.created_at.desc())
    if user.role != "admin" or not all_jobs:
        query = query.filter(PrintJob.user_id == user.id)
    return query.limit(200).all()


@router.get("/{job_id}", response_model=JobOut)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PrintJob:
    job = db.get(PrintJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Auftrag nicht gefunden")
    if user.role != "admin" and job.user_id != user.id:
        raise HTTPException(status_code=403, detail="Kein Zugriff")
    return job


@router.post("/{job_id}/cancel", response_model=JobOut)
def cancel(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PrintJob:
    job = db.get(PrintJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Auftrag nicht gefunden")
    if user.role != "admin" and job.user_id != user.id:
        raise HTTPException(status_code=403, detail="Kein Zugriff")
    if job.cups_job_id:
        cancel_job(job.cups_job_id)
    job.status = "cancelled"
    job.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    return job
