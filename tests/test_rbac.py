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
