# CHƯƠNG 6. KẾT LUẬN

## 6.1. Kết quả đạt được

Đề tài đã xây dựng PoC tích hợp Core RBAC, parser CSV/JSON, ba nhóm detection rule, risk scoring, reporter, CLI và Web UI tối giản. SQLite checker thực thi đường liên kết active user–role–permission; detection engine tạo bằng chứng có rule/event ID; artifact và metric được sinh tự động.

Trên 60 event giả lập, hệ thống đạt macro precision 1.0000, recall 0.9667 và F1 0.9825. Password guessing và unauthorized access phát hiện đủ scenario; SQL Injection phát hiện 9/10 và cung cấp một false negative cụ thể để phân tích giới hạn. Toàn bộ 50 test pass sau khi UI được bổ sung.

## 6.2. Hạn chế

Dataset nhỏ, cân bằng có chủ đích và không đại diện lưu lượng ngân hàng thật. Regex SQL Injection chỉ nhận diện nhóm pattern đã định nghĩa; ngưỡng password cố định không thích ứng theo user hoặc IP; RBAC chưa có hierarchy, session activation và separation of duty. Điểm rủi ro là quy tắc thiết kế cho demo, chưa được hiệu chỉnh bằng dữ liệu vận hành.

## 6.3. Hướng phát triển

Hướng gần nhất là mở rộng test corpus và dùng dữ liệu đã ẩn danh để đo FP/FN thực tế. Sau đó có thể thêm cấu hình rule có version, streaming event, dashboard lịch sử, tích hợp SIEM và RBAC nâng cao. Machine learning chỉ nên được xem xét khi có dữ liệu đủ chất lượng và cơ chế giải thích/giám sát; nó không thay thế prepared statements, kiểm soát truy cập hoặc logging đúng chuẩn.

