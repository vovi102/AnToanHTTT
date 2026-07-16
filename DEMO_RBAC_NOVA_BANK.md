# Hướng dẫn và kịch bản demo RBAC Nova Bank

Tài liệu này là nguồn hướng dẫn duy nhất cho demo giao diện Nova Bank. Thời
lượng mục tiêu là 5–7 phút, dành cho phần trình bày trước giảng viên.

## 1. Demo này chứng minh điều gì?

Một giao dịch viên tạo yêu cầu chuyển khoản 50.000.000 VND. Ở **Baseline**,
người này có thể tự duyệt giao dịch do hệ thống chưa tách quyền. Sau khi bật
**RBAC**, backend từ chối cùng hành vi bằng HTTP 403; chỉ Controller mới phê
duyệt được. Audit log lưu lại toàn bộ quyết định.

Luồng trình bày duy nhất:

```text
Admin tạo Teller
      ↓
Teller tạo và tự duyệt giao dịch ở Baseline
      ↓
Admin bật RBAC
      ↓
Teller thử duyệt giao dịch mới → backend trả HTTP 403
      ↓
Controller phê duyệt → Admin kiểm tra audit
```

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

## 3. Cài đặt lần đầu

Chỉ thực hiện mục này ở lần chạy đầu tiên hoặc sau khi dependency thay đổi.

### Backend

Mở terminal tại thư mục gốc dự án:

```bash
cd /home/khoavd/WORKSPACE/AnToanHTTT
uv sync --extra api
```

UV sẽ tự tạo và quản lý môi trường Python trong `.venv`.

### Frontend

```bash
cd /home/khoavd/WORKSPACE/AnToanHTTT/web
npm install
```

### Kiểm tra trước buổi demo

```bash
cd /home/khoavd/WORKSPACE/AnToanHTTT
UV_CACHE_DIR=.uv-cache uv run pytest -q
```

```bash
cd /home/khoavd/WORKSPACE/AnToanHTTT/web
npm test
npm run build
```

Chỉ tiếp tục khi tất cả lệnh kết thúc thành công. Không cần chạy lại test trong
lúc đang đứng trước lớp nếu bạn đã kiểm tra trước đó.

## 4. Khởi động trước mỗi lần demo

Cần giữ đồng thời hai terminal hoạt động.

### Terminal 1 — FastAPI backend

```bash
cd /home/khoavd/WORKSPACE/AnToanHTTT
uv run uvicorn rbac_guard.api:app --reload --host 127.0.0.1 --port 8000
```

Mở <http://127.0.0.1:8000/health>. Chỉ tiếp tục khi nhận được JSON có:

```json
{"status":"ok"}
```

Nếu health check không hoạt động thì giao diện có thể mở nhưng đăng nhập sẽ báo
`Failed to fetch`.

### Terminal 2 — Next.js frontend

```bash
cd /home/khoavd/WORKSPACE/AnToanHTTT/web
npm run dev
```

Mở <http://localhost:3000>. Không đóng hai terminal trong lúc demo.

## 5. Chuẩn bị trạng thái sạch

Thực hiện phần này trước khi trình bày, không thực hiện giữa kịch bản.

1. Mở <http://localhost:3000> và đăng nhập Admin bằng
   `admin01 / Admin@123`.
2. Chọn **Điều khiển demo** trên menu.
3. Bấm **Đặt lại toàn bộ dữ liệu demo** và xác nhận.
4. Reset sẽ xóa phiên hiện tại; đăng nhập lại Admin.
5. Vào **Điều khiển demo** và xác nhận trạng thái đang là **BASELINE**.
6. Mở riêng ba tab trực tiếp từ <http://localhost:3000> để dùng cho Admin,
   Teller và Controller.
7. Không tạo `lan.demo` trước. Tài khoản này phải được tạo trực tiếp khi trình
   bày để chứng minh backend thật sự thay đổi dữ liệu.

Ứng dụng lưu phiên trong `sessionStorage`, vì vậy mỗi tab có thể giữ một token
đăng nhập độc lập. Hãy mở từng tab trực tiếp, không dùng chung một tab rồi đăng
xuất liên tục.

