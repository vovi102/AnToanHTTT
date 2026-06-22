# CHƯƠNG 1. GIỚI THIỆU TỔNG QUAN

`[INTRO-00]` Chương này trình bày bối cảnh, động lực, vấn đề nghiên cứu, yêu cầu, kết quả hướng tới và các nội dung cần thảo luận của đề tài. Mạch lập luận đi từ nhu cầu bảo vệ dịch vụ ngân hàng điện tử đến một nguyên mẫu kết hợp kiểm soát truy cập RBAC với phân tích log dựa trên luật.

`[INTRO-01]` Dịch vụ ngân hàng điện tử giúp khách hàng truy cập tài khoản và thực hiện giao dịch mà không phụ thuộc địa điểm hay thời gian làm việc của quầy giao dịch. Sự thuận tiện này đồng thời làm hệ thống phụ thuộc nhiều hơn vào định danh số, ứng dụng web, cơ sở dữ liệu và các giao diện trao đổi dữ liệu.

`[INTRO-02]` Tài khoản, thông tin khách hàng, lịch sử giao dịch và chức năng quản trị là các tài sản cần được bảo vệ. Trong phạm vi đề tài, ba rủi ro được tập trung là dữ liệu đầu vào chứa dấu hiệu SQL Injection, nhiều lần đăng nhập thất bại trong thời gian ngắn và hành động vượt quá quyền được cấp.

`[INTRO-03]` RBAC trả lời câu hỏi một người dùng được phép thực hiện hành động nào trên tài nguyên nào thông qua vai trò. Log bảo mật ghi lại sự kiện đã diễn ra, nhờ đó cung cấp bằng chứng để kiểm tra việc tuân thủ quyền và nhận diện chuỗi hành vi đáng ngờ.

`[INTRO-04]` Nếu chỉ kiểm tra quyền tại thời điểm yêu cầu, hệ thống có thể ngăn một hành động nhưng thiếu góc nhìn tổng hợp về các lần thử liên tiếp. Ngược lại, nếu chỉ đọc log mà không có ngữ cảnh vai trò, công cụ phân tích khó phân biệt một thao tác nghiệp vụ hợp lệ với truy cập trái quyền.

`[INTRO-05]` Đề tài vì vậy xây dựng PoC tích hợp SQLite RBAC và detection engine dựa trên luật. Cách tiếp cận này phù hợp thời lượng môn học vì quy tắc, bằng chứng và cách chấm điểm đều có thể truy vết, kiểm thử và giải thích trực tiếp.

`[INTRO-06]` Vấn đề nghiên cứu là khoảng cách giữa dữ liệu phân quyền và dữ liệu sự kiện: hai nguồn thông tin thường được xử lý tách rời, làm giảm khả năng giải thích cảnh báo. PoC cần tạo một luồng thống nhất từ log đầu vào, đối chiếu RBAC, phát hiện, tính điểm đến báo cáo cảnh báo.

`[INTRO-07]` Câu hỏi chính là: có thể mô hình hóa quyền và kết hợp các luật đơn giản như thế nào để phát hiện ba nhóm rủi ro đã chọn với đầu ra tái lập? Phạm vi được giới hạn ở log giả lập CSV/JSON, SQLite, Python CLI và Streamlit tùy chọn; hệ thống không xử lý dữ liệu ngân hàng thật, machine learning hoặc SIEM thời gian thực.

`[INTRO-08]` Mô hình RBAC phải biểu diễn user, role, permission và hai quan hệ gán user–role, role–permission. Một quyền được xác định bởi cặp resource–action; user chỉ được cấp quyền khi đang active và tồn tại đầy đủ đường liên kết qua role.

`[INTRO-09]` Pipeline log phải đọc được CSV và JSON, chuẩn hóa về cùng một Event model, kiểm tra trường bắt buộc và thời gian ISO 8601. File sai cấu trúc bị từ chối, trong khi từng dòng sai được cô lập để các dòng hợp lệ còn lại tiếp tục được xử lý.

`[INTRO-10]` Detection engine phải phát hiện các mẫu SQL Injection được chỉ định, chuỗi đăng nhập thất bại đạt ngưỡng trong time window và truy cập không được RBAC cấp phép. Mỗi finding cần giữ rule ID, event ID và mô tả bằng chứng thay vì chỉ trả một nhãn rủi ro.

`[INTRO-11]` Risk scorer phải tạo điểm trong khoảng 0–100 từ loại rủi ro, confidence, số lần lặp và trạng thái RBAC, sau đó ánh xạ sang Low, Medium, High hoặc Critical. Bộ kiểm thử phải bao phủ trường hợp dương tính, âm tính, biên thời gian, dữ liệu lỗi và luồng tích hợp hoàn chỉnh.

`[INTRO-12]` Kết quả kỹ thuật hướng tới là package `rbac_guard` có thể khởi tạo database, kiểm tra quyền, phân tích log và đánh giá kết quả bằng CLI. Streamlit UI sử dụng cùng application service để tải log, lọc cảnh báo, xem thống kê và tải file kết quả.

`[INTRO-13]` Kết quả đánh giá gồm `alerts.csv`, `alerts.json`, `run_metadata.json` và `metrics.json`. Mỗi cảnh báo chứa thời gian, user, IP, resource, action, loại rủi ro, evidence, risk score, severity và các event nguồn.

`[INTRO-14]` Phần thảo luận đánh giá mức độ phát hiện, tính giải thích và giá trị bổ trợ giữa RBAC với log analysis. Đặc biệt, confusion matrix và metric theo từng risk type cho phép chỉ ra cụ thể luật nào hoạt động ổn định và luật nào cần mở rộng.

`[INTRO-15]` Hạn chế dự kiến đến từ dữ liệu giả lập, tập mẫu SQL cố định, ngưỡng password guessing cố định và mô hình RBAC chưa có hierarchy hay separation of duty. Các hướng mở rộng hợp lý gồm dữ liệu thực đã ẩn danh, streaming, quản lý luật, SIEM và mô hình học máy; đây là future work chứ không phải kết quả của PoC.

