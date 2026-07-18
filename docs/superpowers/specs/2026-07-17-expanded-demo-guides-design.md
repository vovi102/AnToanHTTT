# Thiết kế mở rộng hướng dẫn chạy demo

## Mục tiêu

Giúp người đã có nền tảng kỹ thuật thực hiện được cả hai demo mà không phải suy
luận thêm về mục đích của từng lệnh, thao tác, trạng thái hệ thống hoặc kết quả
cần quan sát.

## Phạm vi

- Cập nhật `DEMO_RBAC_NOVA_BANK.md` cho demo Next.js/FastAPI.
- Cập nhật `HUONG_DAN_CHAY_DEMO.md` cho demo CLI và Streamlit.
- Không đổi câu lệnh, endpoint, dữ liệu mẫu, chính sách RBAC hoặc hành vi ứng
  dụng.

## Cấu trúc thay đổi

Mỗi cụm thao tác quan trọng sẽ có giải thích ngắn, đặt sát lệnh hoặc bước tương
ứng:

- **Bạn làm gì:** hành động trực tiếp cần thực hiện.
- **Ý nghĩa:** thành phần hoặc trạng thái kỹ thuật mà thao tác thiết lập/kiểm
  chứng.
- **Kết quả cần thấy:** đầu ra, trạng thái hoặc tín hiệu thành công cần kiểm
  tra trước khi đi tiếp.

Với Nova Bank, phần bổ sung tập trung vào vai trò của hai server, các tab trình
duyệt có session độc lập, reset dữ liệu, và bằng chứng backend thực thi RBAC.
Với RBAC Guard, phần bổ sung tập trung vào seed SQLite, pipeline `analyze`,
`evaluate`, các artifact, chế độ context-risk và giao diện Streamlit.

## Tiêu chí hoàn thành

1. Người đọc biết lý do phải chạy từng dịch vụ/lệnh theo đúng thứ tự.
2. Mỗi checkpoint chính nói rõ đầu ra hoặc trạng thái hợp lệ.
3. Hướng dẫn vẫn ngắn gọn, dành cho người hiểu kỹ thuật.
4. Nội dung khớp lệnh và hành vi hiện có của ứng dụng.

## Kiểm chứng

Đọc lại hai tệp để kiểm tra tính nhất quán của thuật ngữ, đường dẫn, lệnh và
phân biệt rõ demo Nova Bank với demo phân tích log. Không cần chạy lại hệ thống
vì thay đổi chỉ là tài liệu.
