# RBAC and Rule-based Log Analysis PoC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây dựng PoC Python CLI dùng SQLite RBAC và luật xác định trước để phát hiện SQL Injection, password guessing, truy cập trái quyền; sinh số liệu thực nghiệm và báo cáo sáu chương trong ba tuần.

**Architecture:** Mã nguồn tách thành domain model, SQLite repository, parser, detection rules, scoring, reporting và application service. CLI bắt buộc và Streamlit tùy chọn chỉ gọi application service, nên toàn bộ logic lõi được kiểm thử độc lập và dùng chung.

**Tech Stack:** Python 3.11+, thư viện chuẩn (`argparse`, `csv`, `json`, `sqlite3`, `dataclasses`, `tomllib`), pytest, coverage; Streamlit và pandas chỉ cài nếu đạt cổng triển khai UI.

---

## 1. Cấu trúc file

```text
AnToanHTTT/
├── pyproject.toml                    # package, pytest và command-line entry point
├── README.md                         # cài đặt, lệnh chạy và demo
├── config/default.toml               # ngưỡng detection/scoring duy nhất
├── data/
│   ├── rbac_seed.json                # user, role, permission mẫu
│   ├── logs_demo.csv                 # tập log demo có nhãn
│   └── logs_demo.json                # cùng schema để kiểm tra JSON parser
├── src/rbac_guard/
│   ├── __init__.py
│   ├── models.py                     # Event, Finding, Alert, RunMetadata
│   ├── config.py                     # đọc/kiểm tra TOML
│   ├── rbac.py                       # schema, seed và has_permission
│   ├── parser.py                     # CSV/JSON -> Event + RowError
│   ├── rules.py                      # ba nhóm luật và DetectionEngine
│   ├── scoring.py                    # điểm 0..100 và severity
│   ├── reporting.py                  # alert/metadata CSV/JSON
│   ├── metrics.py                    # confusion matrix và metric
│   ├── service.py                    # orchestration của một lần phân tích
│   ├── cli.py                        # init-db, check-access, analyze, evaluate
│   └── web.py                        # Streamlit tùy chọn
├── tests/
│   ├── fixtures/                     # database/log nhỏ cho test
│   ├── test_config.py
│   ├── test_rbac.py
│   ├── test_parser.py
│   ├── test_rules.py
│   ├── test_scoring.py
│   ├── test_reporting.py
│   ├── test_metrics.py
│   ├── test_service.py
│   └── test_cli.py
├── artifacts/                        # đầu ra tái sinh, không sửa thủ công
│   ├── alerts.csv
│   ├── alerts.json
│   ├── run_metadata.json
│   └── metrics.json
└── report/
    ├── 01-introduction.md
    ├── 02-foundations.md
    ├── 03-system-design.md
    ├── 04-implementation.md
    ├── 05-experiments.md
    ├── 06-conclusion.md
    └── figures/                      # sơ đồ và ảnh CLI/UI
```

## 2. Lịch và trách nhiệm

| Ngày | Đầu ra bắt buộc | Thực hiện chính | Review |
|---|---|---|---|
| 22–23/06 | Task 1–2: nền dự án, model/config | Cả nhóm | Kiểm tra chéo |
| 24–25/06 | Task 3: SQLite RBAC | Vi Đăng Khoa | Vũ Trọng Quảng |
| 26–27/06 | Task 4: dữ liệu và parser | Vũ Trọng Quảng | Vi Đăng Khoa |
| 28–30/06 | Task 5–6: SQLi và password guessing | Quảng / Khoa | Kiểm tra chéo |
| 01–02/07 | Task 7–8: unauthorized, scoring, report | Quảng / Khoa | Kiểm tra chéo |
| 03–04/07 | Task 9–10: CLI, integration, metric | Cả nhóm | Cả nhóm |
| 05/07 | Đóng băng lõi; quyết định Streamlit | Cả nhóm | Cả nhóm |
| 06–11/07 | Task 12: báo cáo sáu chương | Theo `Khung_bao_cao.md` | Kiểm tra chéo |
| 12/07 | Task 13: tái chạy, rà soát, đóng gói | Cả nhóm | Cả nhóm |

