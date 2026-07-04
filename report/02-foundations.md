# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VÀ TỔNG QUAN NGHIÊN CỨU

## 2.1. Kiểm soát truy cập theo vai trò

Kiểm soát truy cập theo vai trò (Role-Based Access Control - RBAC) xuất phát từ nhu cầu quản trị quyền trong các tổ chức có nhiều người dùng, nhiều chức năng và nhiều tài nguyên. Thay vì gán quyền trực tiếp cho từng cá nhân, RBAC đặt quyền vào các vai trò nghiệp vụ, sau đó gán người dùng vào vai trò tương ứng. Ferraiolo và Kuhn (1992) xem RBAC là một hướng kiểm soát truy cập phù hợp hơn với môi trường thương mại và dân sự so với việc chỉ dựa vào quyền tùy ý của từng chủ sở hữu tài nguyên. Sandhu và cộng sự (1996) tiếp tục hệ thống hóa RBAC thành các mức mô hình như Core RBAC, Hierarchical RBAC và Constrained RBAC, qua đó làm rõ các thành phần user, role, permission, session và constraint.

Trong phạm vi PoC, đề tài dùng Core RBAC: user được gán role, role được gán permission, permission được biểu diễn bằng cặp `resource:action`. Cách chọn này phù hợp với mục tiêu demo vì đủ để kiểm tra truy cập hợp lệ/trái quyền nhưng chưa mở rộng sang role hierarchy, separation of duty hoặc thuộc tính ngữ cảnh. Đây là một giới hạn có chủ ý: mô hình càng đơn giản thì kết quả càng dễ giải thích, nhưng khả năng biểu diễn chính sách ngân hàng thực tế cũng giảm.

Nguyên tắc quyền tối thiểu của Saltzer và Schroeder (1975) cung cấp nền tảng lý luận cho RBAC: mỗi chương trình và người dùng chỉ nên hoạt động với tập quyền nhỏ nhất cần thiết. Trong dataset của đề tài, teller được đọc/cập nhật tài khoản nhưng không được xóa user; auditor đọc tài khoản và audit log; administrator có tập quyền rộng hơn. User disabled không được cấp quyền dù vẫn tồn tại quan hệ với role.

## 2.2. Log bảo mật

Log bảo mật là nguồn bằng chứng ghi lại các sự kiện đã xảy ra trong hệ thống. NIST SP 800-92 nhấn mạnh log management không chỉ là lưu file log mà là một quy trình gồm thu thập, truyền, lưu trữ, phân tích và hủy bỏ log theo chính sách. Đối với đề tài này, authentication log mô tả đăng nhập thành công/thất bại; access log ghi hành động trên tài nguyên; authorization log ghi kết quả kiểm tra quyền.

Một sự kiện đơn lẻ thường chưa đủ để kết luận rủi ro. Password guessing cần nhóm theo user/IP và thời gian; unauthorized access cần đối chiếu `resource:action` với chính sách RBAC; SQL Injection cần đọc nội dung request để tìm dấu hiệu thao túng câu truy vấn. Vì vậy, log trong PoC phải giữ timestamp, định danh nguồn, user, action, resource và evidence để cảnh báo có thể được truy vết.

Điểm quan trọng là log chỉ phản ánh dấu vết sau hoặc trong quá trình xử lý, không thay thế kiểm soát phòng ngừa. Literature về log management thường nhấn mạnh tính toàn vẹn, chuẩn hóa và khả năng phân tích của log; trong khi đề tài này chỉ dùng một pipeline nhỏ, có schema cố định và dữ liệu giả lập. Do đó, kết quả demo chứng minh được mạch xử lý và khả năng giải thích, nhưng chưa chứng minh được năng lực vận hành ở quy mô SIEM.

## 2.3. SQL Injection

SQL Injection xảy ra khi dữ liệu do người dùng kiểm soát làm thay đổi cấu trúc câu SQL. OWASP khuyến nghị prepared statements/parameterized queries là biện pháp phòng ngừa chính vì chúng buộc cơ sở dữ liệu phân biệt rõ mã SQL và dữ liệu đầu vào. Theo hướng này, detection bằng regex trong log chỉ nên được xem là lớp giám sát bổ sung, không phải biện pháp bảo vệ chính.

Các nghiên cứu về SQL Injection cho thấy không thể chỉ nhìn SQLi như một vài chuỗi ký tự cố định. Kindy và Pathan (2012) tổng hợp nhiều nhóm tấn công và biện pháp phòng vệ, nhấn mạnh SQLi vẫn là mối đe dọa đáng kể dù đã có nhiều kỹ thuật giảm thiểu. Jahanshahi, Doupé và Egele (2020) tiếp cận hiện đại hơn bằng SQLBlock, kết hợp phân tích tĩnh và động để hạn chế truy vấn SQL theo chức năng phát sinh truy vấn; nghiên cứu này cũng cho thấy các cơ chế phòng vệ dựa trên profile có thể gặp false positive hoặc bị vượt qua nếu ánh xạ chức năng-truy vấn quá thô.

