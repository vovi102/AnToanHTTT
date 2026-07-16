# Unified RBAC Demo Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cung cấp một tài liệu duy nhất để khởi động và trình bày demo RBAC Nova Bank trong 5–7 phút, đồng thời xóa an toàn hai tài liệu demo đã được thay thế.

**Architecture:** `DEMO_RBAC_NOVA_BANK.md` là nguồn sự thật duy nhất cho demo giao diện; `README.md` và phần mở đầu của `HUONG_DAN_CHAY_DEMO.md` chỉ giới thiệu và liên kết tới file này. Phần thực nghiệm nghiên cứu, Streamlit, CLI, dữ liệu, artifact, paper/report và tài liệu lịch sử không bị thay đổi.

**Tech Stack:** Markdown, UV, FastAPI/Uvicorn, Next.js/npm, Git/rg.

## Global Constraints

- Chỉ xóa `docs/CHUAN_BI_DEMO_RBAC.md` và `docs/USER_JOURNEY_DEMO_RBAC.md`.
- Giữ nguyên backend, frontend, dữ liệu seed và chính sách RBAC.
- Giữ Streamlit, CLI, cấu hình, dataset, artifact, `paper/`, `report/`, file Word, đề cương và `docs/superpowers/`.
- Không theo dõi, sửa hoặc xóa file người dùng `Khung_dan_y_v3.md`.
- Không ghi cứng số lượng test; chỉ yêu cầu các lệnh kiểm thử kết thúc thành công.
- Lệnh demo phải chạy từ `/home/khoavd/WORKSPACE/AnToanHTTT` và dùng cổng backend `8000`, frontend `3000`.

---

### Task 1: Tạo tài liệu demo Nova Bank duy nhất

**Files:**
- Create: `DEMO_RBAC_NOVA_BANK.md`
- Reference: `docs/superpowers/specs/2026-07-16-unified-rbac-demo-guide-design.md`
- Reference: `docs/CHUAN_BI_DEMO_RBAC.md`
- Reference: `docs/USER_JOURNEY_DEMO_RBAC.md`

**Interfaces:**
- Consumes: Các route và tài khoản demo hiện có; không thay đổi API.
- Produces: Một tài liệu tự đủ nội dung, được `README.md` và `HUONG_DAN_CHAY_DEMO.md` liên kết ở Task 2.

- [ ] **Step 1: Xác nhận tài liệu hợp nhất chưa tồn tại**

Run:

```bash
test -f DEMO_RBAC_NOVA_BANK.md
```

Expected: exit code `1`, chứng minh file mới chưa tồn tại trước thay đổi.

- [ ] **Step 2: Tạo phần mục tiêu và dữ liệu cố định**

Dùng `apply_patch` tạo `DEMO_RBAC_NOVA_BANK.md` với phần đầu theo mẫu chính xác:

```markdown
# Hướng dẫn và kịch bản demo RBAC Nova Bank

Tài liệu này là nguồn hướng dẫn duy nhất cho demo giao diện Nova Bank. Thời
lượng mục tiêu là 5–7 phút, dành cho phần trình bày trước giảng viên.

## 1. Demo này chứng minh điều gì?

Một giao dịch viên tạo yêu cầu chuyển khoản 50.000.000 VND. Ở Baseline, người
này có thể tự duyệt giao dịch do hệ thống chưa tách quyền. Sau khi bật RBAC,
backend từ chối cùng hành vi bằng HTTP 403; chỉ Controller mới phê duyệt được.
Audit log lưu lại toàn bộ quyết định.

## 2. Thông tin dùng trong demo

| Thành phần | Giá trị |
| --- | --- |
| Giao diện | `http://localhost:3000` |
| Backend health check | `http://127.0.0.1:8000/health` |
| Admin | `admin01 / Admin@123` |
| Controller | `controller01 / Controller@123` |
| Teller tạo trực tiếp | `lan.demo / Lan@1234` |

### Dữ liệu giao dịch mẫu

| Trường | Giá trị |
| --- | --- |
| Tài khoản nguồn | `001100001234` |
| Tài khoản đích | `002200005678` |
| Người nhận | `Lê Bình` |
| Số tiền | `50000000` |
| Nội dung | `Thanh toán hợp đồng` |
```

- [ ] **Step 3: Viết phần cài đặt và khởi động có thể sao chép**

Thêm các mục `## 3. Cài đặt lần đầu` và `## 4. Khởi động trước mỗi lần demo`.
Phải tách rõ hai terminal và dùng đúng các lệnh:

