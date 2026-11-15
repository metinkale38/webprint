import os
import tempfile
from pathlib import Path
from uuid import uuid4

_tmp = Path(tempfile.mkdtemp(prefix="printtool-test-"))
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp / 'test.db'}"
os.environ["JWT_SECRET"] = "test-secret-with-at-least-32-bytes"
os.environ["UPLOAD_DIR"] = str(_tmp / "uploads")
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "test-password"
os.environ["COOKIE_SECURE"] = "false"
os.environ["DISCOVERY_ENABLED"] = "false"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine
from app.main import app
from app.services.rate_limit import login_limiter


@pytest.fixture(autouse=True)
def reset_login_limiter():
    login_limiter.reset()
    yield
    login_limiter.reset()


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        yield session


@pytest.fixture()
def admin_client():
    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "test-password"},
        )
        assert response.status_code == 200
        yield test_client


@pytest.fixture()
def user_client(admin_client):
    username = f"user-{uuid4().hex[:8]}"
    password = "user-password"
    response = admin_client.post(
        "/api/users",
        json={"username": username, "password": password, "role": "user"},
    )
    assert response.status_code == 201

    with TestClient(app) as test_client:
        login = test_client.post(
            "/api/auth/login",
            json={"username": username, "password": password},
        )
        assert login.status_code == 200
        yield test_client
