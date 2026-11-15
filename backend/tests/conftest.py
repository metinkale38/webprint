import os
import tempfile
from pathlib import Path

_tmp = Path(tempfile.mkdtemp(prefix="printtool-test-"))
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp / 'test.db'}"
os.environ["JWT_SECRET"] = "test-secret-with-at-least-32-bytes"
os.environ["UPLOAD_DIR"] = str(_tmp / "uploads")
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "test-password"
os.environ["COOKIE_SECURE"] = "false"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
