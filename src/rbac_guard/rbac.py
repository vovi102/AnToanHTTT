"""SQLite-backed role-based access control repository."""

import json
from pathlib import Path
import sqlite3
from datetime import UTC, datetime, timedelta
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
    role_at_event TEXT,
    resource TEXT NOT NULL,
    action TEXT NOT NULL,
    outcome TEXT NOT NULL CHECK (outcome IN ('allowed', 'denied', 'success', 'failed', 'baseline_bypass', 'conflict')),
    transaction_reference TEXT,
    detail TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS demo_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    reference TEXT NOT NULL UNIQUE,
    source_account TEXT NOT NULL,
    destination_account TEXT NOT NULL,
    beneficiary_name TEXT NOT NULL,
    amount_vnd INTEGER NOT NULL CHECK (amount_vnd > 0),
    description TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'approved')),
    created_by INTEGER NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL,
    approved_by INTEGER REFERENCES users(id),
    approved_at TEXT
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
            audit_sql = connection.execute(
                "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'audit_logs'"
            ).fetchone()[0]
            if "baseline_bypass" not in audit_sql:
                connection.executescript(
                    """
                    ALTER TABLE audit_logs RENAME TO audit_logs_legacy;
                    CREATE TABLE audit_logs (
                        id INTEGER PRIMARY KEY,
                        created_at TEXT NOT NULL,
                        username TEXT,
                        role_at_event TEXT,
                        resource TEXT NOT NULL,
                        action TEXT NOT NULL,
                        outcome TEXT NOT NULL CHECK (outcome IN ('allowed', 'denied', 'success', 'failed', 'baseline_bypass', 'conflict')),
                        transaction_reference TEXT,
                        detail TEXT NOT NULL DEFAULT ''
                    );
                    INSERT INTO audit_logs(id, created_at, username, resource, action, outcome, detail)
                    SELECT id, created_at, username, resource, action, outcome, detail
                    FROM audit_logs_legacy;
                    DROP TABLE audit_logs_legacy;
                    """
                )

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
        expires_at = (datetime.now(UTC) + timedelta(hours=8)).replace(microsecond=0).isoformat()
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
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        with self._connect() as connection:
            row = connection.execute(
                """SELECT users.id, users.username, users.display_name, users.status,
                           sessions.expires_at
                FROM sessions JOIN users ON users.id = sessions.user_id
                WHERE sessions.token_hash = ?""",
                (token_hash,),
            ).fetchone()
            if row is not None and datetime.fromisoformat(row[4]) <= datetime.now(UTC):
                connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
                return None
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

    def audit(
        self,
        username: str | None,
        resource: str,
        action: str,
        outcome: str,
        detail: str = "",
        *,
        transaction_reference: str | None = None,
    ) -> None:
        roles = self.user_roles(username) if username else []
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO audit_logs(
                    created_at, username, role_at_event, resource, action, outcome,
                    transaction_reference, detail
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    datetime.now(UTC).replace(microsecond=0).isoformat(),
                    username,
                    roles[0] if roles else None,
                    resource,
                    action,
                    outcome,
                    transaction_reference,
                    detail,
                ),
            )

    def list_audit_logs(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """SELECT id, created_at, username, role_at_event, resource, action,
                          outcome, transaction_reference, detail
                   FROM audit_logs ORDER BY id DESC LIMIT 100"""
            ).fetchall()
        return [
            {
                "id": row[0],
                "created_at": row[1],
                "username": row[2],
                "role_at_event": row[3],
                "resource": row[4],
                "action": row[5],
                "outcome": row[6],
                "transaction_reference": row[7],
                "detail": row[8],
            }
            for row in rows
        ]

    def security_mode(self) -> str:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT value FROM demo_settings WHERE key = 'security_mode'"
            ).fetchone()
        return row[0] if row else "baseline"

    def set_security_mode(self, mode: str, actor: str) -> None:
        if mode not in {"baseline", "rbac"}:
            raise ValueError("invalid security mode")
        previous = self.security_mode()
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO demo_settings(key, value)
                VALUES ('security_mode', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value""",
                (mode,),
            )
        self.audit(
            actor,
            "demo",
            "configure",
            "success",
            f"Security mode changed from {previous} to {mode}",
        )

    @staticmethod
    def _transaction_dict(row: sqlite3.Row | tuple[object, ...]) -> dict[str, object]:
        return {
            "id": row[0],
            "reference": row[1],
            "source_account": row[2],
            "destination_account": row[3],
            "beneficiary_name": row[4],
            "amount_vnd": row[5],
            "description": row[6],
            "status": row[7],
            "created_by": row[8],
            "created_at": row[9],
            "approved_by": row[10],
            "approved_at": row[11],
        }

    @staticmethod
    def _transaction_select() -> str:
        return """SELECT transactions.id, transactions.reference,
                         transactions.source_account, transactions.destination_account,
                         transactions.beneficiary_name, transactions.amount_vnd,
                         transactions.description, transactions.status,
                         creator.username, transactions.created_at,
                         approver.username, transactions.approved_at
                  FROM transactions
                  JOIN users AS creator ON creator.id = transactions.created_by
                  LEFT JOIN users AS approver ON approver.id = transactions.approved_by"""

    def create_transaction(
        self,
        *,
        creator: str,
        source_account: str,
        destination_account: str,
        beneficiary_name: str,
        amount_vnd: int,
        description: str,
    ) -> dict[str, object]:
        now = datetime.now(UTC).replace(microsecond=0)
        day_prefix = now.strftime("TRX-%Y%m%d-")
        with self._connect() as connection:
            user = connection.execute(
                "SELECT id FROM users WHERE username = ? AND status = 'active'",
                (creator,),
            ).fetchone()
            if user is None:
                raise ValueError("unknown creator")
            count = connection.execute(
                "SELECT COUNT(*) FROM transactions WHERE reference LIKE ?",
                (f"{day_prefix}%",),
            ).fetchone()[0]
            reference = f"{day_prefix}{count + 1:03d}"
            connection.execute(
                """INSERT INTO transactions(
                    reference, source_account, destination_account, beneficiary_name,
                    amount_vnd, description, status, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)""",
                (
                    reference,
                    source_account,
                    destination_account,
                    beneficiary_name,
                    amount_vnd,
                    description,
                    user[0],
                    now.isoformat(),
                ),
            )
        self.audit(
            creator,
            "transactions",
            "create",
            "success",
            f"Created transfer {reference}",
            transaction_reference=reference,
        )
        result = self.get_transaction(reference, creator, read_all=False)
        if result is None:  # pragma: no cover - guarded by the insert above
            raise RuntimeError("created transaction is missing")
        return result

    def list_transactions(
        self, username: str, *, read_all: bool
    ) -> list[dict[str, object]]:
        query = self._transaction_select()
        parameters: tuple[object, ...] = ()
        if not read_all:
            query += " WHERE creator.username = ?"
            parameters = (username,)
        query += " ORDER BY transactions.id DESC"
        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [self._transaction_dict(row) for row in rows]

    def get_transaction(
        self, reference: str, username: str, *, read_all: bool
    ) -> dict[str, object] | None:
        query = self._transaction_select() + " WHERE transactions.reference = ?"
        parameters: tuple[object, ...] = (reference,)
        if not read_all:
            query += " AND creator.username = ?"
            parameters = (reference, username)
        with self._connect() as connection:
            row = connection.execute(query, parameters).fetchone()
        return self._transaction_dict(row) if row else None

    def approve_transaction(
        self, reference: str, approver: str
    ) -> dict[str, object]:
        now = datetime.now(UTC).replace(microsecond=0).isoformat()
        with self._connect() as connection:
            approver_row = connection.execute(
                "SELECT id FROM users WHERE username = ? AND status = 'active'",
                (approver,),
            ).fetchone()
            if approver_row is None:
                raise ValueError("unknown approver")
            exists = connection.execute(
                "SELECT status FROM transactions WHERE reference = ?", (reference,)
            ).fetchone()
            if exists is None:
                raise LookupError("transaction not found")
            if exists[0] != "pending":
                raise ValueError("transaction already processed")
            connection.execute(
                """UPDATE transactions
                   SET status = 'approved', approved_by = ?, approved_at = ?
                   WHERE reference = ? AND status = 'pending'""",
                (approver_row[0], now, reference),
            )
        self.audit(
            approver,
            "transactions",
            "approve",
            "success",
            f"Approved transfer {reference}",
            transaction_reference=reference,
        )
        result = self.get_transaction(reference, approver, read_all=True)
        if result is None:  # pragma: no cover - guarded by the update above
            raise RuntimeError("approved transaction is missing")
        return result

    def transaction_timeline(self, reference: str) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """SELECT id, created_at, username, role_at_event, resource, action,
                          outcome, transaction_reference, detail
                   FROM audit_logs
                   WHERE transaction_reference = ? ORDER BY id""",
                (reference,),
            ).fetchall()
        return [
            {
                "id": row[0],
                "created_at": row[1],
                "username": row[2],
                "role_at_event": row[3],
                "resource": row[4],
                "action": row[5],
                "outcome": row[6],
                "transaction_reference": row[7],
                "detail": row[8],
            }
            for row in rows
        ]

    def reset_demo(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """DELETE FROM sessions;
                DELETE FROM audit_logs;
                DELETE FROM transactions;
                DELETE FROM demo_settings;
                DELETE FROM customer_accounts;
                DELETE FROM role_permissions;
                DELETE FROM user_roles;
                DELETE FROM permissions;
                DELETE FROM roles;
                DELETE FROM users;"""
            )
        self.initialize()
        self._seed_demo()

    def _seed_demo(self) -> None:
        with self._connect() as connection:
            for role in ("administrator", "teller", "controller", "auditor"):
                connection.execute("INSERT INTO roles(name) VALUES (?)", (role,))
            permissions = (
                ("accounts", "read"),
                ("accounts", "update"),
                ("users", "manage"),
                ("audit_logs", "read"),
                ("transactions", "create"),
                ("transactions", "read_own"),
                ("transactions", "read_all"),
                ("transactions", "approve"),
                ("demo", "configure"),
            )
            for resource, action in permissions:
                connection.execute("INSERT INTO permissions(resource, action) VALUES (?, ?)", (resource, action))
            grants = {
                "administrator": (
                    ("accounts", "read"),
                    ("accounts", "update"),
                    ("users", "manage"),
                    ("audit_logs", "read"),
                    ("transactions", "read_all"),
                    ("demo", "configure"),
                ),
                "teller": (
                    ("accounts", "read"),
                    ("accounts", "update"),
                    ("transactions", "create"),
                    ("transactions", "read_own"),
                ),
                "controller": (
                    ("transactions", "read_all"),
                    ("transactions", "approve"),
                ),
                "auditor": (
                    ("accounts", "read"),
                    ("audit_logs", "read"),
                    ("transactions", "read_all"),
                ),
            }
            for role, role_permissions in grants.items():
                for resource, action in role_permissions:
                    connection.execute("""INSERT INTO role_permissions(role_id, permission_id)
                    SELECT roles.id, permissions.id FROM roles, permissions
                    WHERE roles.name = ? AND permissions.resource = ? AND permissions.action = ?""", (role, resource, action))
            connection.execute(
                "INSERT INTO demo_settings(key, value) VALUES ('security_mode', 'baseline')"
            )
        self.create_user("admin01", "Minh Trần", "Admin@123", "administrator")
        self.create_user(
            "controller01", "Hùng Phạm", "Controller@123", "controller"
        )
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