Không bắt đầu Task 11 nếu Task 10 chưa pass toàn bộ hoặc muộn hơn ngày 05/07/2026.

### Tiến độ thực thi

- [x] Task 1: Khởi tạo repository và môi trường tái lập
- [x] Task 2: Domain model và cấu hình duy nhất
- [x] Task 3: SQLite RBAC repository và checker
- [x] Task 4: Dataset có nhãn và parser CSV/JSON
- [x] Task 5: Luật SQL Injection
- [x] Task 6: Luật password guessing theo sliding window
- [x] Task 7: Unauthorized access và DetectionEngine
- [x] Task 8: Risk scoring và alert reporter
- [x] Task 9: Application service và CLI end-to-end
- [x] Task 10: Metrics, scenario suite và cổng đóng băng lõi
- [x] Task 11: Streamlit UI tối giản — mục tiêu phụ có điều kiện
- [x] Task 12: Viết báo cáo từ bằng chứng đã đóng băng
- [x] Task 13: Tái lập, rà soát và đóng gói bài nộp

## 3. Kế hoạch thực hiện

### Task 1: Khởi tạo repository và môi trường tái lập

**Phụ trách:** Cả nhóm  
**Files:** Create `pyproject.toml`, `.gitignore`, `README.md`, `src/rbac_guard/__init__.py`

- [ ] **Step 1: Khởi tạo Git và cây thư mục**

Run:

```bash
git init
mkdir -p config data artifacts report/figures src/rbac_guard tests/fixtures
```

Expected: `git status --short` nhận diện workspace và chưa có file được track.

- [ ] **Step 2: Khai báo package và test runner**

Tạo `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "rbac-guard"
version = "0.1.0"
requires-python = ">=3.11"

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-cov>=5"]
web = ["streamlit>=1.35", "pandas>=2.2"]

[project.scripts]
rbac-guard = "rbac_guard.cli:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --strict-markers"
```

- [ ] **Step 3: Tạo `.gitignore` và hướng dẫn smoke test**

`.gitignore` phải bỏ qua `.venv/`, `__pycache__/`, `.pytest_cache/`, `.coverage`, `*.db` và `artifacts/*`, nhưng giữ `artifacts/.gitkeep`. `README.md` ghi lệnh cài `python -m venv .venv`, `pip install -e '.[dev]'`, `pytest` và `rbac-guard --help`.

- [ ] **Step 4: Cài môi trường và kiểm chứng entry point**

Run:

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -c "import rbac_guard"
```

Expected: import thành công, exit code 0.

- [ ] **Step 5: Commit nền dự án**

```bash
git add pyproject.toml .gitignore README.md src/rbac_guard/__init__.py artifacts/.gitkeep
git commit -m "chore: initialize rbac guard project"
```

### Task 2: Domain model và cấu hình duy nhất

**Phụ trách:** Cả nhóm  
**Files:** Create `src/rbac_guard/models.py`, `src/rbac_guard/config.py`, `config/default.toml`, `tests/test_config.py`

- [ ] **Step 1: Viết test cấu hình thất bại trước**

```python
from pathlib import Path
import pytest
from rbac_guard.config import load_config

def test_load_config_rejects_overlapping_severity_thresholds(tmp_path: Path):
    path = tmp_path / "bad.toml"
    path.write_text("[severity]\nmedium=40\nhigh=30\ncritical=80\n", encoding="utf-8")
    with pytest.raises(ValueError, match="medium < high < critical"):
        load_config(path)
```

- [ ] **Step 2: Chạy test để xác nhận RED**

Run: `.venv/bin/pytest tests/test_config.py -q`  
Expected: FAIL do `rbac_guard.config` chưa tồn tại.

- [ ] **Step 3: Định nghĩa model và config tối thiểu**

`models.py` định nghĩa dataclass bất biến `Event`, `RowError`, `Finding`, `Alert`, `RunMetadata`; mọi finding có `rule_id`, `risk_type`, `event_ids`, `evidence`, `confidence`, `repeat_count`, `rbac_denied`.

`config.py` định nghĩa:

```python
@dataclass(frozen=True)
class AppConfig:
    password_failures: int
    password_window_seconds: int
    medium: int
    high: int
    critical: int

