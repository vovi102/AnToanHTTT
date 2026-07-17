# RBAC Guard

PoC kiểm soát truy cập RBAC và phân tích log dựa trên luật để phát hiện SQL Injection, password guessing và truy cập trái quyền.

Hướng dẫn tái lập đầy đủ hai thực nghiệm baseline và context-risk: xem
[`HUONG_DAN_CHAY_DEMO.md`](HUONG_DAN_CHAY_DEMO.md).

## Thiết lập

Yêu cầu Python 3.11 trở lên.

```bash
uv sync
```

`uv` tự tạo và quản lý môi trường `.venv` cùng các phiên bản phụ thuộc đã
khóa trong `uv.lock`. Nếu chưa có `uv`, cài theo hướng dẫn tại
<https://docs.astral.sh/uv/getting-started/installation/>.

## Kiểm tra ban đầu

```bash
uv run pytest
uv run rbac-guard --help
```

## Chạy demo

```bash
uv run rbac-guard init-db --db demo.db --seed data/rbac_seed.json
uv run rbac-guard check-access --db demo.db --user teller01 --resource accounts --action read
uv run rbac-guard analyze --db demo.db --log data/logs_demo.csv --config config/default.toml --output artifacts
uv run rbac-guard evaluate --alerts artifacts/alerts.json --events data/logs_demo.csv --output artifacts/metrics.json
```

`analyze` tạo `alerts.csv`, `alerts.json` và `run_metadata.json`. `evaluate` tạo
`metrics.json` từ nhãn kỳ vọng trong dataset; không chỉnh sửa các artifact bằng tay.

## Demo nâng cấp: context-aware risk

Chạy phân tích rủi ro có ngữ cảnh hành vi:

```bash
uv run rbac-guard analyze --db demo.db --log data/logs_risk_demo.csv --config config/default.toml --output artifacts --context-risk
```

Chế độ này giữ các alert rule-based hiện có và sinh thêm
`context_findings.json`, `incidents.csv`, `incidents.json`. Dataset
`logs_risk_demo.csv` có các kịch bản IP lạ, ngoài giờ làm việc, truy cập tài
nguyên hiếm, repeated denials và chuỗi sự kiện cần gom thành incident.

## Cổng chất lượng lõi

```bash
uv run pytest -q --cov=rbac_guard --cov-report=term-missing --cov-fail-under=85
```

Coverage gate đo các module lõi; `cli.py` được kiểm tra qua subprocess test và
`web.py` qua helper test cùng smoke test Streamlit.

## Demo nghiệp vụ RBAC Nova Bank (Next.js)

Demo gồm Next.js và FastAPI/SQLite thật: **Admin tạo Teller → Teller tạo giao
dịch 50 triệu → so sánh trước/sau RBAC → Controller phê duyệt**.

Với Kiểm soát cơ bản, Teller tạo rồi hoàn tất giao dịch đầu tiên. Sau khi Admin
áp dụng Phân tách nhiệm vụ, Teller truy cập trực tiếp trang phê duyệt và bị từ
chối; Controller phê duyệt thành công.

Hướng dẫn khởi động, dữ liệu mẫu, kịch bản 5–7 phút và xử lý sự cố nằm tại
[`DEMO_RBAC_NOVA_BANK.md`](DEMO_RBAC_NOVA_BANK.md).

## Giao diện phân tích log tùy chọn

Streamlit cung cấp giao diện riêng cho phần phân tích log kỹ thuật:

```bash
uv sync --no-dev --extra web
uv run --no-dev --extra web streamlit run src/rbac_guard/web.py
```
