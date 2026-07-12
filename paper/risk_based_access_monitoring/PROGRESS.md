# Nhật ký triển khai bài báo

Tệp này lưu checkpoint để có thể tiếp tục bài báo qua nhiều phiên làm việc.
Không xóa các mục cũ; bổ sung mục mới ở đầu phần nhật ký.

## Checkpoint hiện tại

- **Giai đoạn đang làm:** CP3 -- Thực nghiệm tái lập.
- **Task đang làm:** Không còn -- T01--T19 đã hoàn thành.
- **Mục tiêu kế tiếp:** Thay ``Tác giả ẩn danh'' bằng thông tin tác giả khi có
  yêu cầu nộp không ẩn danh; sau đó biên dịch lại bằng lệnh ở T19.
- **Quyết định đã chốt:** Bài báo là đánh giá một nguyên mẫu có thể tái lập
  trên dữ liệu tổng hợp; không tuyên bố là SIEM hay hệ thống ngân hàng sản xuất.
- **Câu hỏi nghiên cứu:** RQ1 về pipeline tích hợp RBAC và log; RQ2 về tín hiệu
  ngữ cảnh hỗ trợ triage; RQ3 về phát hiện/gom nhóm kịch bản tổng hợp.
- **Lưu ý về phạm vi code:** `expected_label` hiện bắt buộc ở parser và chỉ
  phục vụ đánh giá; incident có thời điểm, IDs và evidence, không có timeline
  chi tiết theo thứ tự.
- **Nguồn điều phối task:** Xem `TASKS.md` để biết phụ thuộc, tệp đầu ra và tiêu
  chí nghiệm thu của từng task.

## Nhật ký

### 2026-07-12 -- Hoàn thành T19: bản PDF nộp

- Đã chạy thành công `latexmk -pdf -interaction=nonstopmode -halt-on-error
  main.tex`; `main.pdf` có 10 trang (461314 byte).
- Không có citation/reference undefined, lỗi LaTeX hay placeholder trong các
  tệp `.tex`. Đã kiểm tra trực quan trang phương pháp: tiêu đề ``Phương pháp''
  và nội dung tiếng Việt hiển thị đầy đủ dấu.
- T01--T19 đều **Hoàn thành**. Tác giả hiện được ẩn danh có chủ ý; thay thông
  tin này trước khi nộp bản không ẩn danh.

### 2026-07-12 -- Hoàn thành T18: kiểm toán claim, citation và định dạng

- Đã đối chiếu các claim định lượng với bảng/artifact CP3; các claim về RBAC,
  logging, zero trust và giới hạn vận hành được đặt cạnh citation tương ứng.
- Mọi khóa trong `\cite{...}` đều có trong `references.bib`; lần biên dịch kiểm
  tra không có citation/reference undefined hay lỗi điều khiển LaTeX.
- Đã xác nhận 2 figure và 4 table. Thay thông tin tác giả mẫu bằng ``Tác giả
  ẩn danh'' để bản thảo không còn placeholder danh tính; đã chuyển T18 sang
  **Hoàn thành** và bắt đầu T19.

### 2026-07-12 -- Hoàn thành T17: tóm tắt và kết luận theo số liệu cuối

- Đã đồng bộ `sections/00_abstract.tex` và `sections/08_conclusion.tex` với
  baseline (60 event, 20 alert; precision macro 1,0000, recall macro 0,9667,
  F1 macro 0,9825) và phân tích ngữ cảnh (14 event hợp lệ, 15 alert, 10
  finding, 3 incident).
- Đã nêu một SQL injection bị bỏ sót bởi regex và giới hạn dữ liệu tổng hợp;
  không suy diễn hiệu năng sản xuất hoặc khả năng tổng quát hóa.
- Đã chuyển T17 sang **Hoàn thành** và bắt đầu T18.

### 2026-07-12 -- Hoàn thành T16: thảo luận và threats to validity