## 6. Kịch bản demo 5–7 phút

### Bước 1 — Admin tạo tài khoản Teller

**Thao tác**

1. Ở tab Admin, chọn **Nhân viên**.
2. Nhập:
   - Họ và tên: `Lan Nguyễn`
   - Tên đăng nhập: `lan.demo`
   - Mật khẩu tạm: `Lan@1234`
   - Vai trò: **Giao dịch viên (Teller)**
3. Bấm **Tạo tài khoản và gán vai trò**.

**Kết quả cần thấy**

- Giao diện báo tạo tài khoản thành công.
- `lan.demo` xuất hiện trong **Danh sách nhân viên** với vai trò Giao dịch viên.

**Lời trình bày**

> Admin vừa gửi dữ liệu tới FastAPI. Backend băm mật khẩu, tạo tài khoản và lưu
> role Teller trong SQLite. Đây không phải tài khoản viết cứng ở giao diện.

### Bước 2 — Baseline cho phép Teller tự duyệt

**Thao tác**

1. Ở tab Teller, đăng nhập `lan.demo / Lan@1234`.
2. Chọn **Giao dịch** và nhập dữ liệu mẫu ở mục 2.
3. Bấm **Tạo yêu cầu chuyển khoản**.
4. Tại giao dịch vừa tạo, bấm **Tự phê duyệt giao dịch** và xác nhận.
5. Ghi lại hoặc đọc to mã giao dịch thứ nhất để đối chiếu audit về sau.

**Kết quả cần thấy**

- Giao dịch chuyển từ `Pending` sang `Approved`.
- Người tạo và người duyệt đều là `lan.demo`.
- Banner trên cùng vẫn là `BASELINE`.

**Lời trình bày**

> Hệ thống đã xác thực Lan là ai, nhưng ở Baseline chưa tách quyền tạo và quyền
> duyệt. Một người có thể hoàn tất cả hai bước, tạo ra rủi ro gian lận.

### Bước 3 — Admin bật RBAC

**Thao tác**

1. Quay lại tab Admin và mở **Điều khiển demo**.
2. Bấm **Bật bảo vệ RBAC** và xác nhận.

**Kết quả cần thấy**

- Trạng thái hiện tại chuyển thành `RBAC`.
- Banner trên cùng hiển thị `SECURE MODE`.

**Lời trình bày**

> Chính sách vừa được thay đổi tại backend và thao tác này cũng được ghi audit.
> Đây không phải hiệu ứng đổi màu hoặc ẩn nút riêng ở frontend.

### Bước 4 — Backend chặn Teller vượt quyền

**Thao tác**

1. Chuyển sang tab Teller. Khi tab nhận focus, ứng dụng tải lại security mode.
2. Tạo giao dịch thứ hai với cùng dữ liệu mẫu.
3. Quan sát nút tự phê duyệt thông thường không còn xuất hiện.
4. Mở **Kiểm tra bảo vệ backend** tại giao dịch đang Pending.
5. Bấm **Gửi thử request vượt quyền**.
6. Ghi lại mã giao dịch thứ hai.

**Kết quả cần thấy**

- Backend trả `HTTP 403`.
- Thông báo chỉ ra permission bị thiếu là `transactions:approve`.
- Giao dịch thứ hai vẫn là `Pending`; `approved_by` chưa có giá trị.

**Lời trình bày**

> UI đã ẩn tác vụ để đúng trải nghiệm của Teller, nhưng tôi vẫn cố ý gọi trực
> tiếp endpoint phê duyệt. Backend mới là lớp bảo vệ thật: request bị trả 403
> và dữ liệu giao dịch không thay đổi.

### Bước 5 — Controller duyệt và Admin kiểm tra audit

**Thao tác**

1. Ở tab Controller, đăng nhập `controller01 / Controller@123`.
2. Chọn **Phê duyệt**.
3. Tìm giao dịch thứ hai đang Pending và bấm **Phê duyệt giao dịch**.
4. Quay lại tab Admin, chọn **Nhật ký kiểm toán**.
5. Nhập mã giao dịch vào ô tìm kiếm và đối chiếu các kết quả audit.