def load_config(path: Path) -> AppConfig:
    # đọc tomllib; yêu cầu failures > 1, window > 0,
    # và 0 < medium < high < critical <= 100
```

`config/default.toml` dùng `failures = 5`, `window_seconds = 300`, severity `medium = 30`, `high = 60`, `critical = 85`.

- [ ] **Step 4: Bổ sung test happy path và chạy GREEN**

Assert file mặc định sinh `AppConfig(5, 300, 30, 60, 85)`.

Run: `.venv/bin/pytest tests/test_config.py -q`  
Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add config/default.toml src/rbac_guard/models.py src/rbac_guard/config.py tests/test_config.py
git commit -m "feat: define domain models and validated config"
```

### Task 3: SQLite RBAC repository và checker

**Phụ trách:** Vi Đăng Khoa; **Review:** Vũ Trọng Quảng  
**Files:** Create `src/rbac_guard/rbac.py`, `data/rbac_seed.json`, `tests/test_rbac.py`

- [ ] **Step 1: Viết test ma trận quyền**

```python
def test_permission_matrix(seed_db):
    checker = RBACRepository(seed_db)
    assert checker.has_permission("teller01", "accounts", "read") is True
    assert checker.has_permission("teller01", "users", "delete") is False
    assert checker.has_permission("disabled01", "accounts", "read") is False
    assert checker.has_permission("missing", "accounts", "read") is False
```

- [ ] **Step 2: Chạy RED**

Run: `.venv/bin/pytest tests/test_rbac.py -q`  
Expected: FAIL do `RBACRepository` chưa tồn tại.

- [ ] **Step 3: Triển khai schema, seed và lookup**

`rbac.py` cung cấp đúng các hàm:

```python
class RBACRepository:
    def __init__(self, db_path: Path): ...
    def initialize(self) -> None: ...
    def seed(self, seed_path: Path) -> None: ...
    def has_permission(self, username: str, resource: str, action: str) -> bool: ...
```

Schema bật `PRAGMA foreign_keys=ON`, dùng unique constraint theo đặc tả và transaction cho seed. Query quyền bắt buộc lọc `users.status = 'active'`.

- [ ] **Step 4: Test ràng buộc và rollback**

Thêm test seed lặp không tạo bản ghi trùng và seed có khóa ngoại sai rollback toàn bộ transaction.

Run: `.venv/bin/pytest tests/test_rbac.py -q`  
Expected: toàn bộ test pass.

- [ ] **Step 5: Commit**

```bash
git add src/rbac_guard/rbac.py data/rbac_seed.json tests/test_rbac.py
git commit -m "feat: implement sqlite rbac authorization"
```

### Task 4: Dataset có nhãn và parser CSV/JSON

**Phụ trách:** Vũ Trọng Quảng; **Review:** Vi Đăng Khoa  
**Files:** Create `src/rbac_guard/parser.py`, `data/logs_demo.csv`, `data/logs_demo.json`, `tests/test_parser.py`, `tests/fixtures/invalid_rows.csv`

- [ ] **Step 1: Viết test CSV/JSON cho cùng output**

```python
def test_csv_and_json_normalize_to_same_events(csv_log, json_log):
    csv_result = parse_events(csv_log)
    json_result = parse_events(json_log)
    assert csv_result.events == json_result.events
    assert csv_result.errors == ()
```

- [ ] **Step 2: Chạy RED**

Run: `.venv/bin/pytest tests/test_parser.py -q`  
Expected: FAIL do `parse_events` chưa tồn tại.

- [ ] **Step 3: Triển khai parser theo suffix**

```python
@dataclass(frozen=True)
class ParseResult:
    events: tuple[Event, ...]
    errors: tuple[RowError, ...]

def parse_events(path: Path) -> ParseResult:
    # .csv dùng csv.DictReader; .json yêu cầu JSON array;
    # validate header và event_type; cô lập timestamp/row lỗi
```

