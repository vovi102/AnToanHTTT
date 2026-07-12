# Hướng dẫn chạy lại demo thực nghiệm RBAC Guard

Tài liệu này hướng dẫn tái lập hai thực nghiệm trong bài báo:

1. **Baseline detection:** phát hiện SQL injection, password guessing và truy
   cập trái quyền trên 60 sự kiện tổng hợp.
2. **Context-risk:** bổ sung tín hiệu hành vi, sinh finding và gom cảnh báo
   thành incident trên 14 sự kiện tổng hợp.

Mọi lệnh bên dưới được chạy từ thư mục gốc của kho mã, tức thư mục chứa
`pyproject.toml`.

## 1. Yêu cầu

- Python 3.11 trở lên.
- `pip` và môi trường ảo Python.
- (Tùy chọn) LaTeX/`latexmk` nếu cần biên dịch bài báo.

Kiểm tra phiên bản Python:

```bash
python3.11 --version
```

## 2. Cài đặt môi trường

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e '.[dev]'
```

Xác nhận CLI đã sẵn sàng:

```bash
.venv/bin/rbac-guard --help
```

Nếu lệnh không tìm thấy `python3.11`, dùng trình thông dịch Python 3.11+ đang
có trên máy, ví dụ `python3`.

## 3. Kiểm tra trước khi demo

Chạy bộ kiểm thử hồi quy:

```bash
.venv/bin/pytest -q
```

Kết quả mong đợi tại checkpoint của bài báo là **65 passed**. Để kiểm tra cả
coverage của phần lõi:

```bash
.venv/bin/pytest -q --cov=rbac_guard --cov-report=term-missing --cov-fail-under=85
```

## 4. Khởi tạo RBAC và kiểm tra quyền

Tạo thư mục làm việc tạm cho một lần demo. Biến `DEMO_DIR` giúp các lần chạy
không ghi đè artifact gốc trong `paper/risk_based_access_monitoring/artifacts/`.

```bash
export DEMO_DIR="$(mktemp -d)"
echo "$DEMO_DIR"
.venv/bin/rbac-guard init-db --db "$DEMO_DIR/rbac.db" --seed data/rbac_seed.json
```

Kết quả mong đợi có dạng:

```text
Initialized RBAC database: .../rbac.db
```

Kiểm tra nhanh một quyền của người dùng mẫu:

```bash
.venv/bin/rbac-guard check-access \
  --db "$DEMO_DIR/rbac.db" \
  --user teller01 --resource accounts --action read
```

Kết quả mong đợi: `ALLOWED`.

## 5. Thực nghiệm 1 — Baseline detection

### 5.1 Chạy phân tích

```bash
.venv/bin/rbac-guard analyze \
  --db "$DEMO_DIR/rbac.db" \
  --log data/logs_demo.csv \
  --config config/default.toml \
  --output "$DEMO_DIR/baseline"
```

Kết quả mong đợi:

```text
Analyzed 60 valid events; 0 invalid rows; 20 alerts
```

### 5.2 Tính metric

```bash
.venv/bin/rbac-guard evaluate \
  --alerts "$DEMO_DIR/baseline/alerts.json" \
  --events data/logs_demo.csv \
  --output "$DEMO_DIR/baseline/metrics.json"
```

Kết quả mong đợi:

```text
Macro precision=1.0000; recall=0.9667; f1=0.9825
```

Các tệp kết quả cần có:

```bash
find "$DEMO_DIR/baseline" -maxdepth 1 -type f -printf '%f\n' | sort
```

```text
alerts.csv
alerts.json
metrics.json
run_metadata.json
```

Đọc metric mà không cần cài thêm công cụ:

```bash
.venv/bin/python -m json.tool "$DEMO_DIR/baseline/metrics.json"
```

Diễn giải ngắn: 60 sự kiện gồm dữ liệu lành tính và ba nhãn rủi ro; hệ thống
sinh 20 cảnh báo. Một mẫu SQL injection không khớp luật regex, nên recall macro
không đạt 1,0000. Đây là kết quả trên dữ liệu tổng hợp, không phải hiệu năng
vận hành thực tế.

## 6. Thực nghiệm 2 — Context-aware risk và incident grouping

Dùng cùng CSDL RBAC đã seed ở bước 4:

```bash
.venv/bin/rbac-guard analyze \
  --db "$DEMO_DIR/rbac.db" \
  --log data/logs_risk_demo.csv \
  --config config/default.toml \
  --output "$DEMO_DIR/context" \
  --context-risk