PoC của đề tài không cố gắng giải quyết toàn bộ không gian SQLi. Hệ thống chỉ tìm bốn nhóm dấu hiệu có tính minh họa: tautology, SQL comment, `UNION SELECT` và stacked query. Ưu điểm là luật dễ đọc, evidence rõ và phù hợp kiểm thử; nhược điểm là bỏ sót encoding, second-order injection, payload biến dạng hoặc các truy vấn hợp lệ nhưng có từ khóa giống SQL. Vì vậy, kết quả phát hiện SQLi trong chương thực nghiệm cần được đọc như đánh giá một bộ luật cụ thể, không phải kết luận tổng quát về phòng chống SQLi.

## 2.4. Dò đoán mật khẩu

Password guessing là hành vi thử nhiều mật khẩu để chiếm quyền truy cập một tài khoản. NIST SP 800-63B xem rate limiting/throttling là kiểm soát cần thiết để giảm nguy cơ online guessing; bản SP 800-63B-4 đặt giới hạn trên cho số lần xác thực thất bại liên tiếp và cho phép tổ chức dùng ngưỡng thấp hơn tùy rủi ro. Điều này củng cố lựa chọn của PoC: xem chuỗi đăng nhập thất bại theo user/IP trong một cửa sổ thời gian là tín hiệu đáng ngờ.

PoC sắp xếp event theo timestamp, duy trì cửa sổ trượt 300 giây và phát hiện khi có ít nhất năm lần thất bại. Đăng nhập thành công làm kết thúc chuỗi trước đó; các lần thất bại phân tán ngoài cửa sổ không tạo cảnh báo. Cách làm này giải thích được và dễ kiểm thử, nhưng vẫn đơn giản hơn môi trường thật: attacker có thể phân tán IP, thay đổi user, dùng credential stuffing hoặc tạo tốc độ thử thấp để né ngưỡng.

Vì vậy, luật password guessing nên được hiểu là baseline rule. Trong hệ thống thật, nó cần kết hợp với MFA, throttling, reputation của IP, lịch sử hành vi, cảnh báo thiết bị lạ và chính sách khóa/mở khóa tài khoản. Đề tài chỉ giữ phần đếm chuỗi thất bại để phù hợp phạm vi PoC.

## 2.5. Chỉ số đánh giá

`TP` là event tấn công được phát hiện, `FP` là event bình thường bị cảnh báo, `FN` là event tấn công bị bỏ sót và `TN` là event bình thường không bị cảnh báo. Precision đo tỷ lệ cảnh báo đúng trong số cảnh báo đã tạo; recall đo tỷ lệ tấn công được tìm thấy; F1 là trung bình điều hòa của precision và recall. Kết quả được tính tự động từ `expected_label` và `event_ids`.

Các chỉ số này hữu ích để kiểm tra implementation, nhưng có giới hạn khi dataset nhỏ và được thiết kế có chủ đích. Precision cao trên dataset demo không đồng nghĩa hệ thống ít false positive trên log ngân hàng thật; recall cao cũng không đồng nghĩa luật bao phủ các biến thể tấn công chưa xuất hiện trong tập kiểm thử. Vì vậy, chương thực nghiệm cần trình bày cả số liệu và phân tích lỗi cụ thể, đặc biệt là false negative của SQL Injection.

## 2.6. Tổng quan nghiên cứu liên quan và so sánh phê bình

Các công trình liên quan có thể chia thành ba nhóm. Nhóm thứ nhất là nền tảng kiểm soát truy cập, gồm Saltzer và Schroeder (1975), Ferraiolo và Kuhn (1992), Sandhu và cộng sự (1996), và tài liệu NIST về RBAC. Nhóm này mạnh ở việc định nghĩa nguyên tắc và mô hình quyền, nhưng không xử lý bài toán phát hiện hành vi bất thường từ log. Nhóm thứ hai là quản trị log và xác thực, tiêu biểu là NIST SP 800-92 và NIST SP 800-63B. Nhóm này cung cấp chuẩn thực hành về log và chống đoán mật khẩu, nhưng không đưa ra một detection engine cụ thể cho bài toán ngân hàng điện tử. Nhóm thứ ba là nghiên cứu về SQL Injection, từ survey của Kindy và Pathan (2012) đến cơ chế SQLBlock của Jahanshahi và cộng sự (2020). Nhóm này đi sâu vào tấn công/phòng vệ SQLi, nhưng thường tập trung vào tầng ứng dụng hoặc cơ sở dữ liệu, không kết hợp trực tiếp với RBAC.

