# KẾ HOẠCH TRIỂN KHAI ĐỀ TÀI — VERSION 3

## Thiết kế mô hình RBAC và hệ thống phân tích log dựa trên luật để phát hiện rủi ro SQL Injection và dò đoán mật khẩu trong ngân hàng điện tử

> **Quy ước V3:** Nội dung được bổ sung hoặc điều chỉnh trong version 3 được bôi vàng bằng thẻ `<mark>`. Các paragraph ở cuối tệp là nội dung chuẩn bị sẵn để dùng nguyên văn trong Báo cáo BTL Cuối Kỳ; chỉ được phép viết thêm hoặc mở rộng, không sửa nội dung gốc.

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
| 3.1 | — | Architecture | Kiến trúc tổng quan | Thiết kế luồng xử lý: log đầu vào → parser → detection engine → risk scoring → alert report. | Vũ Trọng Quảng |
| 3.2 | — | RBAC Model | Thiết kế mô hình RBAC | Thiết kế các bảng users, roles, permissions, user_roles, role_permissions và cơ chế kiểm tra quyền. | Vi Đăng Khoa |
| 3.3 | — | Detection Rules | Luật phát hiện rủi ro | Xây dựng luật phát hiện SQL Injection, login fail nhiều lần và truy cập trái quyền. | Vũ Trọng Quảng |
| 3.4 | — | Risk Scoring | Chấm điểm rủi ro | Thiết kế cách tính điểm rủi ro và phân loại cảnh báo Low, Medium, High, Critical. | Vi Đăng Khoa |
| 4.0 | — | IMPLEMENTATION | CHƯƠNG 4: TRIỂN KHAI DEMO | Hiện thực nguyên mẫu bằng dữ liệu log giả lập và script phân tích. | Cả nhóm |
| 4.1 | — | Dataset | Dữ liệu giả lập | Tạo file CSV/JSON mô phỏng log đăng nhập, log truy cập và log kiểm tra quyền. | Vũ Trọng Quảng |
| 4.2 | — | RBAC Checker | Kiểm tra quyền | Viết chức năng kiểm tra user có được phép thực hiện action trên resource hay không. | Vi Đăng Khoa |
| 4.3 | — | Log Detection | Phân tích log | Viết rule/regex phát hiện SQL Injection và đếm login fail theo time window. | Vũ Trọng Quảng |
| 4.4 | — | Alert Report | Báo cáo cảnh báo | Xuất kết quả gồm thời gian, user, IP, loại cảnh báo, bằng chứng, risk score và severity. | Vi Đăng Khoa |
| <mark>5.0</mark> | <mark>—</mark> | <mark>EXPERIMENTS & DISCUSSION</mark> | <mark>CHƯƠNG 5: THỰC NGHIỆM, KẾT QUẢ VÀ THẢO LUẬN</mark> | <mark>Kiểm thử nguyên mẫu bằng các kịch bản tổng hợp, trình bày kết quả tái lập và thảo luận rõ giá trị, giới hạn cùng hướng mở rộng.</mark> | <mark>Cả nhóm</mark> |
| 5.1 | — | Scenario Testing | Thiết lập và kịch bản kiểm thử | Chuẩn bị các trường hợp bình thường và bất thường để kiểm tra khả năng phát hiện. | Cả nhóm |
| <mark>5.1.1</mark> | <mark>[RD-01]</mark> | <mark>Experimental Setup & Reproducibility</mark> | <mark>Thiết lập thực nghiệm và khả năng tái lập</mark> | <mark>Nêu dữ liệu đầu vào, seed RBAC, cấu hình ngưỡng, lệnh sinh alert/metric và nguyên tắc lấy số liệu trực tiếp từ artifact.</mark> | <mark>Vũ Trọng Quảng</mark> |
| <mark>5.2</mark> | <mark>—</mark> | <mark>RESULTS</mark> | <mark>Kết quả thực nghiệm</mark> | <mark>Trình bày kết quả baseline có nhãn, tín hiệu ngữ cảnh và các incident được tái sinh từ dữ liệu tổng hợp.</mark> | <mark>Cả nhóm</mark> |
| <mark>5.2.1</mark> | <mark>[RD-02]</mark> | <mark>Baseline Detection Results</mark> | <mark>Kết quả phát hiện baseline</mark> | <mark>Báo cáo TP, FP, FN, TN, precision, recall và F1 cho SQL Injection, password guessing và unauthorized access; diễn giải macro average.</mark> | <mark>Vũ Trọng Quảng</mark> |
| <mark>5.2.2</mark> | <mark>[RD-03]</mark> | <mark>Context-risk Findings</mark> | <mark>Kết quả các tín hiệu rủi ro theo ngữ cảnh</mark> | <mark>Mô tả số alert và finding theo các tín hiệu ngoài giờ, IP mới, tài nguyên hiếm và từ chối lặp lại; không diễn giải finding như metric phân loại độc lập.</mark> | <mark>Vũ Trọng Quảng</mark> |
| <mark>5.2.3</mark> | <mark>[RD-04]</mark> | <mark>Incident Case Study</mark> | <mark>Case study chuỗi truy cập rủi ro</mark> | <mark>Phân tích incident điển hình để liên kết event, alert, evidence, risk score và severity thành một đơn vị triage có thể truy vết.</mark> | <mark>Vi Đăng Khoa</mark> |
| <mark>5.3</mark> | <mark>—</mark> | <mark>DISCUSSION</mark> | <mark>Thảo luận</mark> | <mark>Diễn giải giá trị của thiết kế, các trade-off, threats to validity và hướng đánh giá tiếp theo mà không suy diễn quá phạm vi PoC.</mark> | <mark>Cả nhóm</mark> |
| <mark>5.3.1</mark> | <mark>[RD-05]</mark> | <mark>Design Value & Interpretability</mark> | <mark>Giá trị thiết kế và tính giải thích</mark> | <mark>Làm rõ lợi ích của việc liên kết quyết định RBAC, luật phát hiện và evidence trong cùng alert/incident, thay vì xem nguyên mẫu là SIEM hoàn chỉnh.</mark> | <mark>Vi Đăng Khoa</mark> |
| <mark>5.3.2</mark> | <mark>[RD-06]</mark> | <mark>Limitations & Threats to Validity</mark> | <mark>Hạn chế và mối đe dọa đối với tính hợp lệ</mark> | <mark>Nêu giới hạn của dữ liệu tổng hợp, regex SQL Injection, ngưỡng cố định và heuristic ngữ cảnh; phân biệt độ phù hợp với scenario khỏi khả năng khái quát hóa.</mark> | <mark>Vũ Trọng Quảng</mark> |
| <mark>5.3.3</mark> | <mark>[RD-07]</mark> | <mark>Verifiable Future Work</mark> | <mark>Hướng mở rộng có thể kiểm chứng</mark> | <mark>Đề xuất đánh giá trên log ẩn danh, có nhãn độc lập, đa nguồn và có thước đo vận hành trước khi tích hợp streaming, SIEM hoặc machine learning.</mark> | <mark>Vũ Trọng Quảng</mark> |
| 6.0 | — | CONCLUSION | CHƯƠNG 6: KẾT LUẬN | Tổng kết kết quả đạt được, hạn chế và hướng phát triển. | Cả nhóm |
| 6.1 | — | Summary | Tổng kết | Khẳng định hệ thống có thể mô phỏng RBAC, phân tích log và phát hiện các rủi ro bảo mật cơ bản. | Vi Đăng Khoa |
| 6.2 | — | Limitations & Future Work | Hạn chế và hướng phát triển | Nêu hạn chế của rule-based detection và hướng mở rộng như ML, realtime streaming, SIEM, dashboard nâng cao. | Vũ Trọng Quảng |

