# CHƯƠNG 3. THIẾT KẾ HỆ THỐNG

## 3.1. Kiến trúc tổng quan

```text
CLI ───────────┐
               ├─> Application Service ─> Parser ─> Detection Engine ─> Scorer ─> Reporter
Streamlit UI ──┘                              │             │
                                         CSV/JSON      SQLite RBAC
```

CLI và Streamlit là adapter; toàn bộ logic nằm trong service và module lõi. `parser.py` chuẩn hóa dữ liệu, `rules.py` chạy ba nhóm luật, `scoring.py` tạo Alert và `reporting.py` ghi file nguyên tử. Thiết kế này bảo đảm kết quả UI và CLI không khác nhau do sao chép logic.

## 3.2. Mô hình RBAC

```text
users --< user_roles >-- roles --< role_permissions >-- permissions
```

`users.username`, `roles.name` và `(permissions.resource, permissions.action)` là duy nhất. Hai bảng liên kết có khóa chính ghép và khóa ngoại. SQLite bật foreign key cho mọi connection; seed chạy trong transaction, hỗ trợ chạy lại và rollback nếu tham chiếu tên không tồn tại.

## 3.3. Data contract

Event gồm `event_id`, `timestamp`, `event_type`, `user`, `ip`, `resource`, `action`, `status`, `request`, `details`, `expected_label`. Ba event type hợp lệ là authentication, access và authorization. `expected_label` chỉ phục vụ dataset đánh giá, không được detection engine đọc khi dự đoán.

## 3.4. Detection rules

`SQLInjectionRule` compile sẵn bốn nhóm regex và dừng ở pattern đầu tiên của mỗi event. `PasswordGuessingRule` nhóm theo `(user, ip)`, sắp xếp theo thời gian và tìm cửa sổ đạt ngưỡng. `UnauthorizedAccessRule` chỉ xử lý access/authorization có user, sau đó gọi `RBACRepository.has_permission` và kết hợp với trạng thái denied trong log. `DetectionEngine` hợp nhất findings theo timestamp, risk type và rule ID để output ổn định.

## 3.5. Risk scoring

Điểm nền lần lượt là 45 cho SQL Injection, 40 cho password guessing và 50 cho unauthorized access. Hệ thống cộng tối đa 20 điểm confidence, 15 điểm số lần lặp và 15 điểm khi RBAC từ chối, sau đó giới hạn 0–100. Ngưỡng severity là Medium từ 30, High từ 60 và Critical từ 85.

## 3.6. Xử lý lỗi và kiểm thử

File thiếu header hoặc sai loại bị từ chối; dòng sai timestamp được tách thành RowError. Reporter ghi file tạm rồi replace để tránh artifact dở dang. Unit test kiểm tra từng module, integration test chạy từ dataset đến artifact, còn subprocess test xác nhận exit code và thông báo CLI không làm lộ traceback.

