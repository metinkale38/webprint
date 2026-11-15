from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

PDF = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n"


def _create_printer(admin_client):
    payload = {
        "name": f"Jobdrucker-{uuid4().hex[:6]}",
        "device_uri": "ipp://192.0.2.11/ipp/print",
    }
    response = admin_client.post("/api/printers", json=payload)
    assert response.status_code == 201
    return response.json()


def test_job_upload_and_cancel(admin_client, user_client, monkeypatch):
    printer = _create_printer(admin_client)
    monkeypatch.setattr("app.api.jobs.submit_job", lambda *args, **kwargs: "testdrucker-7")

    response = user_client.post(
        "/api/jobs",
        data={
            "printer_id": str(printer["id"]),
            "copies": "2",
            "color_mode": "color",
            "duplex": "two-sided-long-edge",
            "nup": "2",
            "page_range": "1-2",
            "media": "A4",
        },
        files={"file": ("test.pdf", PDF, "application/pdf")},
    )
    assert response.status_code == 201
    job = response.json()
    assert job["cups_job_id"] == "testdrucker-7"
    assert job["status"] == "processing"
    assert job["pages"] == 1
    assert job["copies"] == 2
    assert job["color_mode"] == "color"

    me = user_client.get("/api/auth/me").json()
    assert job["user_name"] == me["username"]
    assert job["printer_name"] == printer["name"]

    listing = user_client.get("/api/jobs")
    assert listing.status_code == 200
    assert any(
        item["id"] == job["id"] and item["user_name"] == me["username"]
        for item in listing.json()
    )

    all_jobs = admin_client.get("/api/jobs", params={"all_jobs": True})
    assert all_jobs.status_code == 200
    assert any(item["id"] == job["id"] for item in all_jobs.json())

    cancelled = user_client.post(f"/api/jobs/{job['id']}/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"


def test_job_rejects_invalid_file(admin_client, user_client):
    printer = _create_printer(admin_client)
    response = user_client.post(
        "/api/jobs",
        data={"printer_id": str(printer["id"])},
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 415


def test_job_rejects_invalid_page_range(admin_client, user_client):
    printer = _create_printer(admin_client)
    response = user_client.post(
        "/api/jobs",
        data={"printer_id": str(printer["id"]), "page_range": "1-abc"},
        files={"file": ("test.pdf", PDF, "application/pdf")},
    )
    assert response.status_code == 422


def test_job_access_control(admin_client, user_client, monkeypatch):
    printer = _create_printer(admin_client)
    monkeypatch.setattr("app.api.jobs.submit_job", lambda *args, **kwargs: None)

    job = user_client.post(
        "/api/jobs",
        data={"printer_id": str(printer["id"])},
        files={"file": ("test.pdf", PDF, "application/pdf")},
    ).json()

    other_name = f"other-{uuid4().hex[:6]}"
    created = admin_client.post(
        "/api/users",
        json={"username": other_name, "password": "other-password", "role": "user"},
    )
    assert created.status_code == 201

    with TestClient(app) as other:
        assert (
            other.post(
                "/api/auth/login",
                json={"username": other_name, "password": "other-password"},
            ).status_code
            == 200
        )
        assert other.get(f"/api/jobs/{job['id']}").status_code == 403
        assert other.post(f"/api/jobs/{job['id']}/cancel").status_code == 403
