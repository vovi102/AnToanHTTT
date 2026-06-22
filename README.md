# RBAC Guard

PoC kiểm soát truy cập RBAC và phân tích log dựa trên luật để phát hiện SQL Injection, password guessing và truy cập trái quyền.

## Thiết lập

Yêu cầu Python 3.11 trở lên.

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e '.[dev]'
```

## Kiểm tra ban đầu

```bash
.venv/bin/pytest
.venv/bin/rbac-guard --help
```

Các lệnh vận hành và kịch bản demo sẽ được bổ sung cùng từng chức năng đã kiểm thử.

