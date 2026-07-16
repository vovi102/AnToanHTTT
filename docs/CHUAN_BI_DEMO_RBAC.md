# Chuẩn bị trước khi demo RBAC Nova Bank

Demo cần FastAPI ở cổng `8000` và Next.js ở cổng `3000`. Thực hiện checklist
này trước khi trình bày.

## 1. Cài phụ thuộc lần đầu

Tại thư mục gốc:

```bash
uv sync --extra api
```

Tại thư mục frontend:

```bash
cd web
npm install
```

## 2. Kiểm tra code trước buổi demo

```bash
UV_CACHE_DIR=.uv-cache uv run pytest -q
cd web
npm test
npm run build
```

Kỳ vọng: 78 Python tests pass, 7 frontend tests pass và Next.js build thành
công.

## 3. Chạy backend — Terminal 1

```bash
UV_CACHE_DIR=.uv-cache uv run uvicorn rbac_guard.api:app --reload --host 127.0.0.1 --port 8000
```

Chỉ tiếp tục khi <http://127.0.0.1:8000/health> trả JSON có
`"status":"ok"`.

## 4. Chạy frontend — Terminal 2

```bash
cd web
npm run dev
```

Mở <http://localhost:3000>. Không đóng hai terminal trong lúc demo.

## 5. Đặt lại và chuẩn bị ba tab

1. Đăng nhập Admin `admin01 / Admin@123`.
2. Vào **Điều khiển demo**, chọn **Đặt lại toàn bộ dữ liệu demo** nếu đã từng
   chạy thử. Sau reset, đăng nhập Admin lại.
3. Xác nhận mode là **Baseline**.
4. Mở ba tab trực tiếp tới <http://localhost:3000> và đặt tên để dễ chuyển:
   Admin, Teller, Controller.
5. Controller seed sẵn: `controller01 / Controller@123`.
6. Không tạo `lan.demo` trước; tài khoản này cần được tạo trực tiếp khi trình
   bày để chứng minh backend hoạt động.

## 6. Dữ liệu form chuẩn

```text
Teller: lan.demo / Lan@1234
Nguồn: 001100001234
Đích: 002200005678
Người nhận: Lê Bình
Số tiền: 50000000
Nội dung: Thanh toán hợp đồng
```

## Xử lý lỗi thường gặp

| Hiện tượng | Cách xử lý |
| --- | --- |
| Không thể kết nối máy chủ khi login | Kiểm tra Terminal 1 và mở `/health`. |
| `Failed to fetch` trong DevTools | Backend chưa chạy hoặc sai `NEXT_PUBLIC_API_BASE_URL`. |
| `__webpack_modules__[moduleId] is not a function` | Dừng Next.js, xóa `web/.next`, chạy lại `npm run dev`, rồi hard refresh. |
| Cổng 8000 hoặc 3000 đã được dùng | Dừng tiến trình cũ hoặc đổi cổng tương ứng. |
| Teller vẫn thấy Baseline sau khi Admin bật RBAC | Chuyển sang tab Teller để sự kiện focus tải mode mới; nếu cần bấm Tải lại. |
| Tạo `lan.demo` báo đã tồn tại | Admin dùng **Đặt lại toàn bộ dữ liệu demo**, đăng nhập lại và chạy từ đầu. |
| Controller không thấy giao dịch | Xác nhận giao dịch thứ hai đang Pending và bấm Tải lại ở hàng đợi. |

Kịch bản lời thoại đầy đủ nằm tại `docs/USER_JOURNEY_DEMO_RBAC.md`.