- Đã mở rộng `sections/07_discussion.tex` với trade-off giữa pipeline xác định,
  giải thích được và tính linh hoạt của policy; đồng thời nêu rõ giả định RBAC,
  ngưỡng heuristic và tính chất hậu kiểm offline.
- Đã tách các rủi ro nội tại, tính xây dựng và ngoại suy: dataset tổng hợp,
  regex/threshold có thể bỏ sót, finding không là mẫu độc lập, log vận hành có
  drift/proxy/thiếu trường và nguyên mẫu không bảo vệ toàn vẹn log hay phản ứng
  thời gian thực.
- Hướng mở rộng được giới hạn thành các giả thuyết đo được trên log ẩn danh có
  nhãn độc lập. Đã chuyển T16 sang **Hoàn thành** và bắt đầu T17.

### 2026-07-12 -- Hoàn thành T15: đánh giá truy nguyên được

- Đã kiểm tra lại bốn bảng: dataset, metric baseline, finding context và
  incident. Các giá trị khớp `metrics.json`, `run_metadata.json`,
  `context_findings.json` và `incidents.json` của CP3.
- Đã thêm đoạn kiểm tra tính nhất quán vào `sections/06_evaluation.tex`, tách
  metric phân loại baseline khỏi các số đếm triage của context để tránh suy
  diễn precision/recall hay khả năng tổng quát hóa từ kịch bản tổng hợp.
- Đã đối chiếu case study `incident-38dfcb846bfe`: 6 event, 10 alert, score
  99, Critical và evidence đều có trong artifact. Đã chuyển T15 sang **Hoàn
  thành** và bắt đầu T16.

### 2026-07-12 -- Hoàn thành T14: cài đặt tái lập

- Đã viết lại `sections/05_implementation.tex` theo các mô-đun thực tế:
  parser, RBAC SQLite, rules, context, scoring, reporting, service và hai
  adapter CLI/Streamlit. Phần này nêu rõ CLI, config TOML, artifact đầu ra và
  ranh giới chỉ đọc của giao diện web.
- Đã thêm Listing `lst:reproduce` với các lệnh seed CSDL, tái sinh baseline,
  đánh giá và chạy context-risk; mọi đường dẫn/switch khớp README và CLI.
- Đã ghi cổng chất lượng `pytest`/coverage 85\% cùng phạm vi loại trừ adapter,
  thay cho claim chưa kiểm chứng về một lần chạy cuối.
- Đã chuyển T14 sang **Hoàn thành** và bắt đầu T15.

### 2026-07-12 -- Hoàn thành T13: phương pháp khớp mã nguồn

- Đã viết lại `sections/04_methodology.tex` với schema event, predicate RBAC,
  ba luật phát hiện, điều kiện học baseline ngữ cảnh, hai công thức scoring và
  công thức incident. Các tham số 5 lần thất bại, cửa sổ 300 giây, bonus và
  ngưỡng severity đều khớp `config/default.toml`.
- Đã ghi rõ các chi tiết dễ sai: SQLi chỉ tạo finding ở mẫu khớp đầu tiên;
  truy cập trái phép xảy ra khi RBAC không cấp quyền hoặc log là `denied`; và
  context repeated-denial phát tại lần từ chối thứ ba trong cửa sổ.
- Đã kiểm chứng `latexmk -g -pdf -interaction=nonstopmode -halt-on-error
  main.tex` thành công (9 trang), không có citation/reference undefined; kiểm
  tra trực quan hai hình kiến trúc và luồng event--alert--incident.
- Đã chuyển T13 sang **Hoàn thành** và bắt đầu T14.

### 2026-07-12 -- Hoàn thành T12: mô hình hệ thống và threat model

- Đã mở rộng `sections/03_system_model.tex` với đầu vào/đầu ra, ranh giới tin
  cậy và mô hình đe dọa. Nhật ký là dữ liệu không tin cậy; RBAC seed, cấu hình,
  mã dịch vụ và thư mục report nằm trong ranh giới tin cậy của một lần chạy.
