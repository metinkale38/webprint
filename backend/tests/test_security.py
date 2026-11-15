from app.config import settings


def test_security_headers(client):
    response = client.get("/healthz")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "content-security-policy" in response.headers


def test_oversized_request_is_rejected(client, monkeypatch):
    monkeypatch.setattr(settings, "upload_max_mb", 0)
    response = client.post(
        "/api/auth/login",
        content=b"x" * 2_000_000,
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 413


def test_role_guards(user_client):
    assert user_client.get("/api/users").status_code == 403
    assert user_client.get("/api/stats/overview").status_code == 403
    assert user_client.get("/api/printers").status_code == 200
