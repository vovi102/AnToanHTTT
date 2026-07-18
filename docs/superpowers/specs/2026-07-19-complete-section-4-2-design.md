# Thiết kế bổ sung nội dung mục 4.2

## Bối cảnh

Mục 4.2, “Các thành phần chính”, hiện chỉ chứa một bảng LaTeX dạng float. Khi
LaTeX di chuyển bảng để tối ưu bố cục trang, tiêu đề mục có thể đứng riêng và
tạo cảm giác phần nội dung bị thiếu. Bảng cũng mới liệt kê trách nhiệm, chưa
giải thích cách các thành phần phối hợp trong kiến trúc tổng thể.

## Phạm vi thay đổi

Bổ sung ba đoạn văn ngay sau tiêu đề mục 4.2 và trước Bảng “Phân chia trách
nhiệm giữa các thành phần”. Nội dung mới sẽ:

1. Nhóm các thành phần thành lớp trình bày, lớp nghiệp vụ và kiểm soát truy
   cập, lớp lưu trữ, cùng lớp phân tích nhật ký.
2. Làm rõ ranh giới trách nhiệm và nguyên tắc backend là điểm thực thi quyết
   định bảo mật; frontend không phải nguồn tin cậy cho phân quyền.
3. Trình bày luồng dữ liệu từ Next.js qua FastAPI, SQLite và audit adapter tới
   parser, rules, scoring và reporter.

## Ràng buộc

- Giữ nguyên bảng thành phần hiện tại để làm phần tổng hợp tra cứu nhanh.
- Không thay đổi sơ đồ kiến trúc, mô hình dữ liệu, kết quả thực nghiệm hoặc
  cấu trúc chương.
- Không đưa ra tuyên bố vượt quá khả năng hiện có của mã nguồn.
- Giữ văn phong báo cáo kỹ thuật bằng tiếng Việt và dùng thuật ngữ nhất quán
  với các chương còn lại.

## Tiêu chí hoàn thành

- Mục 4.2 vẫn có nội dung ngay cả khi bảng bị chuyển sang trang hoặc vị trí
  khác.
- Phần diễn giải không lặp nguyên văn mục 4.1 và tạo cầu nối hợp lý sang mục
  4.3 về mô hình dữ liệu RBAC.
- Tài liệu LaTeX biên dịch thành công, không có tham chiếu chưa xác định hoặc
  lỗi tràn dòng mới.
