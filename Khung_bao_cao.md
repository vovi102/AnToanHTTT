# KẾ HOẠCH TRIỂN KHAI ĐỀ TÀI

## Thiết kế mô hình RBAC và hệ thống phân tích log dựa trên luật để phát hiện rủi ro SQL Injection và dò đoán mật khẩu trong ngân hàng điện tử

| ID | Nhãn Report | Từ khóa | Chủ đề | Vai trò / Ý nghĩa | Phụ trách |
|---|---|---|---|---|---|
| 1.0 | [INTRO-00] | INTRODUCTION | CHƯƠNG 1: GIỚI THIỆU TỔNG QUAN | Mở chương, giới thiệu mục đích, phạm vi và mạch lập luận từ bối cảnh đến các thảo luận dự kiến. | Cả nhóm |
| 1.1.1 | [INTRO-01] | Digital Banking Growth | Sự phát triển của ngân hàng điện tử | Trình bày sự phổ biến của dịch vụ ngân hàng trực tuyến, giá trị mang lại và mức độ phụ thuộc ngày càng tăng vào hệ thống số. | Vi Đăng Khoa |
| 1.1.2 | [INTRO-02] | Security Risk Landscape | Bề mặt tấn công và tài sản cần bảo vệ | Xác định tài khoản, dữ liệu và giao dịch là tài sản trọng yếu; dẫn nhập các rủi ro SQL Injection, dò đoán mật khẩu và truy cập trái quyền. | Vi Đăng Khoa |
| 1.1.3 | [INTRO-03] | RBAC & Security Logs | Vai trò của RBAC và log bảo mật | Giải thích RBAC kiểm soát hành động được phép, còn log cung cấp bằng chứng để giám sát và phát hiện hành vi bất thường. | Vi Đăng Khoa |
| 1.2.1 | [INTRO-04] | Fragmented Controls | Hạn chế của các biện pháp kiểm soát tách rời | Nêu hạn chế khi kiểm tra quyền chỉ mang tính phòng ngừa hoặc phân tích log thiếu ngữ cảnh vai trò, khiến việc nhận diện rủi ro không đầy đủ. | Vi Đăng Khoa |
| 1.2.2 | [INTRO-05] | Integrated Rule-based PoC | Động lực xây dựng nguyên mẫu tích hợp | Lập luận cho việc kết hợp RBAC với phân tích log dựa trên luật nhằm tạo giải pháp PoC minh bạch, dễ giải thích và phù hợp phạm vi môn học. | Vi Đăng Khoa |
| 1.3.1 | [INTRO-06] | Security Gap | Vấn đề cần giải quyết | Phát biểu khoảng trống giữa dữ liệu quyền truy cập, sự kiện bảo mật và khả năng phát hiện tập trung ba nhóm rủi ro đã chọn. | Vi Đăng Khoa |
| 1.3.2 | [INTRO-07] | Research Question & Scope | Câu hỏi nghiên cứu và ranh giới bài toán | Đặt câu hỏi về cách mô hình hóa quyền, phân tích log và chấm điểm cảnh báo; giới hạn ở PoC dùng dữ liệu giả lập và luật xác định trước. | Vi Đăng Khoa |
| 1.4.1 | [INTRO-08] | RBAC Requirements | Yêu cầu đối với mô hình RBAC | Xây dựng user, role, permission và các quan hệ gán quyền; hỗ trợ kiểm tra một user có được thực hiện action trên resource hay không. | Vũ Trọng Quảng |
| 1.4.2 | [INTRO-09] | Log Pipeline Requirements | Yêu cầu đối với dữ liệu và pipeline log | Tạo log CSV/JSON cho đăng nhập, truy cập và kiểm tra quyền; chuẩn hóa các trường cần thiết để parser và detection engine xử lý nhất quán. | Vũ Trọng Quảng |
| 1.4.3 | [INTRO-10] | Detection Requirements | Yêu cầu đối với luật phát hiện | Xây dựng luật nhận diện dấu hiệu SQL Injection, nhiều lần đăng nhập thất bại trong time window và hành động bị RBAC từ chối. | Vũ Trọng Quảng |
| 1.4.4 | [INTRO-11] | Scoring & Evaluation Requirements | Yêu cầu chấm điểm và kiểm thử | Gán risk score, phân loại severity, lưu bằng chứng cảnh báo và kiểm thử bằng các kịch bản bình thường lẫn bất thường. | Vũ Trọng Quảng |
| 1.5.1 | [INTRO-12] | Prototype Deliverable | Nguyên mẫu tích hợp hướng tới | Hoàn thành mô hình RBAC, bộ kiểm tra quyền và pipeline phân tích log dựa trên luật có thể chạy với dữ liệu giả lập. | Vũ Trọng Quảng |
| 1.5.2 | [INTRO-13] | Evaluation Deliverable | Báo cáo cảnh báo và bằng chứng đánh giá | Tạo đầu ra gồm thời gian, user, IP, loại rủi ro, bằng chứng, điểm và severity; tổng hợp kết quả theo từng kịch bản. | Vũ Trọng Quảng |
| 1.6.1 | [INTRO-14] | Effectiveness & Interpretability | Hiệu quả và tính giải thích | Thảo luận mức độ phát hiện của từng luật, khả năng truy vết nguyên nhân cảnh báo và giá trị bổ trợ giữa RBAC với phân tích log. | Vũ Trọng Quảng |
| 1.6.2 | [INTRO-15] | Limitations & Future Work | Hạn chế và khả năng mở rộng | Thảo luận false positive/false negative, dữ liệu giả lập, giới hạn của luật cố định và hướng mở rộng sang dữ liệu thực, streaming, SIEM hoặc ML. | Vũ Trọng Quảng |
| 2.0 | — | FOUNDATIONS | CHƯƠNG 2: CƠ SỞ LÝ THUYẾT | Trình bày các kiến thức nền tảng dùng trong đề tài: RBAC, log bảo mật, SQL Injection và dò đoán mật khẩu. | Cả nhóm |
| 2.1 | — | RBAC | Kiểm soát truy cập theo vai trò | Trình bày mô hình user, role, permission, nguyên tắc quyền tối thiểu và kiểm soát truy cập trong ngân hàng điện tử. | Vi Đăng Khoa |
| 2.2 | — | Security Logs | Log bảo mật | Trình bày authentication log, access log, audit log và vai trò của log trong phát hiện rủi ro. | Vũ Trọng Quảng |
| 2.3 | — | SQL Injection | Tấn công SQL Injection | Giới thiệu dấu hiệu SQL Injection trong request/log như từ khóa SQL, ký tự bất thường, lỗi truy vấn. | Vũ Trọng Quảng |
| 2.4 | — | Password Guessing | Dò đoán mật khẩu | Trình bày rủi ro brute force login, nhiều lần đăng nhập thất bại trong thời gian ngắn. | Vi Đăng Khoa |
| 3.0 | — | SYSTEM DESIGN | CHƯƠNG 3: THIẾT KẾ HỆ THỐNG | Mô tả kiến trúc tổng thể và các thành phần của hệ thống demo. | Cả nhóm |
| 3.1 | — | Architecture | Kiến trúc tổng quan | Thiết kế luồng xử lý: log đầu vào -> parser -> detection engine -> risk scoring -> alert report. | Vũ Trọng Quảng |
| 3.2 | — | RBAC Model | Thiết kế mô hình RBAC | Thiết kế các bảng users, roles, permissions, user_roles, role_permissions và cơ chế kiểm tra quyền. | Vi Đăng Khoa |
| 3.3 | — | Detection Rules | Luật phát hiện rủi ro | Xây dựng luật phát hiện SQL Injection, login fail nhiều lần và truy cập trái quyền. | Vũ Trọng Quảng |
| 3.4 | — | Risk Scoring | Chấm điểm rủi ro | Thiết kế cách tính điểm rủi ro và phân loại cảnh báo Low, Medium, High, Critical. | Vi Đăng Khoa |
| 4.0 | — | IMPLEMENTATION | CHƯƠNG 4: TRIỂN KHAI DEMO | Hiện thực nguyên mẫu bằng dữ liệu log giả lập và script phân tích. | Cả nhóm |
| 4.1 | — | Dataset | Dữ liệu giả lập | Tạo file CSV/JSON mô phỏng log đăng nhập, log truy cập và log kiểm tra quyền. | Vũ Trọng Quảng |
| 4.2 | — | RBAC Checker | Kiểm tra quyền | Viết chức năng kiểm tra user có được phép thực hiện action trên resource hay không. | Vi Đăng Khoa |
| 4.3 | — | Log Detection | Phân tích log | Viết rule/regex phát hiện SQL Injection và đếm login fail theo time window. | Vũ Trọng Quảng |
| 4.4 | — | Alert Report | Báo cáo cảnh báo | Xuất kết quả gồm thời gian, user, IP, loại cảnh báo, bằng chứng, risk score và severity. | Vi Đăng Khoa |
| 5.0 | — | EXPERIMENTS | CHƯƠNG 5: THỰC NGHIỆM VÀ ĐÁNH GIÁ | Kiểm thử hệ thống với các kịch bản: truy cập hợp lệ, SQL Injection, dò đoán mật khẩu và truy cập trái quyền. | Cả nhóm |
| 5.1 | — | Scenario Testing | Kịch bản kiểm thử | Chuẩn bị và chạy các trường hợp bình thường và bất thường để kiểm tra khả năng phát hiện. | Cả nhóm |
| 5.2 | — | Result Analysis | Phân tích kết quả | Đánh giá bảng cảnh báo, mức độ rủi ro và khả năng phát hiện của hệ thống demo. | Cả nhóm |
| 6.0 | — | CONCLUSION | CHƯƠNG 6: KẾT LUẬN | Tổng kết kết quả đạt được, hạn chế và hướng phát triển. | Cả nhóm |
| 6.1 | — | Summary | Tổng kết | Khẳng định hệ thống có thể mô phỏng RBAC, phân tích log và phát hiện các rủi ro bảo mật cơ bản. | Vi Đăng Khoa |
| 6.2 | — | Limitations & Future Work | Hạn chế và hướng phát triển | Nêu hạn chế của rule-based detection và hướng mở rộng như ML, realtime streaming, SIEM, dashboard nâng cao. | Vũ Trọng Quảng |

> **Quy ước viết Report:** Mỗi dòng trong phần Intro được phát triển thành ít nhất một đoạn văn và đặt nhãn `[INTRO-xx]` tương ứng ở đầu đoạn để đối chiếu.

> **Phạm vi demo:** PoC dùng log giả lập CSV/JSON, xử lý bằng Python rule-based detection; không xây dựng ngân hàng điện tử thật, không dùng machine learning và không triển khai SIEM phức tạp.