Thiếu file, suffix khác `.csv/.json`, JSON không phải array hoặc thiếu trường bắt buộc phải raise `InputFileError`. Dòng riêng lẻ lỗi được đưa vào `errors`.

- [ ] **Step 4: Tạo dataset đánh giá cân bằng có chủ đích**

Tạo tối thiểu 60 event: ít nhất 10 benign, 10 SQLi, 10 failed-login thuộc burst, 10 failed-login không vượt ngưỡng, 10 allowed access và 10 unauthorized access. Mỗi dòng có `event_id` duy nhất và `expected_label` thuộc `benign`, `sql_injection`, `password_guessing`, `unauthorized_access`.

- [ ] **Step 5: Chạy test parser và kiểm tra số nhãn**

Run:

```bash
.venv/bin/pytest tests/test_parser.py -q
.venv/bin/python -c "from pathlib import Path; from rbac_guard.parser import parse_events; e=parse_events(Path('data/logs_demo.csv')).events; assert len(e)>=60; print(len(e))"
```

Expected: tests pass và in số từ 60 trở lên.

- [ ] **Step 6: Commit**

```bash
git add src/rbac_guard/parser.py data/logs_demo.csv data/logs_demo.json tests/test_parser.py tests/fixtures/invalid_rows.csv
git commit -m "feat: add labeled log datasets and parsers"
```

### Task 5: Luật SQL Injection

**Phụ trách:** Vũ Trọng Quảng; **Review:** Vi Đăng Khoa  
**Files:** Create `src/rbac_guard/rules.py`, `tests/test_rules.py`

- [ ] **Step 1: Viết test dương tính và âm tính**

```python
@pytest.mark.parametrize("request", [
    "' OR 1=1 --", "1 UNION SELECT password FROM users", "1; DROP TABLE users"
])
def test_sqli_rule_detects_supported_patterns(request, event_factory):
    findings = SQLInjectionRule().evaluate((event_factory(request=request),))
    assert len(findings) == 1
    assert findings[0].risk_type == "sql_injection"

def test_sqli_rule_ignores_normal_search(event_factory):
    assert SQLInjectionRule().evaluate((event_factory(request="select account type"),)) == ()
```

- [ ] **Step 2: Chạy RED, sau đó triển khai rule**

`SQLInjectionRule` dùng regex compile sẵn, case-insensitive, mã luật riêng cho tautology, comment, union-select và stacked query. Evidence lưu tên pattern và excerpt tối đa 160 ký tự, không lưu toàn bộ payload không giới hạn.

- [ ] **Step 3: Chạy GREEN và coverage mục tiêu**

Run: `.venv/bin/pytest tests/test_rules.py -q --cov=rbac_guard.rules --cov-report=term-missing`  
Expected: test pass; mọi nhánh pattern và benign case được chạy.

- [ ] **Step 4: Commit**

```bash
git add src/rbac_guard/rules.py tests/test_rules.py
git commit -m "feat: detect explainable sql injection patterns"
```

### Task 6: Luật password guessing theo sliding window

**Phụ trách:** Vi Đăng Khoa; **Review:** Vũ Trọng Quảng  
**Files:** Modify `src/rbac_guard/rules.py`, `tests/test_rules.py`

- [ ] **Step 1: Viết test biên cửa sổ thời gian**

Test 5 lần fail cùng IP/user trong đúng 300 giây tạo một finding; 4 lần không tạo; 5 lần trải quá 300 giây không tạo; một lần success làm kết thúc chuỗi trước đó; event được đưa vào theo thứ tự lộn xộn vẫn cho cùng kết quả.

- [ ] **Step 2: Chạy RED**

Run: `.venv/bin/pytest tests/test_rules.py -q`  
Expected: FAIL ở password guessing cases.

- [ ] **Step 3: Triển khai bằng deque theo khóa `(user, ip)`**

