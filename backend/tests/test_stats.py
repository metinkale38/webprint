from datetime import date, timedelta
from uuid import uuid4

from tests.test_jobs import PDF


def _create_printer(admin_client):
    response = admin_client.post(
        "/api/printers",
        json={
            "name": f"Statdrucker-{uuid4().hex[:6]}",
            "device_uri": "ipp://192.0.2.12/ipp/print",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_stats_and_export(admin_client, user_client, monkeypatch):
    printer = _create_printer(admin_client)
    monkeypatch.setattr("app.api.jobs.submit_job", lambda *args, **kwargs: "test-1")

    response = user_client.post(
        "/api/jobs",
        data={"printer_id": str(printer["id"]), "copies": "3"},
        files={"file": ("test.pdf", PDF, "application/pdf")},
    )
    assert response.status_code == 201

    overview = admin_client.get("/api/stats/overview")
    assert overview.status_code == 200
    data = overview.json()
    assert data["jobs"] >= 1
    assert data["pages"] >= 3
    assert data["copies"] >= 3
    assert data["printers"] >= 1

    users = admin_client.get("/api/stats/users")
    assert users.status_code == 200
    assert any(row["pages"] >= 3 for row in users.json())

    printers = admin_client.get("/api/stats/printers")
    assert printers.status_code == 200
    assert any(row["jobs"] >= 1 for row in printers.json())

    export = admin_client.get("/api/stats/export")
    assert export.status_code == 200
    assert export.headers["content-type"].startswith("text/csv")
    assert "Nutzer" in export.text

    today = date.today()
    fenced = admin_client.get(
        "/api/stats/overview",
        params={
            "start": (today - timedelta(days=1)).isoformat(),
            "end": (today + timedelta(days=1)).isoformat(),
        },
    )
    assert fenced.status_code == 200
    assert fenced.json()["jobs"] >= 1

    future = admin_client.get(
        "/api/stats/overview",
        params={"start": (today + timedelta(days=2)).isoformat()},
    )
    assert future.status_code == 200
    assert future.json()["jobs"] == 0

    invalid = admin_client.get(
        "/api/stats/overview",
        params={
            "start": (today + timedelta(days=1)).isoformat(),
            "end": today.isoformat(),
        },
    )
    assert invalid.status_code == 422
