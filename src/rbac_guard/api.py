"""HTTP API for the interactive BankSafe RBAC demonstration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rbac_guard.rbac import RBACRepository


DATABASE_PATH = Path(os.environ.get("RBAC_DEMO_DB", "demo-rbac.db"))
repository = RBACRepository(DATABASE_PATH)

app = FastAPI(title="BankSafe RBAC API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("RBAC_WEB_ORIGIN", "http://localhost:3000")],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    password: str = Field(min_length=8, max_length=128)


class CreateUserRequest(BaseModel):
    username: str = Field(pattern=r"^[a-zA-Z0-9_.-]{3,40}$")
    display_name: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(min_length=3, max_length=40)


class AccountUpdateRequest(BaseModel):
    phone: str = Field(min_length=6, max_length=30)
    address: str = Field(min_length=4, max_length=160)


class SecurityModeRequest(BaseModel):
    mode: Literal["baseline", "rbac"]


class CreateTransactionRequest(BaseModel):
    source_account: str = Field(pattern=r"^[0-9]{10,20}$")
    destination_account: str = Field(pattern=r"^[0-9]{10,20}$")
    beneficiary_name: str = Field(min_length=2, max_length=80)
    amount_vnd: int = Field(gt=0, le=10_000_000_000)
    description: str = Field(min_length=3, max_length=160)


@app.on_event("startup")
def bootstrap_demo() -> None:
    repository.initialize()
    if "administrator" not in repository.list_roles() or not any(user["username"] == "admin01" for user in repository.list_users()):
        repository.reset_demo()


def current_user(authorization: Annotated[str | None, Header()] = None) -> dict[str, str]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Phiên đăng nhập không hợp lệ")
    user = repository.session_user(authorization.removeprefix("Bearer "))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Phiên đăng nhập không hợp lệ")
    return user


CurrentUser = Annotated[dict[str, str], Depends(current_user)]


def require_permission(resource: str, action: str):
    def check(user: CurrentUser) -> dict[str, str]:
        if not repository.has_permission(user["username"], resource, action):
            repository.audit(user["username"], resource, action, "denied", "RBAC denied request")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"message": "RBAC từ chối thao tác", "permission": f"{resource}:{action}"},
            )
        repository.audit(user["username"], resource, action, "allowed", "RBAC allowed request")
        return user

    return check


def authorized(resource: str, action: str):
    return Annotated[dict[str, str], Depends(require_permission(resource, action))]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "database": str(DATABASE_PATH)}


@app.post("/auth/login")
def login(payload: LoginRequest) -> dict[str, object]:
    user = repository.authenticate(payload.username, payload.password)
    if user is None:
        repository.audit(payload.username, "session", "login", "failed", "Invalid username or password")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai tên đăng nhập hoặc mật khẩu")
    token = repository.create_session(int(user["id"]))
    repository.audit(user["username"], "session", "login", "success", "Password verified")
    return {"token": token, "user": {**user, "roles": repository.user_roles(user["username"])}}


@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(user: CurrentUser, authorization: Annotated[str | None, Header()] = None) -> Response:
    repository.delete_session((authorization or "").removeprefix("Bearer "))
    repository.audit(user["username"], "session", "logout", "success", "Session ended")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/auth/me")
def me(user: CurrentUser) -> dict[str, object]:
    return {**user, "roles": repository.user_roles(user["username"])}


@app.get("/roles")
def roles(user: authorized("users", "manage")) -> list[str]:
    return repository.list_roles()


@app.get("/users")
def users(user: authorized("users", "manage")) -> list[dict[str, object]]:
    return repository.list_users()


@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(payload: CreateUserRequest, user: authorized("users", "manage")) -> dict[str, object]:
    try:
        repository.create_user(payload.username, payload.display_name, payload.password, payload.role)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    repository.audit(user["username"], "users", "manage", "success", f"Created {payload.username} with role {payload.role}")
    return {"username": payload.username, "display_name": payload.display_name, "role": payload.role}


@app.get("/accounts")
def accounts(user: authorized("accounts", "read")) -> list[dict[str, object]]:
    return repository.list_accounts()


@app.patch("/accounts/{account_id}")
def update_account(account_id: int, payload: AccountUpdateRequest, user: authorized("accounts", "update")) -> dict[str, object]:
    if not repository.update_account(account_id, payload.phone, payload.address):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản khách hàng")
    repository.audit(user["username"], "accounts", "update", "success", f"Updated customer account {account_id}")
    return {"id": account_id, "phone": payload.phone, "address": payload.address}


@app.get("/audit-logs")
def audit_logs(user: authorized("audit_logs", "read")) -> list[dict[str, object]]:
    return repository.list_audit_logs()


@app.get("/demo/security-mode")
def get_security_mode(user: CurrentUser) -> dict[str, str]:
    return {"mode": repository.security_mode()}


@app.patch("/demo/security-mode")
def set_security_mode(
    payload: SecurityModeRequest, user: authorized("demo", "configure")
) -> dict[str, str]:
    repository.set_security_mode(payload.mode, user["username"])
    return {"mode": payload.mode}


def transaction_read_scope(user: dict[str, str]) -> bool:
    username = user["username"]
    if repository.has_permission(username, "transactions", "read_all"):
        return True
    if repository.has_permission(username, "transactions", "read_own"):
        return False
    repository.audit(
        username,
        "transactions",
        "read",
        "denied",
        "RBAC denied transaction read",
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "message": "RBAC từ chối thao tác",
            "permission": "transactions:read_own",
        },
    )


@app.post("/transactions", status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: CreateTransactionRequest,
    user: authorized("transactions", "create"),
) -> dict[str, object]:
    return repository.create_transaction(
        creator=user["username"],
        source_account=payload.source_account,
        destination_account=payload.destination_account,
        beneficiary_name=payload.beneficiary_name,
        amount_vnd=payload.amount_vnd,
        description=payload.description,
    )


@app.get("/transactions")
def transactions(user: CurrentUser) -> list[dict[str, object]]:
    read_all = transaction_read_scope(user)
    repository.audit(
        user["username"],
        "transactions",
        "read",
        "allowed",
        "RBAC allowed transaction list",
    )
    return repository.list_transactions(user["username"], read_all=read_all)


def readable_transaction(reference: str, user: dict[str, str]) -> dict[str, object]:
    read_all = transaction_read_scope(user)
    transaction = repository.get_transaction(
        reference, user["username"], read_all=read_all
    )
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy giao dịch",
        )
    return transaction


@app.get("/transactions/{reference}")
def transaction_detail(reference: str, user: CurrentUser) -> dict[str, object]:
    return readable_transaction(reference, user)


@app.get("/transactions/{reference}/timeline")
def transaction_timeline(
    reference: str, user: CurrentUser
) -> list[dict[str, object]]:
    readable_transaction(reference, user)
    return repository.transaction_timeline(reference)


@app.post("/transactions/{reference}/approve")
def approve_transaction(reference: str, user: CurrentUser) -> dict[str, object]:
    username = user["username"]
    if repository.has_permission(username, "transactions", "approve"):
        repository.audit(
            username,
            "transactions",
            "approve",
            "allowed",
            "RBAC allowed transaction approval",
            transaction_reference=reference,
        )
    elif (
        repository.security_mode() == "baseline"
        and "teller" in repository.user_roles(username)
    ):
        repository.audit(
            username,
            "transactions",
            "approve",
            "baseline_bypass",
            "Baseline mode bypassed the approval permission",
            transaction_reference=reference,
        )
    else:
        repository.audit(
            username,
            "transactions",
            "approve",
            "denied",
            "RBAC denied transaction approval",
            transaction_reference=reference,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "RBAC từ chối tự phê duyệt giao dịch",
                "permission": "transactions:approve",
            },
        )
    try:
        return repository.approve_transaction(reference, username)
    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy giao dịch",
        ) from error
    except ValueError as error:
        repository.audit(
            username,
            "transactions",
            "approve",
            "conflict",
            str(error),
            transaction_reference=reference,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Giao dịch đã được xử lý trước đó",
        ) from error


@app.post("/demo/reset")
def reset_demo(user: authorized("users", "manage")) -> dict[str, str]:
    repository.reset_demo()
    return {"message": "Đã đặt lại dữ liệu demo. Vui lòng đăng nhập lại bằng admin01."}