Điểm chung của các nguồn là đều nhấn mạnh tính phân lớp của an toàn thông tin. RBAC làm rõ ai được làm gì; log cho biết điều gì đã xảy ra; SQLi defense giảm khả năng truy vấn bị thao túng; throttling giảm khả năng đoán mật khẩu trực tuyến. Tuy nhiên, nếu triển khai tách rời, các lớp này tạo ra khoảng trống giải thích: một log bị từ chối chưa nói rõ người dùng thiếu quyền nào, còn một quyền RBAC hợp lệ không nói rõ hành vi đăng nhập trước đó có đáng ngờ hay không.

PoC của đề tài nằm ở khoảng giao giữa các hướng này. Nó không mới về mặt thuật toán, nhưng có giá trị ở việc ghép RBAC, log parsing, rule-based detection và risk scoring thành một luồng có thể kiểm thử. Cách tiếp cận này phù hợp báo cáo kỹ thuật vì minh bạch hơn mô hình học máy và nhẹ hơn SIEM hoàn chỉnh. Đổi lại, nó phụ thuộc mạnh vào chất lượng rule, schema log và ngưỡng cấu hình.

| Công trình / nguồn | Trọng tâm | Điểm mạnh | Hạn chế khi áp dụng vào đề tài |
|---|---|---|---|
| Saltzer & Schroeder (1975) | Nguyên tắc bảo vệ thông tin như least privilege và complete mediation | Cung cấp nền tảng lý luận cho thiết kế quyền tối thiểu | Mang tính nguyên lý, không chỉ ra schema RBAC hay luật phát hiện log |
| Ferraiolo & Kuhn (1992); Sandhu et al. (1996); NIST RBAC | Mô hình hóa RBAC và chuẩn hóa thành phần user-role-permission | Phù hợp để thiết kế checker và chính sách truy cập dễ giải thích | Core RBAC chưa xử lý ngữ cảnh, phiên, role hierarchy và xung đột nhiệm vụ |
| NIST SP 800-92 | Quản trị log bảo mật trong tổ chức | Nhấn mạnh lifecycle của log, chuẩn hóa và phân tích log | Là hướng dẫn quản trị, không phải thuật toán phát hiện cụ thể |
| OWASP SQL Injection Prevention | Phòng ngừa SQLi bằng prepared statements và input validation | Gắn trực tiếp với thực hành secure coding | Tập trung phòng ngừa hơn là phát hiện sau sự kiện trong log |
| Kindy & Pathan (2012) | Survey SQLi: lỗ hổng, dạng tấn công và biện pháp phòng vệ | Cho cái nhìn rộng về không gian tấn công SQLi | Survey rộng, chưa gắn với RBAC hoặc risk scoring |
| Jahanshahi et al. (2020) | SQLBlock, kết hợp phân tích tĩnh-động để hạn chế SQLi trong ứng dụng PHP | So sánh phê bình nhiều kỹ thuật phòng vệ và chỉ ra vấn đề false positive/mimicry | Cơ chế nặng hơn PoC, phụ thuộc tầng DB/PHP và không hướng tới log-based classroom demo |
| NIST SP 800-63B-4 | Yêu cầu xác thực và rate limiting chống online guessing | Củng cố cơ sở cho luật đếm đăng nhập thất bại | Là chuẩn xác thực, không thay thế phân tích hành vi hoặc phát hiện credential stuffing phân tán |

## 2.7. Tài liệu tham khảo

- Ferraiolo, D. F., & Kuhn, D. R. (1992). *Role-Based Access Controls*. 15th National Computer Security Conference. <https://csrc.nist.gov/projects/role-based-access-control>
- Jahanshahi, R., Doupé, A., & Egele, M. (2020). *You shall not pass: Mitigating SQL Injection Attacks on Legacy Web Applications*. Proceedings of the 15th ACM Asia Conference on Computer and Communications Security. <https://doi.org/10.1145/3320269.3384760>
- Kent, K., & Souppaya, M. (2006). *Guide to Computer Security Log Management* (NIST SP 800-92). National Institute of Standards and Technology. <https://doi.org/10.6028/NIST.SP.800-92>
- Kindy, D. A., & Pathan, A.-S. K. (2012). *A Detailed Survey on Various Aspects of SQL Injection in Web Applications: Vulnerabilities, Innovative Attacks, and Remedies*. arXiv. <https://arxiv.org/abs/1203.3324>
- NIST. (2025). *Digital Identity Guidelines: Authentication and Authenticator Management* (SP 800-63B-4). <https://pages.nist.gov/800-63-4/sp800-63b.html>
- OWASP Foundation. (n.d.). *SQL Injection Prevention Cheat Sheet*. <https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html>
- Saltzer, J. H., & Schroeder, M. D. (1975). *The Protection of Information in Computer Systems*. Proceedings of the IEEE, 63(9), 1278-1308. <https://web.mit.edu/Saltzer/www/publications/protection/>
- Sandhu, R. S., Coyne, E. J., Feinstein, H. L., & Youman, C. E. (1996). *Role-Based Access Control Models*. IEEE Computer, 29(2), 38-47. <https://doi.org/10.1109/2.485845>