```

Kết quả mong đợi:

```text
Analyzed 14 valid events; 0 invalid rows; 15 alerts; 3 incidents
```

Kiểm tra các artifact:

```bash
find "$DEMO_DIR/context" -maxdepth 1 -type f -printf '%f\n' | sort
```

```text
alerts.csv
alerts.json
context_findings.json
incidents.csv
incidents.json
run_metadata.json
```

Xem finding và incident ở định dạng dễ đọc:

```bash
.venv/bin/python -m json.tool "$DEMO_DIR/context/context_findings.json"
.venv/bin/python -m json.tool "$DEMO_DIR/context/incidents.json"
```

Kết quả checkpoint mong đợi là 10 finding, gồm 6 `CTX-AFTER-HOURS`, 1
`CTX-NEW-IP`, 2 `CTX-RARE-RESOURCE` và 1 `CTX-REPEATED-DENIAL`; các cảnh báo
được gom thành 3 incident. Quy tắc nhóm dựa trên cặp người dùng--IP và cửa sổ
300 giây theo `config/default.toml`.

## 7. Đối chiếu với artifact của bài báo

Artifact đã được dùng để lập bảng trong bài báo nằm tại:

```text
paper/risk_based_access_monitoring/artifacts/cp3-baseline/
paper/risk_based_access_monitoring/artifacts/cp3-context/
```

Để so sánh kết quả vừa chạy với checkpoint, dùng lệnh sau; không sửa thủ công
JSON hoặc metric:

```bash
diff -u \
  paper/risk_based_access_monitoring/artifacts/cp3-baseline/metrics.json \
  "$DEMO_DIR/baseline/metrics.json"

.venv/bin/python - <<'PY'
import json
import os
from pathlib import Path

checkpoint = json.loads(Path(
    "paper/risk_based_access_monitoring/artifacts/cp3-context/run_metadata.json"
).read_text(encoding="utf-8"))
current = json.loads(
    (Path(os.environ["DEMO_DIR"]) / "context" / "run_metadata.json").read_text(
        encoding="utf-8"
    )
)
checkpoint.pop("run_at", None)
current.pop("run_at", None)
assert checkpoint == current, (checkpoint, current)
print("Context metadata matches (except run_at).")
PY
```

Không có đầu ra từ `diff` nghĩa là metric giống hệt nhau. Lệnh Python xác nhận
metadata giống nhau sau khi bỏ qua `run_at`, là thời điểm tạo report nên bắt
buộc khác giữa hai lần chạy. Tên thư mục tạm không ảnh hưởng đến số liệu.

## 8. Giao diện web tùy chọn

Cài phụ thuộc giao diện:

```bash
.venv/bin/pip install -e '.[web]'
.venv/bin/streamlit run src/rbac_guard/web.py
```

Trước khi nhấn **Analyze** trên giao diện, khởi tạo CSDL `demo.db` tại thư mục
gốc:

```bash
.venv/bin/rbac-guard init-db --db demo.db --seed data/rbac_seed.json
```

Sau đó tải `data/logs_demo.csv` cho baseline hoặc `data/logs_risk_demo.csv` và
bật **Context-aware risk analysis** cho thực nghiệm ngữ cảnh. Giao diện chỉ
đọc kết quả và không thay đổi dữ liệu RBAC hay luật phát hiện.

## 9. Biên dịch lại bài báo (tùy chọn)

Sau khi tái lập số liệu, biên dịch PDF từ thư mục bài báo:

```bash
cd paper/risk_based_access_monitoring
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

PDF tạo ra là `paper/risk_based_access_monitoring/main.pdf`.

## 10. Sự cố thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| `python3.11: command not found` | Cài Python 3.11+ hoặc thay bằng đường dẫn Python tương ứng. |
| `rbac-guard: no such file or directory` | Chạy lại bước cài đặt và dùng đúng `.venv/bin/rbac-guard`. |
| Lỗi thiếu bảng/`no such table` | Chạy lại `init-db` với `--seed data/rbac_seed.json` trước khi `analyze`. |
| Kết quả khác checkpoint | Kiểm tra đang dùng đúng hai file log, `config/default.toml`, CSDL vừa seed và có/không có `--context-risk` đúng bước. |
| `latexmk` không có | Cài một bộ TeX có `latexmk`; bước này không cần thiết để chạy demo chương trình. |

## 11. Dọn dẹp

Khi hoàn tất, xóa toàn bộ kết quả của lần chạy hiện tại:

```bash
rm -rf "$DEMO_DIR"
unset DEMO_DIR
```

Không dùng lệnh này nếu bạn đã thay `DEMO_DIR` bằng một thư mục chứa dữ liệu cần
giữ.
