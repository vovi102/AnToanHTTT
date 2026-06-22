# Đặc tả PoC RBAC và phân tích log dựa trên luật

## 1. Mục tiêu

Xây dựng một PoC bằng Python để mô hình hóa RBAC, phân tích log bảo mật và phát hiện ba nhóm rủi ro trong bối cảnh ngân hàng điện tử: SQL Injection, dò đoán mật khẩu và truy cập trái quyền. PoC phải chạy hoàn chỉnh bằng CLI, có kiểm thử tự động, tạo được bằng chứng thực nghiệm và cung cấp đầu vào chính xác cho báo cáo sáu chương.

Web UI bằng Streamlit là mục tiêu phụ có điều kiện. UI chỉ được triển khai sau khi lõi xử lý, CLI và toàn bộ kiểm thử bắt buộc đã hoàn thành.

## 2. Phạm vi

### Trong phạm vi

- Mô hình RBAC lưu bằng SQLite.
- Log giả lập đầu vào ở định dạng CSV và JSON.
- CLI để khởi tạo dữ liệu, kiểm tra quyền, phân tích log và xuất cảnh báo.
- Luật phát hiện SQL Injection, password guessing và unauthorized access.
- Chấm điểm rủi ro và phân loại `Low`, `Medium`, `High`, `Critical`.
- Kết quả cảnh báo ở định dạng CSV và JSON.
- Unit test, integration test và scenario test.
- Đánh giá bằng confusion matrix, precision, recall, F1-score và thời gian xử lý.
- Báo cáo sáu chương được viết dựa trên thiết kế, mã nguồn và kết quả chạy thực tế.

### Ngoài phạm vi

- Hệ thống ngân hàng điện tử thật hoặc dữ liệu khách hàng thật.
- Machine learning, SIEM và xử lý streaming thời gian thực.
- Web UI có đăng nhập, quản trị RBAC, chỉnh sửa luật hoặc phân quyền riêng.
- Triển khai production, cloud hoặc tích hợp hệ thống bên ngoài.

## 3. Kiến trúc

PoC tách giao diện khỏi lõi nghiệp vụ. CLI và Streamlit gọi cùng các application service; không giao diện nào được chứa logic phát hiện riêng.

```text
CLI ───────────┐
               ├─> Application Services ─> RBAC Checker ───┐
Streamlit UI ──┘                         ├─> Log Parser      ├─> Risk Scoring ─> Alert CSV/JSON
                                        └─> Detection Rules┘
                                               │
                                            SQLite
```

Các thành phần có trách nhiệm độc lập:

- `RBAC repository`: khởi tạo schema và truy vấn dữ liệu quyền trong SQLite.
- `RBAC checker`: trả lời user có quyền thực hiện action trên resource hay không.
- `Log parser`: đọc CSV/JSON, chuẩn hóa sự kiện và cô lập các dòng lỗi.
- `Detection engine`: chạy từng luật trên sự kiện đã chuẩn hóa.
- `Risk scorer`: tính điểm và severity từ các phát hiện.
- `Alert reporter`: xuất cảnh báo và metadata của lần chạy.
- `CLI`: cung cấp các lệnh khởi tạo, kiểm tra quyền và phân tích log.
- `Streamlit UI`: tải log, chạy phân tích, lọc kết quả và tải báo cáo; đây là thành phần tùy chọn.

## 4. Mô hình dữ liệu

### SQLite RBAC

- `users(id, username, status)`; `username` là duy nhất.
- `roles(id, name)`; `name` là duy nhất.
- `permissions(id, resource, action)`; cặp `(resource, action)` là duy nhất.
- `user_roles(user_id, role_id)`; khóa chính ghép và khóa ngoại tới user/role.
- `role_permissions(role_id, permission_id)`; khóa chính ghép và khóa ngoại tới role/permission.

Tài khoản chỉ được cấp quyền khi `status = active` và tồn tại đường liên kết user → role → permission khớp chính xác `resource` và `action`.