- Đã giới hạn rõ attacker có thể tạo các hành vi để lại log (SQLi, brute force,
  truy cập trái phép), nhưng nguyên mẫu không xác nhận khai thác thành công.
  Các ngoại lệ gồm kiểm soát thời gian thực, toàn vẹn/nguồn gốc log, tương quan
  đa nguồn, pháp chứng, phản ứng tự động và dữ liệu vận hành thực.
- Đã chuyển T12 sang **Hoàn thành** và bắt đầu T13.

### 2026-07-12 -- Hoàn thành T11: hình luồng event--alert--incident

- Đã tạo `figures/event_alert_incident.tex` và chèn Hình~\ref{fig:event-alert-incident}
  vào phần phương pháp. Sơ đồ theo đúng `build_incidents`: alert giữ event IDs
  và evidence, được phân vùng theo `(user, IP)`, sắp xếp theo thời gian và tách
  đoạn khi khoảng cách lớn hơn cửa sổ $W$ (300 giây theo cấu hình thực nghiệm).
- Caption nêu giới hạn diễn giải của `start_time`/`end_time`, tránh gán cho
  incident một timeline pháp chứng không có trong code/artifact.
- Đã chuyển T11 sang **Hoàn thành** và bắt đầu T12.

### 2026-07-12 -- Hoàn thành T10: hình kiến trúc pipeline

- Đã tạo sơ đồ TikZ tại `figures/architecture.tex` và thay khung chữ tạm trong
  `sections/03_system_model.tex`. Hình thể hiện nhật ký/cấu hình, parser, CSDL
  RBAC, ba luật phát hiện, profiler ngữ cảnh, scorer và reporter CSV/JSON;
  CLI/Streamlit chỉ là adapter vào dịch vụ phân tích.
- Caption ghi rõ profiler và incident chỉ xuất hiện trong chế độ context-risk,
  phù hợp với `src/rbac_guard/service.py`.
- Đã chuyển T10 sang **Hoàn thành** và bắt đầu T11. Kiểm chứng biên dịch PDF
  được thực hiện sau khi hoàn tất hình T11 để kiểm tra hai hình cùng lúc.

### 2026-07-12 -- Hoàn thành T09: dataset và thiết kế đánh giá

- Đã tạo `tables/dataset_description.tex`, tách baseline `logs_demo.csv`
  (60 event; 30 benign và ba nhãn rủi ro, mỗi nhãn 10) khỏi
  `logs_risk_demo.csv` (14 event; 4 benign, 2 context anomaly, 4 password
  guessing, 4 unauthorized access).
- `sections/06_evaluation.tex` nay phân biệt metric TP/FP/FN/TN,
  precision/recall/F1 cho baseline với đánh giá kịch bản/triage cho context;
  đồng thời nêu seed, config, cửa sổ 300 giây, các bonus và vị trí lệnh/artifact.
- Đã chuyển T09 sang **Hoàn thành** và bắt đầu T10.
- **Điểm tiếp tục:** tạo hình kiến trúc pipeline đúng với module code và tích
  hợp vào `sections/03_system_model.tex`.

### 2026-07-12 -- Hoàn thành T08: case study từ artifact incident

- Đã thêm case study cho `incident-38dfcb846bfe` trong
  `sections/06_evaluation.tex`: ID, user--IP, hai mốc thời gian, 6 event,
  10 alert, score 99, severity Critical và evidence đều lấy từ
  `artifacts/cp3-context/incidents.json`.
- Case study giải thích quy tắc tính điểm (max alert score + session-chain bonus
  15, chặn ở 100) và nêu dứt khoát giới hạn dữ liệu/nhãn tổng hợp.
- Đã chuyển T08 sang **Hoàn thành** và T09 sang **Đang làm**.
- **Điểm tiếp tục:** lập bảng tách biệt baseline/context dataset, nhãn, metric,
  cấu hình và lệnh tái lập.

### 2026-07-12 -- Hoàn thành T07: incident grouping tái lập

