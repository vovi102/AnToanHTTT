# RBAC Guard

PoC kiểm soát truy cập RBAC và phân tích log dựa trên luật để phát hiện SQL Injection, password guessing và truy cập trái quyền.

Hướng dẫn tái lập đầy đủ hai thực nghiệm baseline và context-risk: xem
[`HUONG_DAN_CHAY_DEMO.md`](HUONG_DAN_CHAY_DEMO.md).

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

## Chạy demo

```bash
.venv/bin/rbac-guard init-db --db demo.db --seed data/rbac_seed.json
.venv/bin/rbac-guard check-access --db demo.db --user teller01 --resource accounts --action read
.venv/bin/rbac-guard analyze --db demo.db --log data/logs_demo.csv --config config/default.toml --output artifacts
.venv/bin/rbac-guard evaluate --alerts artifacts/alerts.json --events data/logs_demo.csv --output artifacts/metrics.json
```

`analyze` tạo `alerts.csv`, `alerts.json` và `run_metadata.json`. `evaluate` tạo
`metrics.json` từ nhãn kỳ vọng trong dataset; không chỉnh sửa các artifact bằng tay.

## Demo nâng cấp: context-aware risk

Chạy phân tích rủi ro có ngữ cảnh hành vi:

```bash
.venv/bin/rbac-guard analyze --db demo.db --log data/logs_risk_demo.csv --config config/default.toml --output artifacts --context-risk
```

Chế độ này giữ các alert rule-based hiện có và sinh thêm
`context_findings.json`, `incidents.csv`, `incidents.json`. Dataset
`logs_risk_demo.csv` có các kịch bản IP lạ, ngoài giờ làm việc, truy cập tài
nguyên hiếm, repeated denials và chuỗi sự kiện cần gom thành incident.

## Cổng chất lượng lõi

```bash
.venv/bin/pytest -q --cov=rbac_guard --cov-report=term-missing --cov-fail-under=85
```

Coverage gate đo các module lõi; `cli.py` được kiểm tra qua subprocess test và
`web.py` qua helper test cùng smoke test Streamlit.

## Web UI tùy chọn

Sau khi cài extra `web`, khởi động giao diện chỉ đọc:

```bash
.venv/bin/pip install -e '.[web]'
.venv/bin/streamlit run src/rbac_guard/web.py
```

UI cho phép tải CSV/JSON, chạy cùng application service với CLI, lọc cảnh báo,
xem thống kê theo risk type/severity và tải kết quả. UI không chỉnh sửa RBAC hoặc luật.
Khi bật context-aware risk analysis, UI hiển thị thêm bảng incident và bộ lọc
theo user, risk type, severity và context signal.