```bash
cd /home/khoavd/WORKSPACE/AnToanHTTT
uv sync --extra api
```

```bash
cd /home/khoavd/WORKSPACE/AnToanHTTT/web
npm install
```

```bash
cd /home/khoavd/WORKSPACE/AnToanHTTT
uv run uvicorn rbac_guard.api:app --reload --host 127.0.0.1 --port 8000
```

```bash
cd /home/khoavd/WORKSPACE/AnToanHTTT/web
npm run dev
```

Ngay sau lệnh backend phải yêu cầu mở `http://127.0.0.1:8000/health` và chỉ
tiếp tục khi JSON có `"status":"ok"`. Ngay sau lệnh frontend phải yêu cầu mở
`http://localhost:3000` và giữ cả hai terminal hoạt động.

- [ ] **Step 4: Viết phần chuẩn bị trạng thái sạch**

Thêm `## 5. Chuẩn bị trạng thái sạch` với thứ tự bắt buộc:

1. Đăng nhập Admin.
2. Mở **Điều khiển demo**, chọn **Đặt lại toàn bộ dữ liệu demo**.
3. Đăng nhập Admin lại sau reset.
4. Xác nhận mode là **Baseline**.
5. Mở ba tab độc lập cho Admin, Teller và Controller.
6. Không tạo `lan.demo` trước khi trình bày.

Giải thích một câu rằng ứng dụng dùng `sessionStorage`, vì vậy mỗi tab giữ một
phiên đăng nhập riêng.

- [ ] **Step 5: Viết kịch bản 5–7 phút theo định dạng cố định**

Thêm `## 6. Kịch bản demo 5–7 phút` gồm đúng năm checkpoint sau. Mỗi checkpoint
phải có ba tiểu mục `Thao tác`, `Kết quả cần thấy`, `Lời trình bày`:

1. **Admin tạo Teller:** tạo `Lan Nguyễn / lan.demo / Lan@1234 / Teller`; kết
   quả là thông báo thành công; lời thoại nêu API lưu tài khoản, mật khẩu băm và
   role trong SQLite.
2. **Baseline cho phép tự duyệt:** Teller tạo giao dịch thứ nhất, tự phê duyệt;
   kết quả `Approved` với `created_by` và `approved_by` đều là `lan.demo`; lời
   thoại nêu rủi ro một người làm cả hai bước.
3. **Admin bật RBAC:** Admin bật bảo vệ; kết quả banner `SECURE MODE`; lời thoại
   nêu mode được lưu backend và audit.
4. **Backend chặn Teller:** Teller tạo giao dịch thứ hai, mở **Kiểm tra bảo vệ
   backend**, gửi request vượt quyền; kết quả `HTTP 403`, permission
   `transactions:approve`, trạng thái vẫn `Pending`; lời thoại phân biệt ẩn nút
   ở UI với kiểm tra quyền thật ở backend.
5. **Controller duyệt và Admin đối chiếu audit:** Controller duyệt giao dịch
   Pending; kết quả `Approved` bởi `controller01`; Admin tìm theo mã giao dịch
   và chỉ ra `baseline_bypass`, `denied`, `allowed`, `success`.

- [ ] **Step 6: Viết kết quả, kết luận, xử lý lỗi và checklist cuối**

Thêm bốn mục cuối:

- `## 7. Kết quả bắt buộc sau demo`: bảng hai giao dịch và người duyệt.
- `## 8. Lời kết 30 giây`: giải thích authentication, authorization/RBAC và
  audit bằng ba câu ngắn.
- `## 9. Xử lý sự cố`: bảng triệu chứng/cách xử lý cho `Failed to fetch`, health
  check lỗi, webpack module error, cổng bị chiếm, Teller chưa thấy mode mới,
  `lan.demo` đã tồn tại và Controller chưa thấy giao dịch.
- `## 10. Checklist một phút trước khi trình bày`: backend health OK, frontend
  mở được, reset xong, Baseline, ba tab, tài khoản Controller đăng nhập được và
  dữ liệu form sẵn sàng. Không ghi số lượng test cụ thể.

Với lỗi webpack, hướng dẫn dừng Next.js, xóa riêng thư mục cache `web/.next`,
chạy lại `npm run dev` và hard refresh. Với lỗi cổng, hướng dẫn kiểm tra bằng:

