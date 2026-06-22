"""SQLite-backed role-based access control repository."""

import json
from pathlib import Path
import sqlite3


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('active', 'disabled'))
);
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY,
    resource TEXT NOT NULL,
    action TEXT NOT NULL,
    UNIQUE (resource, action)
);
CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER NOT NULL REFERENCES users(id),
    role_id INTEGER NOT NULL REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER NOT NULL REFERENCES roles(id),
    permission_id INTEGER NOT NULL REFERENCES permissions(id),
    PRIMARY KEY (role_id, permission_id)
);
"""


class RBACRepository:
    """Initialize, seed and query the RBAC database."""

    def __init__(self, db_path: Path):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(SCHEMA)

    def seed(self, seed_path: Path) -> None:
        seed = json.loads(seed_path.read_text(encoding="utf-8"))
        with self._connect() as connection:
            for user in seed["users"]:
                connection.execute(
                    """
                    INSERT INTO users(username, status) VALUES (?, ?)
                    ON CONFLICT(username) DO UPDATE SET status = excluded.status
                    """,
                    (user["username"], user["status"]),
                )
            for role in seed["roles"]:
                connection.execute(
                    "INSERT INTO roles(name) VALUES (?) ON CONFLICT(name) DO NOTHING",
                    (role["name"],),
                )
            for permission in seed["permissions"]:
                connection.execute(
                    """
                    INSERT INTO permissions(resource, action) VALUES (?, ?)
                    ON CONFLICT(resource, action) DO NOTHING
                    """,
                    (permission["resource"], permission["action"]),
                )
            for assignment in seed["user_roles"]:
                user = connection.execute(
                    "SELECT id FROM users WHERE username = ?", (assignment["username"],)
                ).fetchone()
                role = connection.execute(
                    "SELECT id FROM roles WHERE name = ?", (assignment["role"],)
                ).fetchone()
                if user is None or role is None:
                    raise ValueError("user_roles contains unknown user or role")
                connection.execute(
                    "INSERT OR IGNORE INTO user_roles(user_id, role_id) VALUES (?, ?)",
                    (user[0], role[0]),
                )
            for grant in seed["role_permissions"]:
                role = connection.execute(
                    "SELECT id FROM roles WHERE name = ?", (grant["role"],)
                ).fetchone()
                permission = connection.execute(
                    "SELECT id FROM permissions WHERE resource = ? AND action = ?",
                    (grant["resource"], grant["action"]),
                ).fetchone()
                if role is None or permission is None:
                    raise ValueError("role_permissions contains unknown role or permission")
                connection.execute(
                    "INSERT OR IGNORE INTO role_permissions(role_id, permission_id) VALUES (?, ?)",
                    (role[0], permission[0]),
                )

    def has_permission(self, username: str, resource: str, action: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM users
                JOIN user_roles ON user_roles.user_id = users.id
                JOIN role_permissions ON role_permissions.role_id = user_roles.role_id
                JOIN permissions ON permissions.id = role_permissions.permission_id
                WHERE users.username = ?
                  AND users.status = 'active'
                  AND permissions.resource = ?
                  AND permissions.action = ?
                LIMIT 1
                """,
                (username, resource, action),
            ).fetchone()
        return row is not None
