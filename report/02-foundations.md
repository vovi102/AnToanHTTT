# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT

## 2.1. Kiểm soát truy cập theo vai trò

NIST mô tả RBAC là mô hình trong đó hành động được phép trên tài nguyên được gắn với vai trò thay vì gắn trực tiếp với từng định danh. Core RBAC gồm user, role, permission cùng quan hệ user–role và permission–role; việc quản trị qua vai trò làm giảm sự phức tạp khi số người dùng và quyền thay đổi. PoC sử dụng phần lõi này, chưa triển khai role hierarchy hoặc separation of duty. Nguồn: [NIST RBAC](https://csrc.nist.gov/projects/role-based-access-control), [NIST RBAC FAQ](https://csrc.nist.gov/Projects/role-based-access-control/faqs).

Nguyên tắc quyền tối thiểu yêu cầu mỗi vai trò chỉ nhận các quyền cần cho chức năng. Trong dataset, teller được đọc/cập nhật account nhưng không xóa user; auditor đọc account và audit log; administrator có tập quyền rộng hơn. User disabled không được cấp quyền dù còn quan hệ với role.

## 2.2. Log bảo mật

Authentication log mô tả đăng nhập thành công/thất bại; access log ghi hành động trên tài nguyên; authorization log ghi kết quả kiểm tra quyền. Một sự kiện đơn lẻ thường chưa đủ kết luận: password guessing cần nhóm theo user/IP và thời gian, còn unauthorized access cần đối chiếu resource/action với chính sách RBAC. Log phải giữ timestamp, định danh nguồn và evidence để cảnh báo có thể truy vết.

## 2.3. SQL Injection

SQL Injection xảy ra khi dữ liệu do người dùng kiểm soát làm thay đổi cấu trúc câu SQL. OWASP khuyến nghị prepared statements/parameterized queries là biện pháp phòng ngừa chính; PoC này không thay thế phòng ngừa mà chỉ tìm dấu hiệu trong log như tautology, SQL comment, `UNION SELECT` và stacked query. Regex có tính giải thích nhưng không thể bao phủ mọi phép biến đổi payload. Nguồn: [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html).

## 2.4. Dò đoán mật khẩu

Password guessing được biểu hiện bằng nhiều lần authentication failed có cùng user/IP trong một khoảng thời gian. PoC sắp xếp event theo timestamp, duy trì cửa sổ trượt 300 giây và phát hiện khi có ít nhất năm lần thất bại. Đăng nhập thành công làm kết thúc chuỗi trước đó; các lần thất bại phân tán ngoài cửa sổ không tạo cảnh báo.

## 2.5. Chỉ số đánh giá

`TP` là event tấn công được phát hiện, `FP` là event bình thường bị cảnh báo, `FN` là event tấn công bị bỏ sót và `TN` là event bình thường không bị cảnh báo. Precision đo tỷ lệ cảnh báo đúng trong số cảnh báo đã tạo; recall đo tỷ lệ tấn công được tìm thấy; F1 là trung bình điều hòa của precision và recall. Kết quả được tính tự động từ `expected_label` và `event_ids`.