```python
class PasswordGuessingRule:
    def __init__(self, failures: int, window_seconds: int): ...
    def evaluate(self, events: tuple[Event, ...]) -> tuple[Finding, ...]: ...
```

Sắp xếp theo timestamp, chỉ nhận authentication/failed, loại event cũ khỏi deque và không tạo finding trùng cho cùng burst. Evidence chứa count, first/last timestamp và khóa nhóm.

- [ ] **Step 4: Chạy GREEN và commit**

Run: `.venv/bin/pytest tests/test_rules.py -q`  
Expected: tất cả test rule pass.

```bash
git add src/rbac_guard/rules.py tests/test_rules.py
git commit -m "feat: detect password guessing in time windows"
```

### Task 7: Unauthorized access và DetectionEngine

**Phụ trách:** Vũ Trọng Quảng; **Review:** Vi Đăng Khoa  
**Files:** Modify `src/rbac_guard/rules.py`, `tests/test_rules.py`

- [ ] **Step 1: Viết test đối chiếu RBAC**

Test phải bao phủ: quyền hợp lệ không cảnh báo; thiếu quyền cảnh báo; user inactive cảnh báo; status `denied` cảnh báo dù request không thành công; authentication event bị bỏ qua.

- [ ] **Step 2: Chạy RED và triển khai dependency injection**

```python
class UnauthorizedAccessRule:
    def __init__(self, checker: Protocol): ...
    def evaluate(self, events: tuple[Event, ...]) -> tuple[Finding, ...]: ...

class DetectionEngine:
    def __init__(self, rules: tuple[DetectionRule, ...]): ...
    def detect(self, events: tuple[Event, ...]) -> tuple[Finding, ...]: ...
```

`DetectionRule` protocol yêu cầu `evaluate(events)`. Engine hợp nhất findings theo thứ tự timestamp, risk type, rule id để output ổn định.

- [ ] **Step 3: Chạy toàn bộ rule tests**

Run: `.venv/bin/pytest tests/test_rules.py tests/test_rbac.py -q`  
Expected: pass.

- [ ] **Step 4: Commit**

```bash
git add src/rbac_guard/rules.py tests/test_rules.py
git commit -m "feat: detect unauthorized access through rbac"
```

### Task 8: Risk scoring và alert reporter

**Phụ trách:** Vi Đăng Khoa; **Review:** Vũ Trọng Quảng  
**Files:** Create `src/rbac_guard/scoring.py`, `src/rbac_guard/reporting.py`, `tests/test_scoring.py`, `tests/test_reporting.py`

- [ ] **Step 1: Viết scoring test tại các biên**

```python
@pytest.mark.parametrize(("score", "expected"), [
    (0, "Low"), (29, "Low"), (30, "Medium"),
    (59, "Medium"), (60, "High"), (84, "High"),
    (85, "Critical"), (100, "Critical")
])
def test_severity_boundaries(scorer, score, expected):
    assert scorer.severity(score) == expected
```

- [ ] **Step 2: Chạy RED và triển khai scorer thuần**

Điểm nền: SQLi 45, password guessing 40, unauthorized 50; cộng tối đa 20 theo confidence, tối đa 15 theo repeat count và 15 nếu `rbac_denied`; clamp 0–100. Công thức và các ngưỡng nằm ở một nơi, alert id sinh ổn định từ rule/event ids.

- [ ] **Step 3: Viết reporter test trước**

Test zero-alert vẫn tạo `alerts.csv` có header, `alerts.json` là `[]`, metadata có `alert_count: 0`; test có alert xác nhận CSV/JSON cùng số record và các trường bắt buộc.

- [ ] **Step 4: Triển khai atomic output**

```python
def write_reports(output_dir: Path, alerts: tuple[Alert, ...], metadata: RunMetadata) -> None:
    # ghi file .tmp cùng thư mục rồi Path.replace sang tên chính thức
```

- [ ] **Step 5: Chạy GREEN và commit**

Run: `.venv/bin/pytest tests/test_scoring.py tests/test_reporting.py -q`  
Expected: pass.

