"""SQLite-backed role-based access control repository."""

import json
from pathlib import Path
import sqlite3
from datetime import UTC, datetime
import hashlib
import secrets


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('active', 'disabled')),
    display_name TEXT NOT NULL DEFAULT '',
    password_hash TEXT
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
CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    expires_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS customer_accounts (
    id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    address TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL,
    username TEXT,
    resource TEXT NOT NULL,
    action TEXT NOT NULL,
    outcome TEXT NOT NULL CHECK (outcome IN ('allowed', 'denied', 'success', 'failed')),
    detail TEXT NOT NULL DEFAULT ''
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

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password with a random salt using only the standard library."""
        salt = secrets.token_bytes(16)
        derived = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
        return f"{salt.hex()}:{derived.hex()}"

    @staticmethod
    def verify_password(password: str, stored_hash: str | None) -> bool:
        if not stored_hash:
            return False
        try:
            salt_hex, digest_hex = stored_hash.split(":", maxsplit=1)
            expected = bytes.fromhex(digest_hex)
            actual = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1)
        except (ValueError, TypeError):
            return False
        return secrets.compare_digest(actual, expected)

    def create_user(self, username: str, display_name: str, password: str, role: str) -> None:
        password_hash = self.hash_password(password)
        with self._connect() as connection:
            role_row = connection.execute("SELECT id FROM roles WHERE name = ?", (role,)).fetchone()
            if role_row is None:
                raise ValueError("unknown role")
            try:
                cursor = connection.execute(
                    "INSERT INTO users(username, status, display_name, password_hash) VALUES (?, 'active', ?, ?)",
                    (username, display_name, password_hash),
                )
            except sqlite3.IntegrityError as error:
                raise ValueError("username already exists") from error
            connection.execute("INSERT INTO user_roles(user_id, role_id) VALUES (?, ?)", (cursor.lastrowid, role_row[0]))

    def authenticate(self, username: str, password: str) -> dict[str, str] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, username, display_name, password_hash, status FROM users WHERE username = ?", (username,)
            ).fetchone()
        if row is None or row[4] != "active" or not self.verify_password(password, row[3]):
            return None
        return {"id": str(row[0]), "username": row[1], "display_name": row[2]}

    def create_session(self, user_id: int) -> str:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC).replace(microsecond=0).isoformat()
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO sessions(token_hash, user_id, expires_at) VALUES (?, ?, ?)",
                (hashlib.sha256(token.encode()).hexdigest(), user_id, expires_at),
            )
        return token

    def delete_session(self, token: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (hashlib.sha256(token.encode()).hexdigest(),))

    def session_user(self, token: str) -> dict[str, str] | None:
        with self._connect() as connection:
            row = connection.execute(
                """SELECT users.id, users.username, users.display_name, users.status
                FROM sessions JOIN users ON users.id = sessions.user_id
                WHERE sessions.token_hash = ?""",
                (hashlib.sha256(token.encode()).hexdigest(),),
            ).fetchone()
        if row is None or row[3] != "active":
            return None
        return {"id": str(row[0]), "username": row[1], "display_name": row[2]}

    def user_roles(self, username: str) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                """SELECT roles.name FROM users JOIN user_roles ON user_roles.user_id = users.id
                JOIN roles ON roles.id = user_roles.role_id WHERE users.username = ? ORDER BY roles.name""",
                (username,),
            ).fetchall()
        return [row[0] for row in rows]

    def list_roles(self) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute("SELECT name FROM roles ORDER BY name").fetchall()
        return [row[0] for row in rows]

    def list_users(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT username, display_name, status FROM users ORDER BY username").fetchall()
        return [{"username": row[0], "display_name": row[1], "status": row[2], "roles": self.user_roles(row[0])} for row in rows]

    def list_accounts(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT id, customer_name, phone, address FROM customer_accounts ORDER BY id").fetchall()
        return [{"id": row[0], "customer_name": row[1], "phone": row[2], "address": row[3]} for row in rows]

    def update_account(self, account_id: int, phone: str, address: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("UPDATE customer_accounts SET phone = ?, address = ? WHERE id = ?", (phone, address, account_id))
        return cursor.rowcount == 1

    def audit(self, username: str | None, resource: str, action: str, outcome: str, detail: str = "") -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO audit_logs(created_at, username, resource, action, outcome, detail) VALUES (?, ?, ?, ?, ?, ?)",
                (datetime.now(UTC).replace(microsecond=0).isoformat(), username, resource, action, outcome, detail),
            )

    def list_audit_logs(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT created_at, username, resource, action, outcome, detail FROM audit_logs ORDER BY id DESC LIMIT 100"
            ).fetchall()
        return [{"created_at": row[0], "username": row[1], "resource": row[2], "action": row[3], "outcome": row[4], "detail": row[5]} for row in rows]

    def reset_demo(self) -> None:
        with self._connect() as connection:
            connection.executescript("DELETE FROM sessions; DELETE FROM audit_logs; DELETE FROM customer_accounts; DELETE FROM role_permissions; DELETE FROM user_roles; DELETE FROM permissions; DELETE FROM roles; DELETE FROM users;")
        self.initialize()
        self._seed_demo()

    def _seed_demo(self) -> None:
        with self._connect() as connection:
            for role in ("administrator", "teller", "auditor"):
                connection.execute("INSERT INTO roles(name) VALUES (?)", (role,))
            permissions = (("accounts", "read"), ("accounts", "update"), ("users", "manage"), ("audit_logs", "read"))
            for resource, action in permissions:
                connection.execute("INSERT INTO permissions(resource, action) VALUES (?, ?)", (resource, action))
            grants = {"administrator": permissions, "teller": permissions[:2], "auditor": (("accounts", "read"), ("audit_logs", "read"))}
            for role, role_permissions in grants.items():
                for resource, action in role_permissions:
                    connection.execute("""INSERT INTO role_permissions(role_id, permission_id)
                    SELECT roles.id, permissions.id FROM roles, permissions
                    WHERE roles.name = ? AND permissions.resource = ? AND permissions.action = ?""", (role, resource, action))
        self.create_user("admin01", "Minh Trần", "Admin@123", "administrator")
        with self._connect() as connection:
            connection.executemany(
                "INSERT INTO customer_accounts(customer_name, phone, address) VALUES (?, ?, ?)",
                [("Nguyễn An", "0901000001", "Quận 1, TP.HCM"), ("Trần Bình", "0901000002", "Thủ Đức, TP.HCM")],
            )

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

    def list_access_rows(self) -> list[dict[str, str]]:
        """Return the user-to-role-to-permission links for an RBAC view."""
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT users.username, users.status, roles.name, permissions.resource,
                       permissions.action
                FROM users
                JOIN user_roles ON user_roles.user_id = users.id
                JOIN roles ON roles.id = user_roles.role_id
                JOIN role_permissions ON role_permissions.role_id = roles.id
                JOIN permissions ON permissions.id = role_permissions.permission_id
                ORDER BY users.username, roles.name, permissions.resource, permissions.action
                """
            ).fetchall()
        return [
            {
                "username": username,
                "status": status,
                "role": role,
                "resource": resource,
                "action": action,
            }
            for username, status, role, resource, action in rows
        ]
