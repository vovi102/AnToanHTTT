# User journey demo RBAC — Nova Bank

Kịch bản này trình bày một case chuyển khoản 50.000.000 VND trong vài phút cho
giảng viên. Mục tiêu là quan sát được cả nghiệp vụ, thay đổi dữ liệu thật và
quyết định phân quyền từ backend.

## Tài khoản và ba tab

Mở ba tab trực tiếp tới <http://localhost:3000>; mỗi tab dùng `sessionStorage`
riêng nên giữ một token backend độc lập.

| Tab | Tài khoản | Vai trò |
| --- | --- | --- |
| Admin | `admin01 / Admin@123` | Quản trị viên |
| Teller | `lan.demo / Lan@1234` | Được tạo trực tiếp khi demo |
| Controller | `controller01 / Controller@123` | Kiểm soát viên seed sẵn |

## Case duy nhất cần trình bày

### 1. Admin tạo giao dịch viên

1. Đăng nhập tab Admin.
2. Mở **Nhân viên**.
3. Giữ dữ liệu mẫu `Lan Nguyễn / lan.demo / Lan@1234 / Giao dịch viên`.
4. Bấm **Tạo tài khoản và gán vai trò**.

Lời nói ngắn:

> Tài khoản này vừa được gửi tới FastAPI, mật khẩu được băm và role Teller được
> lưu vào SQLite. Đây không phải user viết cứng trong giao diện.

### 2. Trước RBAC — Teller tự phê duyệt

1. Tab Admin mở **Điều khiển demo** và xác nhận trạng thái **Baseline**.
2. Tab Teller đăng nhập `lan.demo / Lan@1234`.
3. Giữ form mẫu chuyển 50.000.000 VND cho Lê Bình và bấm **Tạo yêu cầu**.
4. Bấm **Tự phê duyệt giao dịch** rồi xác nhận.
5. Quan sát giao dịch thứ nhất chuyển từ Pending sang Approved, người tạo và
   người duyệt đều là `lan.demo`.

Lời nói ngắn:

> Khi chưa áp dụng RBAC, hệ thống biết Lan là ai nhưng không tách quyền tạo và
> duyệt. Một người hoàn tất cả hai bước, tạo ra rủi ro gian lận.

### 3. Admin bật RBAC

1. Quay lại tab Admin, mở **Điều khiển demo**.
2. Bấm **Bật bảo vệ RBAC** và xác nhận.
3. Quan sát banner chuyển sang `SECURE MODE`.

Lời nói ngắn:

> Chính sách được lưu tại backend. Việc đổi chế độ cũng được ghi audit, không
> phải một hiệu ứng giao diện.

### 4. Sau RBAC — backend chặn Teller

1. Quay lại tab Teller; khi tab nhận focus, mode và dữ liệu được tải lại.
2. Tạo giao dịch 50.000.000 VND thứ hai bằng cùng form mẫu.
3. Nút phê duyệt bình thường không còn xuất hiện.
4. Mở **Kiểm tra bảo vệ backend** trên giao dịch Pending.
5. Bấm **Gửi thử request vượt quyền**.
6. Quan sát `POST /transactions/{reference}/approve → HTTP 403` và permission
   `transactions:approve`; trạng thái vẫn Pending.

Lời nói ngắn:

> Giao diện ẩn tác vụ để đúng trải nghiệm Teller, nhưng tôi vẫn cố ý gọi API.
> Backend mới là lớp bảo vệ thật: trả 403 và không thay đổi giao dịch.

### 5. Controller phê duyệt và đối chiếu audit

1. Đăng nhập tab Controller bằng `controller01 / Controller@123`.
2. Mở **Phê duyệt**, chọn giao dịch Pending và xác nhận.
3. Quan sát trạng thái thành Approved, `approved_by = controller01`.
4. Quay lại Admin, mở **Nhật ký kiểm toán**.
5. Lọc hoặc tìm mã giao dịch để chỉ ra `baseline_bypass`, `denied`, `allowed`
   và `success`.

Lời kết:

> Authentication trả lời người dùng là ai. RBAC quyết định vai trò đó được làm
> gì. Quyền được kiểm tra tại backend trước khi thay đổi trạng thái nghiệp vụ,
> còn audit log chứng minh quyết định đã thực sự xảy ra.

## Kết quả cuối buổi

- Giao dịch thứ nhất: Approved bởi chính Teller trong Baseline.
- Giao dịch thứ hai: từng bị Teller từ chối với 403, sau đó Approved bởi
  Controller.
- Audit log có đầy đủ actor, role, transaction reference, outcome và thời gian.
