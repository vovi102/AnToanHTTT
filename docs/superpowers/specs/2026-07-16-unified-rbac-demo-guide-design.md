# Thiết kế tài liệu demo RBAC Nova Bank hợp nhất

## Mục tiêu

Tạo một tài liệu duy nhất để người trình bày có thể chuẩn bị, khởi động và demo
RBAC Nova Bank cho giảng viên trong 5–7 phút mà không phải chuyển qua nhiều file.
Tài liệu phải làm rõ bằng hành vi nghiệp vụ thật rằng backend, không phải giao
diện, là nơi thực thi quyền.

## Phạm vi

- Tạo tài liệu chính `DEMO_RBAC_NOVA_BANK.md` tại thư mục gốc.
- Gộp nội dung cần thiết từ hướng dẫn chạy, checklist chuẩn bị và user journey
  hiện tại.
- Giữ một case xuyên suốt: chuyển khoản 50.000.000 VND.
- Cập nhật `README.md`, `HUONG_DAN_CHAY_DEMO.md`,
  `docs/CHUAN_BI_DEMO_RBAC.md` và `docs/USER_JOURNEY_DEMO_RBAC.md` để trỏ rõ tới
  tài liệu chính, tránh duy trì nhiều phiên bản kịch bản.
- Không thay đổi backend, frontend, dữ liệu seed hay chính sách RBAC.

## Độc giả và tiêu chí thành công

Độc giả chính là sinh viên đang chuẩn bị demo cho giảng viên. Sau khi chỉ đọc
một file, người dùng phải:

1. Cài được phụ thuộc bằng UV và npm.
2. Chạy đúng FastAPI ở cổng 8000 và Next.js ở cổng 3000.
3. Biết cách kiểm tra backend trước khi mở giao diện.
4. Chuẩn bị đúng ba tab Admin, Teller và Controller.
5. Trình bày được sự khác nhau giữa Baseline và RBAC bằng thay đổi dữ liệu thật.
6. Chứng minh request vượt quyền bị backend trả 403 và giao dịch vẫn Pending.
7. Kết thúc bằng bản ghi audit và một kết luận RBAC ngắn gọn.
8. Tự xử lý được các lỗi demo phổ biến.

## Cấu trúc tài liệu chính

Tài liệu dùng thứ tự thời gian thay vì chia theo vai trò hoặc thành phần kỹ
thuật:

1. **Demo này chứng minh điều gì** — câu chuyện nghiệp vụ và kết quả cuối.
2. **Thông tin dùng trong demo** — URL, tài khoản và dữ liệu giao dịch mẫu.
3. **Cài đặt lần đầu** — lệnh UV và npm, phân biệt rõ bước chỉ chạy một lần.
4. **Khởi động trước mỗi lần demo** — hai terminal, health check và dấu hiệu
   chương trình đã sẵn sàng.
5. **Chuẩn bị trạng thái sạch** — đăng nhập Admin, reset, Baseline và ba tab.
6. **Kịch bản 5–7 phút** — từng bước có đúng ba phần:
   - Thao tác trên màn hình.
   - Kết quả bắt buộc phải quan sát được.
   - Lời thoại ngắn để giải thích ý nghĩa.
7. **Kết quả cần đối chiếu** — hai giao dịch và các sự kiện audit tương ứng.
8. **Kết luận 30 giây** — phân biệt authentication, authorization và audit.
9. **Xử lý sự cố** — tra theo triệu chứng, gồm `Failed to fetch`, lỗi cache
   webpack, trùng user, không thấy giao dịch và cổng bị chiếm.
10. **Checklist một phút** — danh sách kiểm tra cuối ngay trước khi trình bày.

## Luồng demo chuẩn

1. Admin tạo trực tiếp tài khoản `lan.demo` với role Teller, chứng minh user và
   role được gửi tới API và lưu vào SQLite.
2. Ở Baseline, Teller tạo giao dịch thứ nhất và tự phê duyệt; giao dịch chuyển
   từ Pending sang Approved với cùng người tạo và người duyệt.
3. Admin bật RBAC; chế độ được lưu ở backend và ghi audit.
4. Teller tạo giao dịch thứ hai. UI không hiển thị quyền duyệt thông thường,
   nhưng panel kiểm tra vẫn cố ý gọi endpoint phê duyệt.
5. Backend trả HTTP 403 kèm quyền `transactions:approve`; giao dịch không đổi,
   vẫn Pending.
6. Controller đăng nhập và phê duyệt giao dịch thứ hai thành công.
7. Admin mở audit, đối chiếu `baseline_bypass`, `denied`, `allowed` và
   `success` theo mã giao dịch.

## Nguyên tắc trình bày

- Dùng ngôn ngữ tiếng Việt đơn giản; giải thích thuật ngữ ngay lần đầu xuất
  hiện.
- Lệnh shell phải có thư mục chạy rõ ràng và có thể sao chép nguyên khối.
- Không dùng kết quả chỉ xuất hiện ở frontend làm bằng chứng duy nhất; mỗi điểm
  chính phải gắn với trạng thái giao dịch, HTTP status hoặc audit từ backend.
- Phân biệt rõ cài đặt lần đầu với thao tác lặp lại trước mỗi buổi demo.
- Không đưa phần thực nghiệm phân tích log và biên dịch bài báo vào kịch bản
  Nova Bank chính; hướng dẫn chuyên sâu hiện có vẫn giữ cho mục đích nghiên cứu.
- Không ghi cứng số lượng test vào checklist nhanh để tránh tài liệu lỗi thời;
  chỉ yêu cầu lệnh kiểm thử kết thúc thành công.

## Xử lý tài liệu cũ

`DEMO_RBAC_NOVA_BANK.md` là nguồn hướng dẫn chính duy nhất cho demo giao diện.
Các file cũ không lặp lại toàn bộ kịch bản:

- `README.md` giới thiệu ngắn và liên kết tới tài liệu chính.
- `HUONG_DAN_CHAY_DEMO.md` tiếp tục chứa hướng dẫn thực nghiệm nghiên cứu, nhưng
  phần Nova Bank chỉ dẫn tới tài liệu chính.
- Hai file trong `docs/` được thay bằng thông báo ngắn rằng nội dung đã hợp nhất
  và liên kết tương đối đúng tới tài liệu chính.

## Kiểm tra tài liệu

- Kiểm tra mọi lệnh và đường dẫn so với `pyproject.toml`, `web/package.json` và
  route hiện tại.
- Chạy `git diff --check` để bắt lỗi khoảng trắng.
- Kiểm tra toàn bộ liên kết Markdown cục bộ tồn tại.
- Chạy backend health check và frontend build/test ở mức phù hợp để xác nhận
  hướng dẫn không mô tả một luồng đã hỏng.
- Tìm lại các đoạn hướng dẫn Nova Bank cũ để bảo đảm không còn kịch bản trùng
  hoặc mâu thuẫn.

## Ngoài phạm vi

- Không thiết kế lại UI.
- Không thêm role, permission hoặc endpoint.
- Không thay đổi tài khoản seed và mật khẩu demo.
- Không gộp tài liệu tái lập thực nghiệm nghiên cứu vào tài liệu demo ngắn.