```bash
git add src/rbac_guard/scoring.py src/rbac_guard/reporting.py tests/test_scoring.py tests/test_reporting.py
git commit -m "feat: score risks and export reproducible alerts"
```

### Task 9: Application service và CLI end-to-end

**Phụ trách:** Cả nhóm  
**Files:** Create `src/rbac_guard/service.py`, `src/rbac_guard/cli.py`, `tests/test_service.py`, `tests/test_cli.py`

- [ ] **Step 1: Viết integration test cho service**

```python
def test_analyze_end_to_end(seed_db, labeled_log, tmp_path):
    result = analyze(seed_db, labeled_log, DEFAULT_CONFIG, tmp_path)
    assert result.metadata.valid_rows > 0
    assert {a.risk_type for a in result.alerts} == {
        "sql_injection", "password_guessing", "unauthorized_access"
    }
    assert (tmp_path / "alerts.csv").exists()
```

- [ ] **Step 2: Chạy RED và triển khai orchestration**

`analyze(db_path, log_path, config_path, output_dir) -> AnalysisResult` thực hiện đúng thứ tự parse → detect → score → report; clock được inject hoặc truyền vào để test metadata ổn định.

- [ ] **Step 3: Viết CLI test trước**

Dùng `subprocess.run` kiểm tra `init-db`, `check-access`, `analyze`; file sai trả code 2 và stderr không có traceback; lệnh hợp lệ trả code 0.

- [ ] **Step 4: Triển khai `argparse` commands**

```text
rbac-guard init-db --db PATH --seed data/rbac_seed.json
rbac-guard check-access --db PATH --user USER --resource RESOURCE --action ACTION
rbac-guard analyze --db PATH --log PATH --config config/default.toml --output artifacts
rbac-guard evaluate --alerts artifacts/alerts.json --events data/logs_demo.csv --output artifacts/metrics.json
```

- [ ] **Step 5: Chạy E2E thật**

```bash
.venv/bin/rbac-guard init-db --db /tmp/rbac-demo.db --seed data/rbac_seed.json
.venv/bin/rbac-guard analyze --db /tmp/rbac-demo.db --log data/logs_demo.csv --config config/default.toml --output artifacts
.venv/bin/pytest tests/test_service.py tests/test_cli.py -q
```

Expected: lệnh in số event/cảnh báo, tạo ba artifact và test pass.

- [ ] **Step 6: Commit**

```bash
git add src/rbac_guard/service.py src/rbac_guard/cli.py tests/test_service.py tests/test_cli.py
git commit -m "feat: add end-to-end analysis cli"
```

### Task 10: Metrics, scenario suite và cổng đóng băng lõi

**Phụ trách:** Cả nhóm  
**Files:** Create `src/rbac_guard/metrics.py`, `tests/test_metrics.py`; Modify `README.md`

- [ ] **Step 1: Viết test confusion matrix**

Với fixture 4 label gồm 2 positive, prediction gồm 1 TP và 1 FP, assert `tp=1, fp=1, fn=1, tn=1`, precision/recall/F1 đều `0.5`. Test lớp không có prediction không được chia cho 0.

- [ ] **Step 2: Chạy RED và triển khai metric không dùng sklearn**

```python
@dataclass(frozen=True)
class Metrics:
    tp: int; fp: int; fn: int; tn: int
    precision: float; recall: float; f1: float

def evaluate_labels(expected: set[str], predicted: set[str], universe: set[str]) -> Metrics: ...
```

Sinh metric riêng cho từng risk type và tổng hợp macro average; JSON ghi số đếm nguyên và metric làm tròn 4 chữ số.

- [ ] **Step 3: Chạy toàn bộ suite và coverage**

```bash
.venv/bin/pytest -q --cov=rbac_guard --cov-report=term-missing --cov-fail-under=85
.venv/bin/rbac-guard evaluate --alerts artifacts/alerts.json --events data/logs_demo.csv --output artifacts/metrics.json
```

Expected: tất cả test pass, coverage ≥85%, `metrics.json` có ba risk type.

