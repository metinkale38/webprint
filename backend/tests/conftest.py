import os
import tempfile
from pathlib import Path
from uuid import uuid4

_fake_bin = Path(tempfile.mkdtemp(prefix="printtool-fakecups-"))
_FAKE_SCRIPTS = {
    "lp": '#!/bin/sh\necho "request id is ${2:-fake-queue}-1 (1 file(s))"\nexit 0\n',
    "lpadmin": "#!/bin/sh\nexit 0\n",
    "cupsenable": "#!/bin/sh\nexit 0\n",
    "cupsaccept": "#!/bin/sh\nexit 0\n",
    "cancel": "#!/bin/sh\nexit 0\n",
    "lpoptions": "#!/bin/sh\nexit 0\n",
    "ipptool": "#!/bin/sh\nexit 0\n",
    "snmpget": "#!/bin/sh\nexit 1\n",
    "lpstat": (
        '#!/bin/sh\n'
        'case " $* " in\n'
        '  *" -p "*)\n'
        "    for last; do :; done\n"
        '    echo "printer $last is idle. enabled since now"\n'
        "    exit 0\n"
        "    ;;\n"
        "  *) exit 0 ;;\n"
        "esac\n"
    ),
}
for _name, _script in _FAKE_SCRIPTS.items():
    _path = _fake_bin / _name
    _path.write_text(_script)
    _path.chmod(0o755)
os.environ["PATH"] = f"{_fake_bin}:{os.environ.get('PATH', '')}"

_tmp = Path(tempfile.mkdtemp(prefix="printtool-test-"))
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp / 'test.db'}"
os.environ["JWT_SECRET"] = "test-secret-with-at-least-32-bytes"
os.environ["UPLOAD_DIR"] = str(_tmp / "uploads")
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "test-password"
os.environ["COOKIE_SECURE"] = "false"
os.environ["DISCOVERY_ENABLED"] = "false"
os.environ["JOB_SYNC_ENABLED"] = "false"

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