```bash
ss -ltnp '( sport = :8000 or sport = :3000 )'
```

- [ ] **Step 7: Kiểm tra cấu trúc và commit tài liệu chính**

Run:

```bash
test -f DEMO_RBAC_NOVA_BANK.md
rg -n '^## [1-9]\.|^## 10\.' DEMO_RBAC_NOVA_BANK.md
rg -n 'HTTP 403|transactions:approve|baseline_bypass|controller01' DEMO_RBAC_NOVA_BANK.md
git diff --check
```

Expected: file tồn tại; đủ mục `1` đến `10`; bốn bằng chứng backend/audit đều
xuất hiện; `git diff --check` không có output.

Commit:

```bash
git add DEMO_RBAC_NOVA_BANK.md
git commit -m "docs: add unified Nova Bank demo guide"
```

---

### Task 2: Loại bỏ tài liệu trùng và cập nhật các điểm vào

**Files:**
- Modify: `README.md`
- Modify: `HUONG_DAN_CHAY_DEMO.md`
- Delete: `docs/CHUAN_BI_DEMO_RBAC.md`
- Delete: `docs/USER_JOURNEY_DEMO_RBAC.md`

**Interfaces:**
- Consumes: `DEMO_RBAC_NOVA_BANK.md` từ Task 1.
- Produces: Hai entry point còn lại trỏ tới nguồn hướng dẫn chính, không còn liên kết hoạt động tới file bị xóa.

- [ ] **Step 1: Ghi nhận các tham chiếu trùng trước khi sửa**

Run:

```bash
rg -n 'CHUAN_BI_DEMO_RBAC|USER_JOURNEY_DEMO_RBAC|Giao diện Streamlit cũ|78 passed|7 frontend tests' README.md HUONG_DAN_CHAY_DEMO.md docs
```

Expected: có kết quả trong tài liệu người dùng hiện tại; các kết quả trong
`docs/superpowers/` chỉ là lịch sử và không sửa.

- [ ] **Step 2: Rút gọn phần Nova Bank trong README**

Giữ phần mô tả một đoạn về luồng `Admin → Teller → Controller`, thay các lệnh
khởi động và hai liên kết cũ bằng đúng một liên kết:

```markdown
Hướng dẫn khởi động, dữ liệu mẫu, kịch bản 5–7 phút và xử lý sự cố nằm tại
[`DEMO_RBAC_NOVA_BANK.md`](DEMO_RBAC_NOVA_BANK.md).
```

Đổi tiêu đề đoạn Streamlit thành `Giao diện phân tích log tùy chọn`; giữ nguyên
hai lệnh UV/Streamlit vì đây là chức năng độc lập.

- [ ] **Step 3: Rút gọn phần Nova Bank trong hướng dẫn thực nghiệm**

Thay toàn bộ phần đầu từ `## Demo giao diện RBAC có backend (Next.js + FastAPI)`
đến trước câu `Tài liệu này hướng dẫn tái lập hai thực nghiệm` bằng:

```markdown
## Demo giao diện RBAC Nova Bank

Hướng dẫn cài đặt, khởi động, chuẩn bị ba vai trò, kịch bản 5–7 phút và xử lý sự
cố đã được hợp nhất tại [`DEMO_RBAC_NOVA_BANK.md`](DEMO_RBAC_NOVA_BANK.md).

Phần còn lại của tài liệu này chỉ dành cho việc tái lập thực nghiệm phân tích
log và context-aware risk.
```

Trong phần kiểm tra, đổi câu có số lượng test cố định thành `Kết quả mong đợi:
toàn bộ kiểm thử kết thúc thành công.` Giữ nguyên các số liệu thực nghiệm như
60 sự kiện, 20 alert và metric vì đó là kết quả nghiên cứu, không phải số test.

- [ ] **Step 4: Xóa đúng hai tài liệu đã hợp nhất**

Dùng `apply_patch` xóa:

```text
docs/CHUAN_BI_DEMO_RBAC.md
docs/USER_JOURNEY_DEMO_RBAC.md
```

Không xóa hoặc sửa file nào khác trong `docs/`.

- [ ] **Step 5: Kiểm tra không còn tham chiếu hoạt động và commit cleanup**

Run:

