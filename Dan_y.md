# KẾ HOẠCH TRIỂN KHAI ĐỀ TÀI

Thiết kế mô hình RBAC và hệ thống phân tích log dựa trên luật để phát hiện rủi ro SQL Injection và dò đoán mật khẩu trong ngân hàng

| ID | Từ khóa | Chủ đề | Vai trò/Ý nghĩa | Liên kết |
| --- | --- | --- | --- | --- |
| 1.0 | INTRODUCTION | CHƯƠNG 1: GIỚI THIỆU TỔNG QUAN | Tổng quan về bối cảnh an toàn ngân hàng điện tử và lý do cần kết hợp RBAC với phân tích log. | [NIST RBAC](https://csrc.nist.gov/projects/role-based-access-control); [NIST SP 800-92](https://doi.org/10.6028/NIST.SP.800-92) |
| 1.1 | Background | Bối cảnh đề tài | Phác họa sự gia tăng giao dịch trực tuyến và các rủi ro bảo mật làm nền cho đề tài. | [OWASP SQLi](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html); [NIST SP 800-92](https://doi.org/10.6028/NIST.SP.800-92) |
| 1.2 | Research Problem | Vấn đề nghiên cứu | Nêu khoảng trống chính: phân quyền chưa rõ và log chưa được khai thác để phát hiện hành vi bất thường. | [Sandhu et al. 1996](https://doi.org/10.1109/2.485845); [Kent & Souppaya 2006](https://doi.org/10.6028/NIST.SP.800-92) |
| 1.3 | Research Objectives | Mục tiêu nghiên cứu | Xác định các mục tiêu cần đạt để biến bài toán bảo mật thành một hệ thống demo có thể kiểm chứng. | [Ferraiolo & Kuhn 1992](https://csrc.nist.gov/projects/role-based-access-control); [Kindy & Pathan 2012](https://arxiv.org/abs/1203.3324) |
| 1.4 | Scope | Phạm vi | Giới hạn phạm vi triển khai ở mức Proof of Concept, dùng log giả lập và luật phát hiện thay vì hệ thống SIEM hoàn chỉnh. | [Jahanshahi et al. 2020](https://doi.org/10.1145/3320269.3384760); [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html) |
| 2.0 | FOUNDATIONS | CHƯƠNG 2: CƠ SỞ LÝ THUYẾT | Xây dựng nền tảng lý thuyết để người đọc hiểu các khái niệm bảo mật được dùng trong hệ thống. | [Saltzer & Schroeder 1975](https://web.mit.edu/Saltzer/www/publications/protection/); [NIST RBAC](https://csrc.nist.gov/projects/role-based-access-control) |
| 2.1 | RBAC | Kiểm soát truy cập theo vai trò | Giải thích vì sao phân quyền theo vai trò là lớp kiểm soát đầu tiên để hạn chế truy cập trái quyền. | [Ferraiolo & Kuhn 1992](https://csrc.nist.gov/projects/role-based-access-control); [Sandhu et al. 1996](https://doi.org/10.1109/2.485845) |
| 2.2 | Security Logs | Log bảo mật | Làm rõ log là nguồn bằng chứng quan trọng giúp truy vết hành vi và phát hiện dấu hiệu rủi ro. | [Kent & Souppaya 2006](https://doi.org/10.6028/NIST.SP.800-92) |
| 2.3 | SQL Injection | Tấn công SQL Injection | Trình bày mối đe dọa SQL Injection để làm cơ sở xây dựng luật nhận diện trong log. | [OWASP SQLi](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html); [Kindy & Pathan 2012](https://arxiv.org/abs/1203.3324); [Jahanshahi et al. 2020](https://doi.org/10.1145/3320269.3384760) |
| 2.4 | Password Guessing | Dò đoán mật khẩu | Mô tả hành vi dò đoán mật khẩu như một mẫu tấn công phổ biến cần được phát hiện sớm. | [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html) |
| 3.0 | SYSTEM DESIGN | CHƯƠNG 3: THIẾT KẾ HỆ THỐNG | Chuyển các cơ sở lý thuyết thành thiết kế tổng thể cho hệ thống phát hiện rủi ro. | [Sandhu et al. 1996](https://doi.org/10.1109/2.485845); [NIST SP 800-92](https://doi.org/10.6028/NIST.SP.800-92) |
| 3.1 | Architecture | Kiến trúc tổng quan | Cho thấy cách các thành phần RBAC checker, log parser, detection rules và alert report phối hợp với nhau. | [Kent & Souppaya 2006](https://doi.org/10.6028/NIST.SP.800-92) |
| 3.2 | RBAC Model | Thiết kế mô hình RBAC | Xác định vai trò, quyền hạn và hành động được phép để hệ thống có căn cứ đánh giá truy cập hợp lệ. | [Ferraiolo & Kuhn 1992](https://csrc.nist.gov/projects/role-based-access-control); [Sandhu et al. 1996](https://doi.org/10.1109/2.485845) |
| 3.3 | Detection Rules | Luật phát hiện rủi ro | Mô tả bộ luật giúp chuyển dữ liệu log thô thành cảnh báo về SQL Injection, dò mật khẩu và truy cập sai quyền. | [OWASP SQLi](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html); [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html) |
| 3.4 | Risk Scoring | Chấm điểm rủi ro | Thiết lập cách lượng hóa mức độ nguy hiểm để ưu tiên xử lý các cảnh báo quan trọng. | [NIST SP 800-92](https://doi.org/10.6028/NIST.SP.800-92) |
| 4.0 | IMPLEMENTATION | CHƯƠNG 4: TRIỂN KHAI DEMO | Hiện thực hóa thiết kế thành bản demo có dữ liệu đầu vào, xử lý kiểm tra và kết quả cảnh báo. |  |
| 4.1 | Dataset | Dữ liệu giả lập | Tạo bối cảnh thử nghiệm an toàn bằng các log mô phỏng giao dịch, đăng nhập và hành vi tấn công. |  |
| 4.2 | RBAC Checker | Kiểm tra quyền | Kiểm tra từng hành động trong log có phù hợp với vai trò người dùng hay không. |  |
| 4.3 | Log Detection | Phân tích log | Áp dụng các luật phát hiện để tìm mẫu bất thường trong chuỗi sự kiện hệ thống. |  |
| 4.4 | Alert Report | Báo cáo cảnh báo | Tổng hợp kết quả thành cảnh báo có loại rủi ro, bằng chứng, điểm rủi ro và mức độ nghiêm trọng. |  |
| 5.0 | EXPERIMENTS | CHƯƠNG 5: THỰC NGHIỆM VÀ ĐÁNH GIÁ | Kiểm chứng hệ thống bằng các kịch bản giả lập để đánh giá khả năng phát hiện rủi ro. |  |
| 5.1 | Scenario Testing | Kịch bản kiểm thử | Thiết kế các tình huống bình thường và bất thường để kiểm tra từng nhóm luật phát hiện. |  |
| 5.2 | Result Analysis | Phân tích kết quả | Đọc kết quả cảnh báo để đánh giá điểm mạnh, điểm thiếu và mức độ phù hợp của cách tiếp cận dựa trên luật. |  |
| 6.0 | CONCLUSION | CHƯƠNG 6: KẾT LUẬN | Khép lại câu chuyện nghiên cứu bằng việc tổng hợp kết quả đạt được và hướng phát triển tiếp theo. |  |
| 6.1 | Summary | Tổng kết | Tóm tắt những gì hệ thống đã thực hiện được về RBAC, phân tích log và cảnh báo rủi ro. |  |
| 6.2 | Limitations & Future Work | Hạn chế và hướng phát triển | Nêu các giới hạn của demo và mở ra hướng nâng cấp như dữ liệu thực, SIEM hoặc machine learning. |  |