- [ ] **Step 4: Review cổng ngày 05/07**

Chỉ đóng băng lõi khi: setup từ môi trường sạch chạy được; không test fail; output tái sinh được; mỗi loại rủi ro có positive/negative scenario; README chứa lệnh demo sao chép được. Nếu một điều kiện fail, bỏ Task 11 và dùng thời gian sửa lõi.

- [ ] **Step 5: Commit**

```bash
git add src/rbac_guard/metrics.py tests/test_metrics.py README.md artifacts/.gitkeep
git commit -m "test: validate scenarios and evaluation metrics"
```

### Task 11: Streamlit UI tối giản — mục tiêu phụ có điều kiện

**Phụ trách:** Vũ Trọng Quảng; **Review:** Vi Đăng Khoa  
**Files:** Create `src/rbac_guard/web.py`, `tests/test_web_helpers.py`; Modify `README.md`

- [ ] **Step 1: Ghi quyết định GO/NO-GO vào nhật ký tiến độ**

GO chỉ khi Task 10 hoàn tất không muộn hơn 05/07. NO-GO nghĩa là bỏ toàn bộ task này, không ảnh hưởng tiêu chí hoàn thành đề tài.

- [ ] **Step 2: Với GO, cài dependency web và viết test helper**

Test helper chuyển alerts thành rows, lọc theo `risk_type`/`severity`, đếm theo nhóm và không phụ thuộc runtime Streamlit.

Run: `.venv/bin/pip install -e '.[dev,web]' && .venv/bin/pytest tests/test_web_helpers.py -q`  
Expected trước implementation: FAIL.

- [ ] **Step 3: Triển khai UI chỉ gọi `service.analyze`**

UI có file uploader CSV/JSON, input đường dẫn DB, nút Analyze, bảng/filter, hai thống kê nhóm và download CSV/JSON. Catch lỗi đầu vào đã định nghĩa, hiển thị `st.error(str(exc))`; không hiển thị traceback và không viết logic regex/RBAC trong `web.py`.

- [ ] **Step 4: Smoke test thủ công**

Run: `.venv/bin/streamlit run src/rbac_guard/web.py`  
Expected: tải `data/logs_demo.csv`, phân tích và số alert khớp CLI.

- [ ] **Step 5: Commit**

```bash
git add src/rbac_guard/web.py tests/test_web_helpers.py README.md
git commit -m "feat: add optional streamlit alert viewer"
```

### Task 12: Viết báo cáo từ bằng chứng đã đóng băng

**Phụ trách:** Theo `Khung_bao_cao.md`; **Review:** kiểm tra chéo  
**Files:** Create `report/01-introduction.md` through `report/06-conclusion.md`, `report/figures/*`

- [ ] **Step 1: Chương 1 — Introduction, 06–07/07**

Phát triển đủ `[INTRO-00]` đến `[INTRO-15]`, mỗi nhãn tối thiểu một đoạn. Nội dung bám mục tiêu, phạm vi, yêu cầu, đầu ra và thảo luận trong đặc tả; không tuyên bố kết quả chưa có trong artifacts.

- [ ] **Step 2: Chương 2 — Foundations, 07/07**

Viết RBAC, security logs, SQL Injection và password guessing. Mỗi định nghĩa/khẳng định học thuật có nguồn; phân biệt lý thuyết tổng quát với lựa chọn thiết kế của PoC.

- [ ] **Step 3: Chương 3 — System Design, 08/07**

Sinh sơ đồ kiến trúc, ERD năm bảng, sequence log → alert, bảng rule id và bảng scoring trực tiếp từ code/config đã đóng băng. Kiểm tra tên trường trong báo cáo khớp `models.py` và SQLite schema.

- [ ] **Step 4: Chương 4 — Implementation, 09/07**

Trình bày môi trường, cấu trúc module, dataset, CLI, RBAC checker, detection và alert output. Dùng excerpt ngắn; dẫn đường dẫn file và command thay vì sao chép toàn bộ mã.

- [ ] **Step 5: Chương 5 — Experiments, 10/07**

