# CHƯƠNG 4. TRIỂN KHAI DEMO

## 4.1. Môi trường và cấu trúc

PoC sử dụng Python 3.11, SQLite trong thư viện chuẩn, pytest/coverage cho kiểm thử và Streamlit/pandas cho UI tùy chọn. Package được khai báo trong `pyproject.toml`; entry point `rbac-guard` trỏ tới `rbac_guard.cli:main`.

## 4.2. Dữ liệu giả lập

`data/rbac_seed.json` chứa bốn user, ba role, bốn permission và các quan hệ gán mẫu. `data/logs_demo.csv` có 60 event: 30 benign, 10 SQL Injection, 10 password guessing và 10 unauthorized access. `logs_demo.json` cung cấp mẫu tương đương schema để kiểm tra nhánh JSON.

## 4.3. Các lệnh chính

```bash
rbac-guard init-db --db demo.db --seed data/rbac_seed.json
rbac-guard check-access --db demo.db --user teller01 --resource accounts --action read
rbac-guard analyze --db demo.db --log data/logs_demo.csv --config config/default.toml --output artifacts
rbac-guard evaluate --alerts artifacts/alerts.json --events data/logs_demo.csv --output artifacts/metrics.json
```

Lần chạy thực nghiệm đọc đủ 60 event hợp lệ, không có dòng lỗi và sinh 20 Alert. Alert ID được băm ổn định từ rule ID và event IDs, nhờ đó cùng input và rule tạo cùng định danh.

## 4.4. Web UI

Streamlit UI cho phép tải CSV/JSON, nhập đường dẫn database/config, chạy analysis, lọc theo risk type/severity, xem hai biểu đồ đếm và tải CSV/JSON. UI không quản trị RBAC hoặc sửa luật; test helper xác nhận lọc và nhóm dữ liệu, còn smoke test headless xác nhận server khởi động.

## 4.5. Chất lượng mã

Từng chức năng được triển khai theo chu trình test thất bại trước, implementation tối thiểu và chạy lại toàn suite. Tại thời điểm đóng băng lõi, 48 test đạt coverage 86.08%; sau khi thêm UI, toàn bộ 50 test pass.

