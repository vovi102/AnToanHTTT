# Hướng dẫn và kịch bản demo RBAC Nova Bank

Tài liệu này là nguồn hướng dẫn duy nhất cho demo giao diện Nova Bank. Thời
lượng mục tiêu là 5–7 phút, dành cho phần trình bày trước giảng viên.

## 1. Demo này chứng minh điều gì?

Một giao dịch viên tạo yêu cầu chuyển khoản 50.000.000 VND. Với **Kiểm soát cơ
bản**, người này có thể hoàn tất giao dịch do hệ thống chưa tách quyền. Sau khi
áp dụng **Phân tách nhiệm vụ**, backend từ chối khi Teller truy cập trực tiếp
trang phê duyệt; chỉ Controller mới phê duyệt được. Lịch sử hoạt động lưu lại
toàn bộ quyết định.

Luồng trình bày duy nhất:

```text
Admin tạo Teller
      ↓
Teller tạo và hoàn tất giao dịch với Kiểm soát cơ bản
      ↓
Admin áp dụng Phân tách nhiệm vụ
      ↓
Teller mở trực tiếp trang phê duyệt → không có quyền truy cập
      ↓
Controller phê duyệt → Admin kiểm tra lịch sử hoạt động
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
| Tài khoản nhận | `002200005678` |
| Người thụ hưởng | `Lê Bình` |
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
2. Chọn **Chính sách phê duyệt** trên menu.
3. Bấm **Khôi phục dữ liệu** và xác nhận.
4. Khôi phục dữ liệu sẽ xóa phiên hiện tại; đăng nhập lại Admin.
5. Vào **Chính sách phê duyệt** và xác nhận chính sách hiện tại là **Kiểm soát
   cơ bản**.
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
   - Vai trò: **Giao dịch viên**
3. Bấm **Tạo tài khoản và gán vai trò**.

**Kết quả cần thấy**

- Giao diện báo tạo tài khoản thành công.
- `lan.demo` xuất hiện trong **Danh sách nhân viên** với vai trò Giao dịch viên.

**Lời trình bày**

> Admin vừa gửi dữ liệu tới FastAPI. Backend băm mật khẩu, tạo tài khoản và lưu
> role Teller trong SQLite. Đây không phải tài khoản viết cứng ở giao diện.

### Bước 2 — Kiểm soát cơ bản cho phép Teller hoàn tất giao dịch

**Thao tác**

1. Ở tab Teller, đăng nhập `lan.demo / Lan@1234`.
2. Chọn **Giao dịch** và nhập dữ liệu mẫu ở mục 2.
3. Bấm **Tạo yêu cầu chuyển khoản**.
4. Tại giao dịch vừa tạo, bấm **Hoàn tất giao dịch** và xác nhận.
5. Ghi lại hoặc đọc to mã giao dịch thứ nhất để đối chiếu lịch sử hoạt động về
   sau.

**Kết quả cần thấy**

- Giao dịch chuyển từ **Chờ phê duyệt** sang **Đã phê duyệt**.
- Người tạo và người duyệt đều là `lan.demo`.
- Chính sách trên cùng vẫn là **Kiểm soát cơ bản**.

**Lời trình bày**

> Hệ thống đã xác thực Lan là ai, nhưng với Kiểm soát cơ bản chưa tách quyền tạo
> và quyền duyệt. Một người có thể hoàn tất cả hai bước, tạo ra rủi ro gian lận.

### Bước 3 — Admin áp dụng Phân tách nhiệm vụ

**Thao tác**

1. Quay lại tab Admin và mở **Chính sách phê duyệt**.
2. Bấm **Áp dụng phân tách nhiệm vụ** và xác nhận.

**Kết quả cần thấy**

- Chính sách hiện tại chuyển thành **Phân tách nhiệm vụ**.
- Chính sách trên cùng hiển thị **Phân tách nhiệm vụ**.

**Lời trình bày**

> Chính sách vừa được thay đổi tại backend và thao tác này cũng được ghi vào
> lịch sử hoạt động. Đây không phải hiệu ứng đổi màu hoặc ẩn nút riêng ở
> frontend.

### Bước 4 — Teller bị từ chối tại trang phê duyệt

**Thao tác**

1. Chuyển sang tab Teller. Khi tab nhận focus, ứng dụng tải lại chính sách.
2. Tạo giao dịch thứ hai với cùng dữ liệu mẫu.
3. Sao chép hoặc ghi lại mã giao dịch thứ hai.
4. Trong cùng tab Teller, mở
   `http://localhost:3000/approvals/<reference>`, thay `<reference>` bằng mã vừa
   ghi lại.