Ghi cấu hình thí nghiệm, phân bố nhãn, scenario, confusion matrix, precision/recall/F1, thời gian chạy và phân tích FP/FN. Mọi số liệu phải lấy từ `artifacts/run_metadata.json` và `artifacts/metrics.json`.

- [ ] **Step 6: Chương 6 — Conclusion, 11/07**

Đối chiếu từng mục tiêu với bằng chứng; nêu hạn chế rule-based, dữ liệu giả lập, ngưỡng cố định và khả năng khái quát. ML, streaming, SIEM và dashboard nâng cao chỉ là future work.

- [ ] **Step 7: Kiểm tra liên kết khung–report**

Run:

```bash
for n in $(seq -w 0 15); do rg -q "\[INTRO-$n\]" report/01-introduction.md || exit 1; done
rg -n "TBD|TODO|sẽ bổ sung|chưa có kết quả" report
```

Expected: vòng lặp exit 0; `rg` cuối không có kết quả.

- [ ] **Step 8: Commit từng chương**

Commit riêng sau khi mỗi chương được review, dùng message `docs: write chapter N ...`; không gộp sáu chương vào một commit.

### Task 13: Tái lập, rà soát và đóng gói bài nộp

**Phụ trách:** Cả nhóm  
**Files:** Modify `README.md`, report files; Generate `artifacts/*`

- [ ] **Step 1: Tái chạy từ môi trường sạch**

```bash
python -m venv /tmp/rbac-guard-final
/tmp/rbac-guard-final/bin/pip install -e '.[dev,web]'
/tmp/rbac-guard-final/bin/pytest -q --cov=rbac_guard --cov-fail-under=85
/tmp/rbac-guard-final/bin/rbac-guard init-db --db /tmp/rbac-final.db --seed data/rbac_seed.json
/tmp/rbac-guard-final/bin/rbac-guard analyze --db /tmp/rbac-final.db --log data/logs_demo.csv --config config/default.toml --output artifacts
/tmp/rbac-guard-final/bin/rbac-guard evaluate --alerts artifacts/alerts.json --events data/logs_demo.csv --output artifacts/metrics.json
```

Expected: setup và test thành công; bốn artifact được tái sinh.

- [ ] **Step 2: Đối chiếu báo cáo với artifact cuối**

Hai thành viên kiểm tra chéo mọi bảng số liệu, tên rule, severity threshold, số event và số alert. Chênh lệch phải sửa trong báo cáo hoặc tái sinh artifact, không sửa JSON bằng tay.

- [ ] **Step 3: Kiểm tra chất lượng repository**

```bash
git diff --check
git status --short
rg -n "TBD|TODO|FIXME|password\s*=|api[_-]?key" README.md config data src tests report
```

Expected: không whitespace error, không secret, không placeholder; chỉ artifact dự kiến có thể thay đổi.

- [ ] **Step 4: Đóng gói**

Tạo file nộp gồm mã nguồn, config, dữ liệu giả lập, test, artifacts cuối, README và báo cáo. Loại `.venv`, cache, database tạm và file upload thử khỏi gói.

- [ ] **Step 5: Tag bản cuối**

```bash
git add README.md config data src tests artifacts report
git commit -m "release: finalize rbac log analysis poc and report"
git tag v1.0.0
```

## 4. Tiêu chí nghiệm thu cuối

- CLI cài và chạy được từ môi trường Python sạch theo README.
- SQLite RBAC thực thi đúng active user → role → permission.
- CSV và JSON được chuẩn hóa về cùng model; dòng lỗi được cô lập.
- Cả ba risk type có luật, evidence, score và severity.
- Test pass với coverage tối thiểu 85%; scenario có positive và negative cases.
- Metric được sinh tự động từ nhãn, không nhập tay.
- Web UI nếu có chỉ là adapter tùy chọn, kết quả khớp CLI.
- Sáu chương khớp mã nguồn/artifact; Intro có đủ 16 nhãn.
- Không có dữ liệu thật, secret, placeholder hoặc tuyên bố vượt quá bằng chứng.
