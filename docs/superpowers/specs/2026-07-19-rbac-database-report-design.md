# Thiết kế phần cơ sở dữ liệu RBAC trong báo cáo

## Mục tiêu

Mở rộng mục "Mô hình dữ liệu RBAC" trong báo cáo kỹ thuật LaTeX để người đọc
hiểu được cả mô hình Core RBAC và cách mô hình này liên kết với dữ liệu vận hành
của demo Nova Bank. Nội dung phải phản ánh đúng schema SQLite trong
`src/rbac_guard/rbac.py` và không thay đổi database hay mã nguồn ứng dụng.

## Phạm vi

Phần bổ sung nằm trong chương "Kiến trúc hệ thống". Thiết kế dữ liệu được trình
bày theo hai lớp để bảo đảm đầy đủ mà sơ đồ vẫn dễ đọc:

1. Lớp Core RBAC gồm `users`, `roles`, `permissions`, `user_roles` và
   `role_permissions`.
2. Lớp tích hợp Nova Bank gồm `sessions`, `transactions`, `audit_logs`,
   `customer_accounts` và `demo_settings`, đồng thời thể hiện các quan hệ trực
   tiếp với `users`.

## Nội dung báo cáo

### Sơ đồ dữ liệu

Tạo hai hình TikZ/LaTeX độc lập:

- ERD Core RBAC thể hiện khóa chính, khóa ngoại và hai quan hệ nhiều--nhiều
  User--Role và Role--Permission thông qua bảng liên kết.
- ERD tích hợp thể hiện `users` sở hữu nhiều `sessions`, tạo và có thể phê duyệt
  nhiều `transactions`; `audit_logs` lưu `username` và `role_at_event` như ảnh
  chụp phục vụ điều tra thay vì khóa ngoại. `customer_accounts` và
  `demo_settings` là bảng độc lập trong schema hiện tại.

Các hình được đặt trong `report/technical-report/figures/` và được nhúng vào
`chapters/02-architecture.tex`.

### Mô tả bảng và ràng buộc

Bổ sung bảng tóm tắt cho cả mười quan hệ, nêu mục đích, khóa chính và ràng buộc
quan trọng. Nội dung phải ghi rõ:

- `username`, tên role và cặp `resource, action` là duy nhất.
- Hai bảng liên kết dùng khóa chính ghép, ngăn gán trùng.
- Trạng thái user, giao dịch và outcome audit dùng `CHECK` giới hạn miền giá trị.
- `transactions.created_by` bắt buộc tham chiếu user;
  `transactions.approved_by` có thể rỗng khi giao dịch đang chờ.
- Token phiên được lưu dưới dạng SHA-256; mật khẩu được băm bằng scrypt cùng salt
  ngẫu nhiên.
- SQLite bật kiểm tra khóa ngoại trên từng kết nối; thao tác seed và thay đổi dữ
  liệu tận dụng transaction của connection context.

### Luồng kiểm tra quyền

Diễn giải đường tra cứu `users -> user_roles -> roles -> role_permissions ->
permissions`. Quyền chỉ được cấp khi user có trạng thái `active` và tồn tại cặp
`resource:action` tương ứng. Backend là nơi đưa ra quyết định cuối cùng; việc ẩn
nút trên frontend không thay thế kiểm tra quyền tại API.

Phần này cũng phân biệt constraint cấu trúc của database với chính sách nghiệp
vụ Maker--Checker: permission `transactions:approve` thuộc Controller, còn API
thực hiện quy tắc phê duyệt. Không tuyên bố database đã triển khai Separation of
Duty tổng quát vì PoC chưa có bảng constraint chuyên biệt.

## Kiểm chứng

- Đối chiếu tên bảng, cột và ràng buộc với hằng `SCHEMA` trong
  `src/rbac_guard/rbac.py`.
- Biên dịch báo cáo bằng `latexmk -pdf -interaction=nonstopmode -halt-on-error
  main.tex` từ `report/technical-report`.
- Kiểm tra không còn placeholder và mọi `label`/`ref` mới đều hợp lệ.

## Ngoài phạm vi

- Không thay đổi schema SQLite, seed data, API hoặc giao diện.
- Không thêm role hierarchy, session activation, separation-of-duty constraint
  hay cơ chế migration mới.
- Không mô tả `audit_logs.username` là khóa ngoại, vì schema hiện tại chủ ý lưu
  dấu vết văn bản tại thời điểm sự kiện.