- Từ `artifacts/cp3-context/incidents.json`, xác nhận có 3 incident: một Medium
  và hai Critical. Bảng `tables/incident_summary.tex` ghi ID, hai mốc thời gian,
  severity, số sự kiện/cảnh báo và evidence của từng incident.
- Quy tắc grouping đã đối chiếu với `src/rbac_guard/context.py`: cảnh báo được
  nhóm theo cặp user--IP; trong một cặp, chênh lệch lớn hơn 300 giây tạo đoạn mới.
  Điểm incident là điểm alert tối đa cộng session-chain bonus nếu đoạn có nhiều
  alert, bị chặn tối đa 100.
- Đã ghi rõ trong caption và phần đánh giá rằng `start_time`/`end_time` không
  phải timeline pháp chứng chi tiết.
- Đã chuyển T07 sang **Hoàn thành** và T08 sang **Đang làm**.
- **Điểm tiếp tục:** viết case study cho `incident-38dfcb846bfe` với evidence
  nguyên gốc; nêu rõ đây là kịch bản tổng hợp.

### 2026-07-12 -- Hoàn thành T06: context-risk tái lập

- **Lệnh tái sinh:**
  ```bash
  tmpdir=$(mktemp -d)
  .venv/bin/rbac-guard init-db --db "$tmpdir/rbac.db" --seed data/rbac_seed.json
  .venv/bin/rbac-guard analyze --db "$tmpdir/rbac.db" --log data/logs_risk_demo.csv \
    --config config/default.toml \
    --output paper/risk_based_access_monitoring/artifacts/cp3-context --context-risk
  ```
- **Artifact gốc:** `artifacts/cp3-context/alerts.json`, `context_findings.json`,
  `incidents.json` và `run_metadata.json` (cùng hai tệp CSV do chương trình sinh).
- **Kết quả:** 14 sự kiện hợp lệ, 0 dòng lỗi, 15 cảnh báo và 10 finding. Phân
  theo signal: CTX-AFTER-HOURS 6, CTX-NEW-IP 1, CTX-RARE-RESOURCE 2 và
  CTX-REPEATED-DENIAL 1. Tất cả số liệu được chép sang
  `tables/context_findings.tex` từ artifact JSON.
- Đã chuyển T06 sang **Hoàn thành** và T07 sang **Đang làm**.
- **Điểm tiếp tục:** lập bảng incident từ `incidents.json`; mô tả đúng việc
  code nhóm theo cặp user--IP và khoảng cách thời gian, không suy diễn timeline
  chi tiết ngoài `start_time` và `end_time` có trong artifact.

### 2026-07-12 -- Hoàn thành T05: baseline detection tái lập

- **Lệnh tái sinh:**
  ```bash
  tmpdir=$(mktemp -d)
  .venv/bin/rbac-guard init-db --db "$tmpdir/rbac.db" --seed data/rbac_seed.json
  .venv/bin/rbac-guard analyze --db "$tmpdir/rbac.db" --log data/logs_demo.csv \
    --config config/default.toml --output paper/risk_based_access_monitoring/artifacts/cp3-baseline
  .venv/bin/rbac-guard evaluate \
    --alerts paper/risk_based_access_monitoring/artifacts/cp3-baseline/alerts.json \
    --events data/logs_demo.csv \
    --output paper/risk_based_access_monitoring/artifacts/cp3-baseline/metrics.json
  ```
- **Artifact gốc:** `artifacts/cp3-baseline/alerts.json`, `run_metadata.json`
  và `metrics.json` (kèm `alerts.csv` do chương trình sinh tự động).
- **Kết quả:** 60 sự kiện hợp lệ, 0 dòng lỗi, 20 cảnh báo; macro precision
  1.0000, recall 0.9667 và F1 0.9825. Theo nhãn: SQL injection có
  TP/FP/FN/TN = 9/0/1/50, precision/recall/F1 = 1.0000/0.9000/0.9474;
  hai nhãn còn lại đều đạt 10/0/0/50 và 1.0000/1.0000/1.0000.
