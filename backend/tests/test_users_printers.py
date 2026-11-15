from uuid import uuid4


def test_user_crud(admin_client):
    username = f"crud-{uuid4().hex[:6]}"
    created = admin_client.post(
        "/api/users",
        json={
            "username": username,
            "password": "password-123",
            "display_name": "Testnutzer",
        },
    )
    assert created.status_code == 201
    user_id = created.json()["id"]

    listing = admin_client.get("/api/users")
    assert listing.status_code == 200
    assert any(user["username"] == username for user in listing.json())

    patched = admin_client.patch(
        f"/api/users/{user_id}",
        json={"display_name": "Neu", "active": False},
    )
    assert patched.status_code == 200
    assert patched.json()["display_name"] == "Neu"
    assert patched.json()["active"] is False

    assert admin_client.delete(f"/api/users/{user_id}").status_code == 204


def test_create_printer_and_duplicate(admin_client):
    payload = {
        "name": f"Testdrucker-{uuid4().hex[:6]}",
        "device_uri": "ipp://192.0.2.10/ipp/print",
        "location": "EG",
        "model": "Test",
    }
    created = admin_client.post("/api/printers", json=payload)
    assert created.status_code == 201
    printer = created.json()
    assert printer["slug"]

    duplicate = admin_client.post("/api/printers", json=payload)
    assert duplicate.status_code == 409

    patched = admin_client.patch(
        f"/api/printers/{printer['id']}",
        json={"location": "1. OG"},
    )
    assert patched.status_code == 200
    assert patched.json()["location"] == "1. OG"

    capabilities = admin_client.get(f"/api/printers/{printer['id']}/capabilities")
    assert capabilities.status_code == 200
    assert capabilities.json() == {}

    assert admin_client.delete(f"/api/printers/{printer['id']}").status_code == 204


def test_invalid_printer_payload(admin_client):
    invalid_uri = admin_client.post(
        "/api/printers",
        json={"name": "X", "device_uri": "smb://server/printer"},
    )
    assert invalid_uri.status_code == 422

    invalid_slug = admin_client.post(
        "/api/printers",
        json={
            "name": "X",
            "slug": "bad slug",
            "device_uri": "ipp://192.0.2.10/ipp/print",
        },
    )
    assert invalid_slug.status_code == 422


def test_printer_queue_lifecycle(admin_client, monkeypatch):
    calls: list[tuple] = []

    def fake_add(name, device_uri, driver_mode):
        calls.append(("add", name, device_uri, driver_mode))
        return True

    def fake_remove(name):
        calls.append(("remove", name))
        return True

    monkeypatch.setattr("app.api.printers.cups.add_printer", fake_add)
    monkeypatch.setattr("app.api.printers.cups.remove_printer", fake_remove)
    monkeypatch.setattr("app.api.printers.cups.printer_status", lambda name: "idle")

    created = admin_client.post(
        "/api/printers",
        json={
            "name": f"Queue-{uuid4().hex[:6]}",
            "device_uri": "ipp://192.0.2.40/ipp/print",
        },
    )
    assert created.status_code == 201
    printer = created.json()
    assert printer["status"] == "idle"
    assert calls[0][0] == "add"

    patched = admin_client.patch(
        f"/api/printers/{printer['id']}",
        json={"device_uri": "ipps://192.0.2.40/ipp/print"},
    )
    assert patched.status_code == 200
    assert calls[-1][0] == "add"

    assert admin_client.delete(f"/api/printers/{printer['id']}").status_code == 204
    assert calls[-1] == ("remove", printer["slug"])
