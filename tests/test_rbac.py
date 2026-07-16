import json
from pathlib import Path
import sqlite3

import pytest

from rbac_guard.rbac import RBACRepository


@pytest.fixture
def seed_path(tmp_path: Path) -> Path:
    path = tmp_path / "seed.json"
    path.write_text(
        json.dumps(
            {
                "users": [
                    {"username": "teller01", "status": "active"},
                    {"username": "disabled01", "status": "disabled"},
                ],
                "roles": [{"name": "teller"}],
                "permissions": [{"resource": "accounts", "action": "read"}],
                "user_roles": [
                    {"username": "teller01", "role": "teller"},
                    {"username": "disabled01", "role": "teller"},
                ],
                "role_permissions": [
                    {"role": "teller", "resource": "accounts", "action": "read"}
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def seed_db(tmp_path: Path, seed_path: Path) -> Path:
    db_path = tmp_path / "rbac.db"
    repository = RBACRepository(db_path)
    repository.initialize()
    repository.seed(seed_path)
    return db_path


def test_permission_matrix(seed_db: Path) -> None:
    checker = RBACRepository(seed_db)

    assert checker.has_permission("teller01", "accounts", "read") is True
    assert checker.has_permission("teller01", "users", "delete") is False
    assert checker.has_permission("disabled01", "accounts", "read") is False
    assert checker.has_permission("missing", "accounts", "read") is False


def test_seed_is_idempotent(seed_db: Path, seed_path: Path) -> None:
    repository = RBACRepository(seed_db)

    repository.seed(seed_path)

    with sqlite3.connect(seed_db) as connection:
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 2
        assert connection.execute("SELECT COUNT(*) FROM user_roles").fetchone()[0] == 2


def test_invalid_assignment_rolls_back_entire_seed(tmp_path: Path) -> None:
    db_path = tmp_path / "rollback.db"
    seed_path = tmp_path / "invalid.json"
    seed_path.write_text(
        json.dumps(
            {
                "users": [{"username": "new-user", "status": "active"}],
                "roles": [],
                "permissions": [],
                "user_roles": [{"username": "new-user", "role": "missing-role"}],
                "role_permissions": [],
            }
        ),
        encoding="utf-8",
    )
    repository = RBACRepository(db_path)
    repository.initialize()

    with pytest.raises(ValueError, match="unknown user or role"):
        repository.seed(seed_path)

    with sqlite3.connect(db_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0


def test_project_seed_grants_expected_roles(tmp_path: Path) -> None:
    repository = RBACRepository(tmp_path / "project-seed.db")
    repository.initialize()
    repository.seed(Path("data/rbac_seed.json"))

    assert repository.has_permission("teller01", "accounts", "read") is True
    assert repository.has_permission("auditor01", "audit_logs", "read") is True
    assert repository.has_permission("teller01", "users", "delete") is False


def test_list_access_rows_exposes_user_role_permission_links(seed_db: Path) -> None:
    rows = RBACRepository(seed_db).list_access_rows()

    assert rows == [
        {
            "username": "disabled01",
            "status": "disabled",
            "role": "teller",
            "resource": "accounts",
            "action": "read",
        },
        {
            "username": "teller01",
            "status": "active",
            "role": "teller",
            "resource": "accounts",
            "action": "read",
        },
    ]


@pytest.fixture
def demo_repository(tmp_path: Path) -> RBACRepository:
    repository = RBACRepository(tmp_path / "demo.db")
    repository.initialize()
    repository.reset_demo()
    repository.create_user("lan.demo", "Lan Nguyễn", "Lan@1234", "teller")
    return repository


def test_demo_reset_seeds_baseline_controller_and_transaction_permissions(
    demo_repository: RBACRepository,
) -> None:
    assert demo_repository.security_mode() == "baseline"
    assert demo_repository.authenticate("controller01", "Controller@123") is not None
    assert demo_repository.has_permission("lan.demo", "transactions", "create") is True
    assert demo_repository.has_permission("lan.demo", "transactions", "approve") is False
    assert demo_repository.has_permission("controller01", "transactions", "approve") is True


def test_transaction_lifecycle_filters_rows_and_rejects_second_approval(
    demo_repository: RBACRepository,
) -> None:
    transaction = demo_repository.create_transaction(
        creator="lan.demo",
        source_account="001100001234",
        destination_account="002200005678",
        beneficiary_name="Lê Bình",
        amount_vnd=50_000_000,
        description="Thanh toán hợp đồng",
    )

    assert transaction["reference"].startswith("TRX-")
    assert transaction["status"] == "pending"
    assert demo_repository.list_transactions("lan.demo", read_all=False) == [transaction]
    assert demo_repository.list_transactions("admin01", read_all=False) == []
    assert demo_repository.get_transaction(
        transaction["reference"], "admin01", read_all=False
    ) is None

    approved = demo_repository.approve_transaction(
        transaction["reference"], "controller01"
    )

    assert approved["status"] == "approved"
    assert approved["approved_by"] == "controller01"
    assert demo_repository.list_transactions("admin01", read_all=True) == [approved]
    with pytest.raises(ValueError, match="already processed"):
        demo_repository.approve_transaction(transaction["reference"], "controller01")


def test_security_mode_and_transaction_timeline_are_persisted(
    demo_repository: RBACRepository,
) -> None:
    demo_repository.set_security_mode("rbac", "admin01")
    transaction = demo_repository.create_transaction(
        creator="lan.demo",
        source_account="001100001234",
        destination_account="002200005678",
        beneficiary_name="Lê Bình",
        amount_vnd=50_000_000,
        description="Thanh toán hợp đồng",
    )
    demo_repository.audit(
        "lan.demo",
        "transactions",
        "approve",
        "denied",
        "RBAC denied request",
        transaction_reference=str(transaction["reference"]),
    )

    assert demo_repository.security_mode() == "rbac"
    assert [event["outcome"] for event in demo_repository.transaction_timeline(str(transaction["reference"]))] == [
        "success",
        "denied",
    ]


def test_expired_session_is_rejected_and_deleted(demo_repository: RBACRepository) -> None:
    admin = demo_repository.authenticate("admin01", "Admin@123")
    assert admin is not None
    token = demo_repository.create_session(int(admin["id"]))
    with sqlite3.connect(demo_repository.db_path) as connection:
        connection.execute(
            "UPDATE sessions SET expires_at = '2000-01-01T00:00:00+00:00'"
        )

    assert demo_repository.session_user(token) is None
    with sqlite3.connect(demo_repository.db_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] == 0