- Đã lưu bảng truy nguyên số liệu tại `tables/baseline_results.tex` và chuyển
  T05 sang **Hoàn thành**; T06 là task **Đang làm**.
- **Điểm tiếp tục:** tái sinh context-risk và thống kê từng context rule chỉ từ
  artifact `artifacts/cp3-context/`.

### 2026-07-12 -- Hoàn thành T04: regression test

- **Lệnh kiểm chứng:** `.venv/bin/pytest -q`.
- **Kết quả:** thành công, 65/65 test pass (kiểm đếm bằng
  `.venv/bin/pytest --collect-only -q | awk '{total += $2} END {print total}'`).
- Đã chuyển T04 sang **Hoàn thành** và T05 sang **Đang làm** trong `TASKS.md`.
- **Điểm tiếp tục:** tái sinh baseline detection theo các lệnh CP3 bên dưới;
  lưu toàn bộ JSON gốc tại `artifacts/cp3-baseline/` trước khi viết bảng LaTeX.

### 2026-07-12 -- Chuẩn hóa backlog thực thi

- Đã tạo `TASKS.md` với 19 task có mã định danh, phụ thuộc, đầu ra, tiêu chí
  nghiệm thu và trạng thái.
- T04--T09 chia nhỏ CP3 để số liệu chỉ được viết sau khi có test, artifact,
  bảng baseline, context và incident tương ứng.
- **Điểm tiếp tục:** Hoàn thành T04, sau đó T05; cập nhật trạng thái trong
  `TASKS.md` và nhật ký này.

### 2026-07-12 -- Hoàn thành CP2: tài liệu và khung lập luận

- `references.bib` hiện có 12 nguồn: RBAC nền tảng, NIST về log management,
  zero trust, authentication và audit, SoK về context/risk-aware access control,
  alert correlation, OWASP và MITRE ATT\&CK.
- `02_related_work.tex` có thêm hai tiểu mục về correlation và kịch bản tấn
  công; phần risk monitoring đã phân biệt rõ access control thời gian thực với
  hậu kiểm log của nguyên mẫu.
- Đã sửa các claim không khớp code: `expected_label`, incident timeline và
  coverage gate.
- **Kiểm chứng:** `latexmk -pdf -interaction=nonstopmode -halt-on-error
  main.tex` thành công, không có citation/reference undefined.
- **Điểm tiếp tục:** CP3, dùng chính xác các lệnh tái sinh bên dưới.

### 2026-07-12 -- Khởi tạo triển khai

- Đã chuyển kế hoạch thành checkpoint có điều kiện hoàn thành trong `PLAN.md`.
- Đã khởi tạo hướng thu thập nguồn cho RBAC theo ngữ cảnh, zero trust,
  correlation và threat taxonomy.
- **Kiểm chứng đã có:** `pytest -q` đạt 65 tests; baseline cho 60 event có 20
  alerts; context demo cho 14 event có 15 alerts và 3 incidents.
- **Việc tiếp theo tại thời điểm khởi tạo:** Hoàn thiện CP2, rồi chạy lại lệnh
  CP3 và lưu artifact/bảng tái sinh.

## Lệnh tái sinh cho CP3

```bash
tmpdir=$(mktemp -d)
.venv/bin/rbac-guard init-db --db "$tmpdir/rbac.db" --seed data/rbac_seed.json
.venv/bin/rbac-guard analyze --db "$tmpdir/rbac.db" --log data/logs_demo.csv \
  --config config/default.toml --output "$tmpdir/base"
.venv/bin/rbac-guard evaluate --alerts "$tmpdir/base/alerts.json" \
  --events data/logs_demo.csv --output "$tmpdir/base/metrics.json"
.venv/bin/rbac-guard analyze --db "$tmpdir/rbac.db" --log data/logs_risk_demo.csv \
  --config config/default.toml --output "$tmpdir/context" --context-risk
```