```bash
test ! -e docs/CHUAN_BI_DEMO_RBAC.md
test ! -e docs/USER_JOURNEY_DEMO_RBAC.md
! rg -n 'CHUAN_BI_DEMO_RBAC|USER_JOURNEY_DEMO_RBAC|Giao diện Streamlit cũ|78 passed|7 frontend tests' README.md HUONG_DAN_CHAY_DEMO.md docs --glob '!docs/superpowers/**'
rg -n 'DEMO_RBAC_NOVA_BANK\.md' README.md HUONG_DAN_CHAY_DEMO.md
git diff --check
```

Expected: hai file không còn tồn tại; không còn tham chiếu lỗi thời trong tài
liệu đang dùng; README và hướng dẫn thực nghiệm đều liên kết file mới; không có
lỗi whitespace.

Commit:

```bash
git add README.md HUONG_DAN_CHAY_DEMO.md docs/CHUAN_BI_DEMO_RBAC.md docs/USER_JOURNEY_DEMO_RBAC.md
git commit -m "docs: remove superseded RBAC demo guides"
```

---

### Task 3: Xác minh tài liệu và chương trình demo

**Files:**
- Verify: `DEMO_RBAC_NOVA_BANK.md`
- Verify: `README.md`
- Verify: `HUONG_DAN_CHAY_DEMO.md`
- Preserve: `Khung_dan_y_v3.md`

**Interfaces:**
- Consumes: Tài liệu và liên kết sau Task 1–2.
- Produces: Bằng chứng rằng hướng dẫn không có liên kết local hỏng và chương trình vẫn build/test thành công.

- [ ] **Step 1: Kiểm tra các liên kết Markdown local trong tài liệu đang dùng**

Run:

```bash
for file in README.md HUONG_DAN_CHAY_DEMO.md DEMO_RBAC_NOVA_BANK.md; do
  sed -nE 's/.*\]\(([^)#]+)(#[^)]+)?\).*/\1/p' "$file"
done | while IFS= read -r target; do
  case "$target" in
    http://*|https://*) continue ;;
  esac
  test -e "$target" || { echo "Broken link: $target"; exit 1; }
done
```

Expected: exit code `0`, không in `Broken link`.

- [ ] **Step 2: Chạy toàn bộ kiểm thử backend**

Run:

```bash
UV_CACHE_DIR=.uv-cache uv run pytest -q
```

Expected: exit code `0`; toàn bộ Python tests pass.

- [ ] **Step 3: Chạy test và build frontend**

Run:

```bash
cd web
npm test
npm run build
```

Expected: cả hai lệnh exit code `0`; Vitest pass và Next.js build thành công.

- [ ] **Step 4: Smoke-test backend health endpoint**

Từ thư mục gốc, chạy backend tạm ở cổng `8000`, gọi health endpoint, rồi dừng
đúng PID vừa tạo:

```bash
UV_CACHE_DIR=.uv-cache uv run uvicorn rbac_guard.api:app --host 127.0.0.1 --port 8000 > /tmp/rbac-guide-api.log 2>&1 &
API_PID=$!
for attempt in 1 2 3 4 5; do
  curl -fsS http://127.0.0.1:8000/health && break
  sleep 1
done
kill "$API_PID"
wait "$API_PID" 2>/dev/null || true
```

Expected: curl trả JSON chứa `"status":"ok"`; tiến trình tạm được dừng.

- [ ] **Step 5: Kiểm tra phạm vi xóa và working tree**

Run:

```bash
git diff --check
git status --short
git ls-files --deleted
test -f /home/khoavd/WORKSPACE/AnToanHTTT/Khung_dan_y_v3.md
git -C /home/khoavd/WORKSPACE/AnToanHTTT status --short --untracked-files=all | rg '^\?\? Khung_dan_y_v3\.md$'
```

Expected: worktree không có thay đổi chưa commit từ Task 1–2; không còn file
tracked bị xóa nhưng chưa staged; `Khung_dan_y_v3.md` vẫn tồn tại trong checkout
gốc và vẫn là file untracked của người dùng.

- [ ] **Step 6: Ghi nhận kết quả xác minh**

Không tạo commit nếu Step 1–5 không làm thay đổi file. Báo cáo rõ:

- file hướng dẫn chính đã tạo;
- hai file lỗi thời đã xóa;
- các phần được giữ nguyên;
- kết quả pytest, Vitest, Next.js build và health check;
- trạng thái `Khung_dan_y_v3.md`.