> **Quy ước viết Report:** Mỗi dòng trong phần Intro được phát triển thành ít nhất một đoạn văn và đặt nhãn `[INTRO-xx]` tương ứng ở đầu đoạn để đối chiếu. Các dòng `[RD-01]` đến `[RD-07]` liên kết trực tiếp với các paragraph chuẩn bị sẵn bên dưới.

> **Phạm vi demo:** PoC dùng log giả lập CSV/JSON, xử lý bằng Python rule-based detection; không xây dựng ngân hàng điện tử thật, không dùng machine learning và không triển khai SIEM phức tạp.

---

## Paragraphs chuẩn bị sẵn cho Results & Discussion

> **Lưu ý sử dụng:** Bảy paragraph dưới đây được dùng nguyên văn trong báo cáo cuối cùng. Có thể thêm câu, bảng, hình hoặc paragraph mở rộng trước/sau chúng, nhưng không chỉnh sửa phần nội dung đã soạn.

### [RD-01] Thiết lập thực nghiệm và khả năng tái lập

<mark>Thực nghiệm baseline sử dụng tệp `data/logs_demo.csv`, seed phân quyền `data/rbac_seed.json` và cấu hình `config/default.toml`. Bộ dữ liệu gồm 60 sự kiện hợp lệ, trong đó có 30 sự kiện lành tính và ba nhóm sự kiện rủi ro được gán nhãn: SQL Injection, dò đoán mật khẩu và truy cập trái quyền. Ngưỡng phát hiện dò đoán mật khẩu được đặt là năm lần đăng nhập thất bại trong cửa sổ 300 giây; các ngưỡng phân loại severity lần lượt là 30, 60 và 85 điểm. Alert được sinh trước bằng lệnh phân tích, sau đó lệnh đánh giá đối chiếu định danh sự kiện với nhãn kỳ vọng để tạo confusion matrix và các chỉ số đo lường. Vì các số liệu được lấy trực tiếp từ artifact sinh bởi chương trình thay vì nhập thủ công, kết quả có thể được tái lập khi dùng cùng dữ liệu đầu vào và cấu hình.</mark>

