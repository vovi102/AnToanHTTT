# Chuẩn bị trước khi demo RBAC

Demo này cần **hai dịch vụ cùng chạy**: backend FastAPI ở cổng `8000` và giao
diện Next.js ở cổng `3000`. Nếu thiếu backend, nút Đăng nhập sẽ báo
`Failed to fetch`.

## 1. Cài phụ thuộc (chỉ cần làm lần đầu)

Tại thư mục gốc dự án:

```bash
uv sync --extra api
```

Tại thư mục giao diện:

```bash
cd web
npm install
```

## 2. Chạy backend — Terminal 1

Mở một terminal tại thư mục gốc dự án và giữ lệnh này chạy trong suốt buổi demo:

```bash
UV_CACHE_DIR=.uv-cache uv run uvicorn rbac_guard.api:app --reload --host 127.0.0.1 --port 8000
```

Chỉ tiếp tục khi terminal hiện:

```text
Uvicorn running on http://127.0.0.1:8000
```

Kiểm tra nhanh bằng trình duyệt: <http://127.0.0.1:8000/health>. Trang phải
trả về JSON, ví dụ `{"status":"ok"}`.

## 3. Chạy giao diện — Terminal 2

Mở terminal thứ hai:

```bash
cd web
npm run dev
```

Mở <http://localhost:3000> khi terminal hiện địa chỉ Local.

## 4. Tài khoản để bắt đầu demo

```text
Username: admin01
Mật khẩu: Admin@123
```

Đăng nhập bằng tài khoản này để tạo một nhân viên mới, gán role, sau đó đăng
xuất và đăng nhập lại bằng tài khoản nhân viên vừa tạo.

## Xử lý lỗi thường gặp

| Hiện tượng | Cách xử lý |
| --- | --- |
| `Failed to fetch` khi đăng nhập | Backend chưa chạy. Thực hiện lại bước 2 và kiểm tra `/health`. |
| `__webpack_modules__[moduleId] is not a function` | Dừng Next.js, chạy `rm -rf web/.next`, sau đó `cd web && npm run dev`; hard refresh trình duyệt (`Ctrl + Shift + R`). |
| Cổng 8000 đã được dùng | Dừng tiến trình FastAPI cũ, rồi chạy lại lệnh ở bước 2. |