**Kết quả cần thấy**

- Giao dịch thứ hai chuyển thành `Approved`.
- Người duyệt là `controller01`, khác người tạo `lan.demo`.
- Audit thể hiện các outcome quan trọng:
  - `baseline_bypass`: Teller tự duyệt giao dịch đầu ở Baseline.
  - `denied`: backend từ chối Teller duyệt giao dịch thứ hai.
  - `allowed`: Controller có quyền thực hiện hành động.
  - `success`: giao dịch được Controller phê duyệt thành công.

**Lời trình bày**

> Cùng một endpoint và cùng dữ liệu nghiệp vụ, quyết định thay đổi theo role.
> Teller chỉ tạo giao dịch, Controller mới được duyệt, còn audit lưu lại ai đã
> làm gì, với giao dịch nào và kết quả ra sao.

## 7. Kết quả bắt buộc sau demo

| Giao dịch | Chế độ khi Teller thử duyệt | Trạng thái cuối | Người tạo | Người duyệt |
| --- | --- | --- | --- | --- |
| Thứ nhất | Baseline | Approved | `lan.demo` | `lan.demo` |
| Thứ hai | RBAC | Approved sau khi từng bị 403 | `lan.demo` | `controller01` |

Nếu giao dịch thứ hai chuyển sang Approved ngay sau request của Teller thì demo
không đạt mục tiêu: backend chưa thực thi đúng RBAC hoặc hệ thống chưa ở Secure
Mode.

## 8. Lời kết 30 giây

> Authentication trả lời người dùng là ai. Authorization bằng RBAC quyết định
> role đó được phép làm gì. Quyền được kiểm tra tại backend trước khi thay đổi
> dữ liệu, còn audit log chứng minh quyết định đã thực sự xảy ra.

## 9. Xử lý sự cố

| Hiện tượng | Cách xử lý |
| --- | --- |
| `/health` không trả `{"status":"ok"}` | Kiểm tra Terminal 1 có lỗi hay không; chạy lại lệnh Uvicorn từ thư mục gốc. |
| Đăng nhập báo `Failed to fetch` | Backend chưa chạy hoặc frontend không gọi được cổng 8000; kiểm tra `/health` trước. |
| `__webpack_modules__[moduleId] is not a function` | Dừng Next.js, xóa riêng cache bằng `rm -rf web/.next`, chạy lại `npm run dev`, sau đó hard refresh trình duyệt. |
| Cổng 8000 hoặc 3000 đã được dùng | Chạy `ss -ltnp '( sport = :8000 or sport = :3000 )'`, dừng đúng tiến trình cũ rồi khởi động lại. |
| Teller vẫn thấy `BASELINE` sau khi bật RBAC | Chuyển focus sang tab Teller để ứng dụng tải mode mới; nếu cần, refresh tab. |
| Tạo `lan.demo` báo đã tồn tại | Admin vào **Điều khiển demo**, reset toàn bộ dữ liệu, đăng nhập lại và bắt đầu từ đầu. |
| Controller không thấy giao dịch | Xác nhận giao dịch thứ hai vẫn Pending, mở lại trang **Phê duyệt** hoặc bấm **Tải lại**. |
| Một tab đăng nhập sai vai trò | Mở tab mới trực tiếp từ URL và đăng nhập lại đúng tài khoản; không tiếp tục bằng session cũ. |

## 10. Checklist một phút trước khi trình bày

- [ ] Terminal backend đang chạy và `/health` trả `{"status":"ok"}`.
- [ ] Terminal frontend đang chạy và mở được <http://localhost:3000>.
- [ ] Dữ liệu demo đã reset và Admin đã đăng nhập lại.
- [ ] **Điều khiển demo** đang ở `BASELINE`.
- [ ] Đã mở riêng ba tab Admin, Teller và Controller.
- [ ] Đăng nhập thử được `controller01 / Controller@123`.
- [ ] Chưa tạo `lan.demo`.
- [ ] Dữ liệu giao dịch mẫu ở mục 2 đã sẵn sàng để nhập.
- [ ] Đã biết vị trí **Nhật ký kiểm toán** và ô tìm theo mã giao dịch.
