from pathlib import Path

from fastapi.testclient import TestClient
import pytest

import rbac_guard.api as api
from rbac_guard.rbac import RBACRepository


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(api, "repository", RBACRepository(tmp_path / "banksafe.db"))
    with TestClient(api.app) as test_client:
        yield test_client


def login(client: TestClient, username: str, password: str) -> str:
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["token"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_admin_creates_teller_then_backend_enforces_permissions(client: TestClient) -> None:
    admin_token = login(client, "admin01", "Admin@123")
    created = client.post("/users", headers=auth(admin_token), json={"username": "lan.demo", "display_name": "Lan Demo", "password": "Lan@1234", "role": "teller"})
    assert created.status_code == 201
    teller_token = login(client, "lan.demo", "Lan@1234")
    accounts = client.get("/accounts", headers=auth(teller_token))
    assert accounts.status_code == 200
    account_id = accounts.json()[0]["id"]
    changed = client.patch(f"/accounts/{account_id}", headers=auth(teller_token), json={"phone": "0909999999", "address": "Demo District 1"})
    assert changed.status_code == 200
    assert changed.json()["phone"] == "0909999999"
    denied = client.get("/users", headers=auth(teller_token))
    assert denied.status_code == 403
    assert denied.json()["detail"]["permission"] == "users:manage"


def test_auditor_reads_logs_and_reset_invalidates_sessions(client: TestClient) -> None:
    admin_token = login(client, "admin01", "Admin@123")
    client.post("/users", headers=auth(admin_token), json={"username": "ha.demo", "display_name": "Hà Demo", "password": "HaDemo@1", "role": "auditor"})
    auditor_token = login(client, "ha.demo", "HaDemo@1")
    logs = client.get("/audit-logs", headers=auth(auditor_token))
    assert logs.status_code == 200
    assert any(item["resource"] == "session" for item in logs.json())
    reset = client.post("/demo/reset", headers=auth(admin_token))
    assert reset.status_code == 200
    assert client.get("/auth/me", headers=auth(admin_token)).status_code == 401
    assert login(client, "admin01", "Admin@123")


def test_login_rejects_invalid_password(client: TestClient) -> None:
    response = client.post("/auth/login", json={"username": "admin01", "password": "wrongpass"})
    assert response.status_code == 401