### Sự kiện log chuẩn hóa

Mỗi sự kiện hợp lệ gồm:

- `timestamp`: thời điểm theo ISO 8601.
- `event_type`: `authentication`, `access` hoặc `authorization`.
- `user`: định danh người dùng; có thể rỗng với đăng nhập không xác định.
- `ip`: địa chỉ nguồn.
- `resource`: tài nguyên được truy cập.
- `action`: hành động trên tài nguyên.
- `status`: kết quả như `success`, `failed`, `allowed`, `denied`.
- `request`: request hoặc chuỗi đầu vào cần kiểm tra.
- `details`: dữ liệu bổ sung.
- `expected_label`: nhãn chuẩn chỉ dùng trong tập dữ liệu đánh giá.

Parser từ chối file thiếu header bắt buộc. Dòng riêng lẻ sai timestamp hoặc sai kiểu được ghi vào danh sách lỗi và không làm dừng toàn bộ lần chạy.

## 5. Luật phát hiện

### SQL Injection

Kiểm tra trường `request` bằng các nhóm mẫu tách biệt: tautology, SQL comment, `UNION SELECT`, stacked query và từ khóa SQL kết hợp ký tự bất thường. Mỗi kết quả phải chứa mã luật, mẫu khớp và phần request làm bằng chứng.

### Password guessing

Nhóm các lần đăng nhập `failed` theo user và IP trong một time window cấu hình được. Cảnh báo được tạo khi số lần thất bại đạt ngưỡng; bằng chứng gồm khoảng thời gian, số lần và danh sách event liên quan.

### Unauthorized access

Với sự kiện access/authorization, đối chiếu `user`, `resource`, `action` với RBAC checker. Tạo cảnh báo nếu RBAC không cấp quyền hoặc log ghi nhận trạng thái `denied`. Bằng chứng phải nêu quyền được yêu cầu và kết quả kiểm tra.

Ngưỡng và time window có giá trị mặc định cố định cho bộ dữ liệu demo, đồng thời được lưu trong metadata kết quả để thí nghiệm có thể tái lập.

## 6. Chấm điểm và đầu ra

Điểm cảnh báo được tính từ điểm nền theo loại rủi ro, độ tin cậy của dấu hiệu, số lần lặp và kết quả kiểm tra RBAC. Điểm cuối được giới hạn trong khoảng 0–100 rồi ánh xạ sang bốn severity bằng các ngưỡng duy nhất được định nghĩa trong cấu hình.

Mỗi cảnh báo gồm:

- `alert_id`, `timestamp`, `rule_id`, `risk_type`;
- `user`, `ip`, `resource`, `action`;
- `evidence`, `risk_score`, `severity`;
- các định danh sự kiện nguồn để truy vết.

Mỗi lần chạy còn tạo metadata gồm thời điểm chạy, file nguồn, cấu hình luật, tổng dòng, số dòng hợp lệ, số dòng lỗi và số cảnh báo.

## 7. Giao diện vận hành

### CLI bắt buộc

CLI hỗ trợ tối thiểu:

- khởi tạo database và nạp dữ liệu RBAC mẫu;
- kiểm tra một bộ `user/action/resource`;
- phân tích file CSV hoặc JSON;
- chọn thư mục đầu ra;
- in tóm tắt lần chạy và trả exit code khác 0 khi lỗi cấp file/database.

### Streamlit tùy chọn

Chỉ bắt đầu khi CLI và test bắt buộc đã đạt tiêu chí hoàn thành. UI hỗ trợ tải file, chạy phân tích, xem/lọc bảng cảnh báo, xem số lượng theo risk type và severity, tải CSV/JSON. UI không thay đổi SQLite hoặc cấu hình luật.

## 8. Kiểm thử và đánh giá