### [RD-02] Kết quả phát hiện baseline

<mark>Ở lần chạy baseline, hệ thống xử lý đầy đủ 60 sự kiện hợp lệ, không có dòng lỗi và tạo 20 alert. Kết quả cho thấy password guessing và unauthorized access đều đạt precision, recall và F1 bằng 1,0000 trên bộ dữ liệu tổng hợp. Với SQL Injection, hệ thống nhận diện đúng 9 trong 10 sự kiện tấn công, không tạo false positive và bỏ sót một biến thể, tương ứng precision 1,0000, recall 0,9000 và F1 0,9474. Khi lấy trung bình vĩ mô cho ba nhóm rủi ro, precision đạt 1,0000, recall đạt 0,9667 và F1 đạt 0,9825. Các số liệu này cho thấy implementation đáp ứng tốt các scenario có nhãn đã thiết kế; tuy nhiên, chúng không được diễn giải là bằng chứng về hiệu năng trên nhật ký vận hành thực tế.</mark>

### [RD-03] Kết quả tín hiệu rủi ro theo ngữ cảnh

<mark>Trên kịch bản rủi ro theo ngữ cảnh, hệ thống xử lý 14 sự kiện hợp lệ, không có dòng lỗi, tạo 15 alert và ghi nhận 10 finding ngữ cảnh. Các finding gồm sáu tín hiệu hoạt động ngoài giờ, hai tín hiệu truy cập tài nguyên hiếm, một tín hiệu IP mới đối với người dùng và một cụm hành động bị từ chối lặp lại. Kết quả này cho thấy lớp context-risk có thể bổ sung thông tin ưu tiên hóa cho các alert vốn được phát hiện từ luật nền. Tuy nhiên, số finding không phải số lượng sự kiện độc lập vì một sự kiện có thể đồng thời mang nhiều tín hiệu. Do đó, phần kết quả chỉ trình bày finding như bằng chứng triage có khả năng giải thích, không dùng chúng để suy ra precision, recall hoặc F1 độc lập.</mark>

### [RD-04] Case study incident rủi ro

