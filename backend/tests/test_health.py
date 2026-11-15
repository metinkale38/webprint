def test_health(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_admin_login_and_me(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "test-password"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin"
    assert "access_token" in response.cookies

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["username"] == "admin"


def test_login_rejects_invalid_password(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert response.status_code == 401


def test_printers_require_authentication(client):
    response = client.get("/api/printers")
    assert response.status_code == 401


def test_spa_fallback_serves_index(client):
    response = client.get("/admin")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "PrintTool Demo" in response.text


def test_unknown_api_path_returns_404(client):
    assert client.get("/api/unbekannt").status_code == 404