- Unit test cho schema/repository, RBAC checker, parser, từng nhóm luật, scorer và reporter.
- Integration test từ file log đầu vào đến SQLite lookup và alert đầu ra.
- Scenario test cho hoạt động hợp lệ, SQL Injection rõ ràng và biến thể, password guessing, unauthorized access, dữ liệu biên và sự kiện bình thường dễ gây cảnh báo sai.
- Đánh giá theo từng risk type với `TP`, `FP`, `FN`, `TN`, precision, recall và F1-score.
- Đo thời gian xử lý trên tập dữ liệu demo với cùng cấu hình và môi trường.

Tiêu chí lõi hoàn thành: CLI chạy lại được từ môi trường sạch; toàn bộ test bắt buộc pass; ba nhóm rủi ro đều có ít nhất một kịch bản dương tính và âm tính; báo cáo cảnh báo có bằng chứng giải thích được; số liệu đánh giá được sinh từ dữ liệu có nhãn thay vì nhập thủ công.

## 9. Xử lý lỗi

- File không tồn tại, sai định dạng hoặc thiếu trường bắt buộc: dừng lệnh với thông báo ngắn gọn và exit code khác 0.
- Dòng log lỗi: cô lập, thống kê và tiếp tục các dòng hợp lệ.
- Database chưa khởi tạo hoặc vi phạm ràng buộc: rollback transaction và báo hành động khắc phục.
- Streamlit: hiển thị thông báo thân thiện, không lộ stack trace.
- Không có cảnh báo: vẫn tạo file kết quả hợp lệ và metadata ghi số cảnh báo bằng 0.

## 10. Tiến độ ba tuần

### Tuần 1: lõi PoC

Chốt cấu trúc dự án, schema, data contract và cấu hình; tạo dữ liệu mẫu; triển khai SQLite repository, RBAC checker, parser, CLI cơ bản và các test tương ứng.

### Tuần 2: phát hiện và kiểm chứng

Triển khai ba nhóm luật, scoring, reporter, integration/scenario test và công cụ tính metric. Sửa lỗi, chạy lại từ môi trường sạch và đóng băng lõi. Chỉ sau mốc này mới triển khai Streamlit nếu còn đủ thời gian.

### Tuần 3: báo cáo

- Ngày 1–2: Chương 1 và 2.
- Ngày 3–4: Chương 3 và 4 dựa trên schema, kiến trúc và mã nguồn thật.
- Ngày 5: Chương 5 từ scenario test và metric đã sinh.
- Ngày 6: Chương 6, trích dẫn và rà soát tính nhất quán.
- Ngày 7: kiểm tra hình/bảng, nhãn đoạn, định dạng và đóng gói bài nộp.

Nếu Streamlit chưa bắt đầu trước khi kết thúc tuần 2, thành phần này bị loại khỏi bản nộp để bảo vệ chất lượng CLI và báo cáo.

## 11. Liên kết với báo cáo

- Chương 1 dùng mục tiêu, phạm vi, yêu cầu và kết quả hướng tới của đặc tả.
- Chương 2 giải thích RBAC, security log và nguyên lý của ba nhóm rủi ro.
- Chương 3 dùng kiến trúc, schema, data flow, luật và scoring thực tế.
- Chương 4 trình bày cấu trúc mã, CLI, dữ liệu mẫu và đầu ra chạy được.
- Chương 5 dùng scenario, confusion matrix, metric, thời gian và phân tích lỗi.
- Chương 6 đối chiếu tiêu chí hoàn thành, hạn chế của dữ liệu giả lập/rule-based và hướng mở rộng.

Mỗi mục trong khung báo cáo phải có người phụ trách, đầu ra kỹ thuật hoặc nguồn tham khảo, tiêu chí hoàn thành, hạn chót và nhãn đối chiếu trong bản Report.

## 12. Phân công nguyên tắc

Giữ trách nhiệm nội dung theo `Khung_bao_cao.md`, nhưng cả hai thành viên cùng chịu trách nhiệm cho các điểm tích hợp. Mỗi đầu việc kỹ thuật có một người thực hiện chính và một người review; người viết chương chỉ sử dụng kết quả đã được tái chạy hoặc kiểm tra chéo.
