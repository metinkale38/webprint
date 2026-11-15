def test_refresh_and_logout(client):
    login = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "test-password"},
    )
    assert login.status_code == 200

    refresh = client.post("/api/auth/refresh")
    assert refresh.status_code == 200
    assert refresh.json()["username"] == "admin"

    logout = client.post("/api/auth/logout")
    assert logout.status_code == 200

    assert client.get("/api/auth/me").status_code == 401


def test_login_cookie_flags(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "test-password"},
    )
    assert response.status_code == 200

    cookies = response.headers.get_list("set-cookie")
    access = next(cookie for cookie in cookies if cookie.startswith("access_token="))
    refresh = next(cookie for cookie in cookies if cookie.startswith("refresh_token="))

    assert "HttpOnly" in access
    assert "SameSite=strict" in access
    assert "Path=/" in access
    assert "HttpOnly" in refresh


def test_login_rate_limit(client):
    for _ in range(5):
        response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "wrong"},
        )
        assert response.status_code == 401

    blocked = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert blocked.status_code == 429
