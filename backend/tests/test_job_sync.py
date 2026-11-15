from uuid import uuid4

from app.models.job import PrintJob
from app.models.printer import Printer
from app.models.user import User
from app.services import job_sync

PDF = b"%PDF-1.4\n%%EOF\n"


def _seed_job(
    db_session,
    *,
    status: str = "processing",
    cups_job_id: str = "job-1",
) -> PrintJob:
    suffix = uuid4().hex[:8]
    user = User(
        username=f"sync-{suffix}",
        password_hash="x",
        display_name="Sync",
        role="user",
    )
    printer = Printer(
        name=f"Sync-{suffix}",
        slug=f"sync-{suffix}",
        device_uri=f"ipp://192.0.2.30/{suffix}/ipp/print",
    )
    db_session.add_all([user, printer])
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(printer)

    job = PrintJob(
        user_id=user.id,
        printer_id=printer.id,
        filename="x.pdf",
        stored_name="x.pdf",
        options={},
        pages=1,
        copies=1,
        status=status,
        cups_job_id=cups_job_id,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


def test_sync_jobs_marks_processing_and_completed(db_session, monkeypatch):
    job = _seed_job(db_session, status="queued", cups_job_id="job-sync-1")

    monkeypatch.setattr(job_sync.cups, "active_job_ids", lambda: {"job-sync-1"})
    monkeypatch.setattr(job_sync.cups, "completed_job_ids", lambda: set())
    assert job_sync.sync_jobs(db_session) == 1

    db_session.refresh(job)
    assert job.status == "processing"
    assert job.started_at is not None

    monkeypatch.setattr(job_sync.cups, "active_job_ids", lambda: set())
    monkeypatch.setattr(job_sync.cups, "completed_job_ids", lambda: {"job-sync-1"})
    assert job_sync.sync_jobs(db_session) == 1

    db_session.refresh(job)
    assert job.status == "completed"
    assert job.finished_at is not None


def test_refresh_job(db_session, monkeypatch):
    job = _seed_job(db_session, status="processing", cups_job_id="job-sync-2")
    monkeypatch.setattr(job_sync.cups, "job_status", lambda cups_id: "completed")

    refreshed = job_sync.refresh_job(db_session, job)

    assert refreshed.status == "completed"
    assert refreshed.finished_at is not None


def test_get_job_endpoint_refreshes_status(admin_client, user_client, monkeypatch):
    printer = admin_client.post(
        "/api/printers",
        json={
            "name": f"Refresh-{uuid4().hex[:6]}",
            "device_uri": "ipp://192.0.2.31/ipp/print",
        },
    ).json()

    monkeypatch.setattr("app.api.jobs.submit_job", lambda *args, **kwargs: "job-refresh-api")
    job = user_client.post(
        "/api/jobs",
        data={"printer_id": str(printer["id"])},
        files={"file": ("test.pdf", PDF, "application/pdf")},
    ).json()

    monkeypatch.setattr(
        "app.services.job_sync.cups.job_status",
        lambda cups_id: "completed",
    )
    response = user_client.get(f"/api/jobs/{job['id']}")

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