5. Quan sát trang báo **Không có quyền truy cập**.
6. Bấm **Quay lại giao dịch** và xác nhận giao dịch vẫn **Chờ phê duyệt**.

**Kết quả cần thấy**

- Teller thấy **Không có quyền truy cập** tại đúng URL của giao dịch thứ hai.
- Giao dịch thứ hai vẫn là **Chờ phê duyệt** và chưa có người duyệt.

**Lời trình bày**

> Teller đã biết đường dẫn của một hồ sơ cụ thể nhưng vẫn không thể xem trang
> phê duyệt. Backend từ chối quyền truy cập và dữ liệu giao dịch không thay đổi.

### Bước 5 — Controller duyệt và Admin kiểm tra lịch sử hoạt động

**Thao tác**

1. Ở tab Controller, đăng nhập `controller01 / Controller@123`.
2. Chọn **Phê duyệt**.
3. Tìm giao dịch thứ hai đang **Chờ phê duyệt**, bấm **Xem và phê duyệt**, sau
   đó bấm **Phê duyệt giao dịch**.
4. Quay lại tab Admin, chọn **Nhật ký kiểm toán**, sau đó xác nhận trang
   **Lịch sử hoạt động** đã mở.
5. Nhập mã giao dịch vào ô tìm kiếm và đối chiếu các kết quả audit.

**Kết quả cần thấy**

- Giao dịch thứ hai chuyển thành **Đã phê duyệt**.
- Người duyệt là `controller01`, khác người tạo `lan.demo`.
- Lịch sử hoạt động hiển thị các kết quả quan trọng cho giao dịch thứ hai:
  - **Đã từ chối** khi Teller mở trang phê duyệt.
  - **Đã cho phép** khi Controller xem hồ sơ phê duyệt.
  - **Thành công** khi Controller phê duyệt giao dịch.

**Lời trình bày**

> Cùng một endpoint và cùng dữ liệu nghiệp vụ, quyết định thay đổi theo role.
> Teller chỉ tạo giao dịch, Controller mới được duyệt, còn audit lưu lại ai đã
> làm gì, với giao dịch nào và kết quả ra sao.

## 7. Kết quả bắt buộc sau demo

| Giao dịch | Chế độ khi Teller thử duyệt | Trạng thái cuối | Người tạo | Người duyệt |
| --- | --- | --- | --- | --- |
| Thứ nhất | Kiểm soát cơ bản | Đã phê duyệt | `lan.demo` | `lan.demo` |
| Thứ hai | Phân tách nhiệm vụ | Đã phê duyệt sau khi Teller bị từ chối | `lan.demo` | `controller01` |

Nếu Teller xem được trang phê duyệt hoặc giao dịch thứ hai đổi trạng thái sau
lần truy cập đó thì demo không đạt mục tiêu: backend chưa thực thi đúng RBAC
hoặc chưa áp dụng Phân tách nhiệm vụ.

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
| Teller vẫn thấy **Kiểm soát cơ bản** sau khi đổi chính sách | Chuyển focus sang tab Teller để ứng dụng tải chính sách mới; nếu cần, refresh tab. |
| Tạo `lan.demo` báo đã tồn tại | Admin vào **Chính sách phê duyệt**, khôi phục dữ liệu, đăng nhập lại và bắt đầu từ đầu. |
| Controller không thấy giao dịch | Xác nhận giao dịch thứ hai vẫn **Chờ phê duyệt**, mở lại trang **Phê duyệt** hoặc bấm **Tải lại**. |
| Một tab đăng nhập sai vai trò | Mở tab mới trực tiếp từ URL và đăng nhập lại đúng tài khoản; không tiếp tục bằng session cũ. |

## 10. Checklist một phút trước khi trình bày

- [ ] Terminal backend đang chạy và `/health` trả `{"status":"ok"}`.
- [ ] Terminal frontend đang chạy và mở được <http://localhost:3000>.
- [ ] Dữ liệu đã được khôi phục và Admin đã đăng nhập lại.
- [ ] **Chính sách phê duyệt** đang ở **Kiểm soát cơ bản**.
- [ ] Đã mở riêng ba tab Admin, Teller và Controller.
- [ ] Đăng nhập thử được `controller01 / Controller@123`.
- [ ] Chưa tạo `lan.demo`.
- [ ] Dữ liệu giao dịch mẫu ở mục 2 đã sẵn sàng để nhập.
- [ ] Đã biết vị trí menu **Nhật ký kiểm toán**, trang **Lịch sử hoạt động** và
      ô tìm theo mã giao dịch.
