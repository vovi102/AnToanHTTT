# User journey demo RBAC — BankSafe

Tài liệu này là kịch bản để trình bày trực tiếp ý nghĩa của Role-Based Access
Control (RBAC) qua ứng dụng ngân hàng mẫu BankSafe.

## 1. Khởi động backend và giao diện

Tại thư mục gốc dự án, chạy:

```bash
uv sync --extra api
uv run uvicorn rbac_guard.api:app --reload --port 8000
```

Mở terminal thứ hai:

```bash
cd web
npm install
npm run dev
```

Mở trình duyệt tại <http://localhost:3000>. Backend chạy ở
<http://localhost:8000>; dữ liệu được lưu vào SQLite.

## 2. Đăng nhập quản trị viên và tạo nhân viên

1. Đăng nhập `admin01` với mật khẩu `Admin@123`.
2. Mở **Quản lý người dùng**.
3. Tạo `lan.demo`, đặt mật khẩu `Lan@1234`, chọn role **Giao dịch viên**.

**Điểm cần nói:** Tài khoản và role vừa được gửi đến FastAPI, băm mật khẩu và
lưu vào SQLite. Đây không phải danh sách người dùng cố định trong giao diện.

## 3. Đăng nhập bằng tài khoản vừa tạo

1. Đăng xuất admin.
2. Đăng nhập `lan.demo / Lan@1234`.
3. Mở **Khách hàng**, thay đổi số điện thoại hoặc địa chỉ, rồi bấm lưu.

Giao diện hiện `PATCH /accounts/{id} → HTTP 200`; thay đổi được lưu thật trong
SQLite.

**Điểm cần nói:** Backend nhận ra Lan thuộc role Giao dịch viên và kiểm tra
quyền `accounts:update` trước khi ghi dữ liệu.

## 4. Chứng minh backend chặn vượt quyền

1. Khi vẫn đăng nhập bằng Lan, bấm **Quản lý người dùng**.
2. Giao diện gọi `GET /users`, nhưng hiện `HTTP 403 · cần users:manage`.

**Điểm cần nói:** Nút vẫn gửi request đến backend. Chỉ server quyết định quyền,
vì vậy không thể vượt quyền bằng cách mở URL hay gọi API trực tiếp.

## 5. Kiểm toán bằng chứng

1. Đăng nhập lại `admin01 / Admin@123`.
2. Mở **Nhật ký kiểm toán**.
3. Quan sát các dòng `success`, `allowed` và `denied`: đăng nhập Lan, cập nhật
khách hàng và lần bị chặn `users:manage`.

**Điểm cần nói:** Audit log lấy trực tiếp từ SQLite, chứng minh kết quả không
chỉ là thông báo trên trình duyệt.

## 6. Kịch bản Kiểm toán viên và đặt lại

Tạo một user role **Kiểm toán viên** rồi đăng nhập user này để xem audit log;
role này không thể quản lý người dùng hoặc cập nhật khách hàng. Cuối buổi, admin
chọn **Đặt lại dữ liệu demo** để trở về tài khoản bootstrap và xóa dữ liệu thử.

## Thông điệp kết thúc

> RBAC đảm bảo đúng người, đúng vai trò, đúng quyền. Đăng nhập xác định người
> dùng là ai; vai trò quyết định người dùng được làm gì; hệ thống kiểm tra quyền
> trước mỗi thao tác quan trọng.
