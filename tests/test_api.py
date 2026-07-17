from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
import threading

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


def create_transfer(client: TestClient, token: str) -> str:
    response = client.post(
        "/transactions",
        headers=auth(token),
        json={
            "source_account": "001100001234",
            "destination_account": "002200005678",
            "beneficiary_name": "Lê Bình",
            "amount_vnd": 50_000_000,
            "description": "Thanh toán hợp đồng",
        },
    )
    assert response.status_code == 201
    return response.json()["reference"]


class ApprovalRaceConnection(sqlite3.Connection):
    approval_barrier: threading.Barrier | None = None

    def execute(
        self, sql: str, parameters: tuple[object, ...] = ()
    ) -> sqlite3.Cursor:
        normalized = " ".join(sql.split()).lower()
        if (
            self.approval_barrier is not None
            and normalized.startswith("update transactions")
            and "status = 'pending'" in normalized
        ):
            self.approval_barrier.wait(timeout=5)
        return super().execute(sql, parameters)


class ApprovalRaceRepository(RBACRepository):
    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.db_path, timeout=5, factory=ApprovalRaceConnection
        )
        connection.execute("PRAGMA foreign_keys = ON")
        return connection


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


def test_baseline_then_rbac_requires_controller_approval(client: TestClient) -> None:
    admin_token = login(client, "admin01", "Admin@123")
    created = client.post(
        "/users",
        headers=auth(admin_token),
        json={
            "username": "lan.demo",
            "display_name": "Lan Nguyễn",
            "password": "Lan@1234",
            "role": "teller",
        },
    )
    assert created.status_code == 201
    teller_token = login(client, "lan.demo", "Lan@1234")

    baseline_reference = create_transfer(client, teller_token)
    baseline_approval = client.post(
        f"/transactions/{baseline_reference}/approve", headers=auth(teller_token)
    )
    assert baseline_approval.status_code == 200
    assert baseline_approval.json()["status"] == "approved"
    assert baseline_approval.json()["approved_by"] == "lan.demo"

    changed_mode = client.patch(
        "/demo/security-mode",
        headers=auth(admin_token),
        json={"mode": "rbac"},
    )
    assert changed_mode.status_code == 200
    assert changed_mode.json() == {"mode": "rbac"}

    rbac_reference = create_transfer(client, teller_token)
    denied = client.post(
        f"/transactions/{rbac_reference}/approve", headers=auth(teller_token)
    )
    assert denied.status_code == 403
    assert denied.json()["detail"]["permission"] == "transactions:approve"
    unchanged = client.get(
        f"/transactions/{rbac_reference}", headers=auth(teller_token)
    )
    assert unchanged.status_code == 200
    assert unchanged.json()["status"] == "pending"

    controller_token = login(client, "controller01", "Controller@123")
    approved = client.post(
        f"/transactions/{rbac_reference}/approve", headers=auth(controller_token)
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert approved.json()["approved_by"] == "controller01"

    repeated = client.post(
        f"/transactions/{rbac_reference}/approve", headers=auth(controller_token)
    )
    assert repeated.status_code == 409


def test_concurrent_approval_has_one_winner_and_one_conflict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = ApprovalRaceRepository(tmp_path / "approval-race.db")
    monkeypatch.setattr(api, "repository", repository)

    with TestClient(api.app) as test_client:
        admin_token = login(test_client, "admin01", "Admin@123")
        created = test_client.post(
            "/users",
            headers=auth(admin_token),
            json={
                "username": "lan.demo",
                "display_name": "Lan Nguyễn",
                "password": "Lan@1234",
                "role": "teller",
            },
        )
        assert created.status_code == 201
        teller_token = login(test_client, "lan.demo", "Lan@1234")
        reference = create_transfer(test_client, teller_token)
        changed_mode = test_client.patch(
            "/demo/security-mode",
            headers=auth(admin_token),
            json={"mode": "rbac"},
        )
        assert changed_mode.status_code == 200
        controller_token = login(test_client, "controller01", "Controller@123")

        ApprovalRaceConnection.approval_barrier = threading.Barrier(2)
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                responses = list(
                    executor.map(
                        lambda _: test_client.post(
                            f"/transactions/{reference}/approve",
                            headers=auth(controller_token),
                        ),
                        range(2),
                    )
                )
        finally:
            ApprovalRaceConnection.approval_barrier = None

        assert sorted(response.status_code for response in responses) == [200, 409]
        transaction = repository.get_transaction(
            reference, "controller01", read_all=True
        )
        assert transaction is not None
        assert transaction["status"] == "approved"
        assert transaction["approved_by"] == "controller01"

        approval_successes = [
            event
            for event in repository.transaction_timeline(reference)
            if event["action"] == "approve" and event["outcome"] == "success"
        ]
        assert len(approval_successes) == 1


def test_approval_resource_is_protected_and_audited(client: TestClient) -> None:
    admin_token = login(client, "admin01", "Admin@123")
    created = client.post(
        "/users",
        headers=auth(admin_token),
        json={
            "username": "lan.demo",
            "display_name": "Lan Nguyễn",
            "password": "Lan@1234",
            "role": "teller",
        },
    )
    assert created.status_code == 201
    teller_token = login(client, "lan.demo", "Lan@1234")
    reference = create_transfer(client, teller_token)

    baseline_view = client.get(
        f"/approvals/{reference}", headers=auth(teller_token)
    )
    assert baseline_view.status_code == 200
    assert baseline_view.json()["reference"] == reference

    changed = client.patch(
        "/demo/security-mode",
        headers=auth(admin_token),
        json={"mode": "rbac"},
    )
    assert changed.status_code == 200

    denied = client.get(f"/approvals/{reference}", headers=auth(teller_token))
    assert denied.status_code == 403
    unchanged = client.get(
        f"/transactions/{reference}", headers=auth(teller_token)
    )
    assert unchanged.json()["status"] == "pending"

    controller_token = login(client, "controller01", "Controller@123")
    allowed = client.get(
        f"/approvals/{reference}", headers=auth(controller_token)
    )
    assert allowed.status_code == 200
    assert allowed.json()["reference"] == reference
    assert client.get(
        "/approvals/TXN-DOES-NOT-EXIST", headers=auth(controller_token)
    ).status_code == 404
    assert client.get(
        "/approvals/TXN-DOES-NOT-EXIST", headers=auth(teller_token)
    ).status_code == 403

    logs = client.get("/audit-logs", headers=auth(admin_token)).json()
    review_outcomes = [
        event["outcome"]
        for event in logs
        if event["transaction_reference"] == reference
        and event["resource"] == "transactions"
        and event["action"] == "review"
    ]
    assert "baseline_bypass" in review_outcomes
    assert "denied" in review_outcomes
    assert "allowed" in review_outcomes


def test_transaction_lists_are_role_aware_and_timeline_is_ordered(
    client: TestClient,
) -> None:
    admin_token = login(client, "admin01", "Admin@123")
    client.post(
        "/users",
        headers=auth(admin_token),
        json={
            "username": "lan.demo",
            "display_name": "Lan Nguyễn",
            "password": "Lan@1234",
            "role": "teller",
        },
    )
    teller_token = login(client, "lan.demo", "Lan@1234")
    reference = create_transfer(client, teller_token)

    teller_rows = client.get("/transactions", headers=auth(teller_token))
    admin_rows = client.get("/transactions", headers=auth(admin_token))
    assert [row["reference"] for row in teller_rows.json()] == [reference]
    assert [row["reference"] for row in admin_rows.json()] == [reference]

    denied_audit = client.get("/audit-logs", headers=auth(teller_token))
    denied_users = client.get("/users", headers=auth(teller_token))
    assert denied_audit.status_code == 403
    assert denied_users.status_code == 403

    timeline = client.get(
        f"/transactions/{reference}/timeline", headers=auth(teller_token)
    )
    assert timeline.status_code == 200
    assert [event["action"] for event in timeline.json()] == ["create"]


def test_only_admin_can_change_security_mode_and_transaction_is_validated(
    client: TestClient,
) -> None:
    admin_token = login(client, "admin01", "Admin@123")
    controller_token = login(client, "controller01", "Controller@123")
    assert client.get("/demo/security-mode", headers=auth(controller_token)).json() == {
        "mode": "baseline"
    }
    denied = client.patch(
        "/demo/security-mode",
        headers=auth(controller_token),
        json={"mode": "rbac"},
    )
    assert denied.status_code == 403

    invalid = client.post(
        "/transactions",
        headers=auth(admin_token),
        json={
            "source_account": "1",
            "destination_account": "2",
            "beneficiary_name": "X",
            "amount_vnd": 0,
            "description": "x",
        },
    )
    assert invalid.status_code in {403, 422}