<mark>Case study có nhiều tín hiệu nhất là incident gắn với người dùng `teller01` và địa chỉ IP `198.51.100.50` trong khoảng 22:00–22:05 ngày 22-06-2026. Incident này gồm sáu sự kiện và mười alert, đồng thời chứa các bằng chứng về truy cập ngoài giờ, IP mới, chuỗi năm lần đăng nhập thất bại trong năm phút, thao tác `users:delete` bị RBAC từ chối và truy cập tài nguyên hiếm. Cơ chế grouping gom các alert có cùng cặp người dùng–IP trong cửa sổ thời gian công bố; điểm incident được tính từ điểm alert lớn nhất cộng bonus chuỗi, sau đó giới hạn ở 100. Vì vậy incident đạt 99 điểm và mức Critical. Ví dụ này minh họa cách các rule nền và tín hiệu ngữ cảnh được liên kết thành một đơn vị triage có thể truy vết về event gốc, thay vì chỉ tạo ra các cảnh báo rời rạc.</mark>

### [RD-05] Giá trị của thiết kế và tính giải thích

<mark>Giá trị thực tế của nguyên mẫu không nằm ở việc thay thế một nền tảng SIEM hoàn chỉnh, mà ở việc liên kết quyết định RBAC, luật phát hiện và bằng chứng trong cùng một đầu ra. Mỗi alert lưu định danh sự kiện, luật đã khớp, evidence, điểm rủi ro và severity; incident chỉ gom các alert cùng cặp người dùng–IP theo cửa sổ đã công bố. Nhờ đó, người phân tích có thể lần từ một incident về các event tạo ra cảnh báo và kiểm tra lý do xếp hạng rủi ro mà không phải suy luận từ một điểm số thiếu ngữ cảnh. Cách tổ chức này phù hợp với mục tiêu của PoC: minh họa một pipeline giám sát nhỏ gọn, có thể kiểm thử và có thể giải thích, trong đó dữ liệu phân quyền bổ sung ngữ cảnh cho phân tích log.</mark>

### [RD-06] Hạn chế và threats to validity

<mark>Kết quả cần được diễn giải trong giới hạn của dữ liệu và luật đã xây dựng. Dataset cùng trường `expected_label` được nhóm tạo ra để kiểm thử các scenario mục tiêu, vì vậy precision, recall và F1 phản ánh mức độ khớp giữa implementation với tập luật trên dữ liệu tổng hợp, không chứng minh khả năng phát hiện trên tập dữ liệu độc lập. Regex SQL Injection chỉ bao phủ các mẫu đã định nghĩa nên có thể bỏ sót biến thể được mã hóa hoặc phân mảnh; ngược lại, việc mở rộng regex có thể làm tăng false positive. Tương tự, luật dò đoán mật khẩu dựa trên đúng cặp người dùng–IP và cửa sổ cố định, nên có thể không phát hiện hành vi phân tán theo IP, tài khoản hoặc thời gian. Các tín hiệu IP mới, ngoài giờ, tài nguyên hiếm và từ chối lặp lại cũng chỉ là heuristic phục vụ triage, không phải kết luận chắc chắn về ý đồ hoặc mức độ thành công của một cuộc tấn công.</mark>

### [RD-07] Hướng mở rộng có thể kiểm chứng

<mark>Bước phát triển tiếp theo là đánh giá nguyên mẫu trên nhật ký đã ẩn danh, đại diện cho nhiều khoảng thời gian và có nhãn hoặc đánh giá độc lập của chuyên gia. Khi đó, báo cáo cần đo thêm false positive, false negative, độ trễ xử lý, chi phí triage và độ ổn định của kết quả khi thay đổi cấu hình, thay vì chỉ thống kê số lượng scenario. Pipeline cũng có thể được mở rộng bằng kiểm tra schema, provenance của log và correlation đa nguồn trước khi đưa dữ liệu vào luồng sự kiện. Streaming, tích hợp SIEM, dashboard lịch sử hoặc mô hình học máy chỉ nên được xem xét sau khi có dữ liệu đủ chất lượng, quy trình hiệu chỉnh ngưỡng và cơ chế giải thích, kiểm toán rõ ràng. Hướng mở rộng theo từng giả thuyết có thể đo được sẽ giúp tránh suy diễn quá mức từ kết quả trên dữ liệu tổng hợp hiện tại.</mark>
