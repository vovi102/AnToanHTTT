# Thiết kế chuyển trọng tâm từ kiểm thử sang thực nghiệm

## Mục tiêu

Điều chỉnh báo cáo kỹ thuật để không trình bày hoạt động kiểm thử phần mềm,
nhưng vẫn giữ bằng chứng thực nghiệm cần thiết cho việc đánh giá mô hình RBAC
và pipeline phân tích nhật ký.

## Phạm vi thay đổi

- Đổi tên chương `Kiểm thử và kết quả` thành `Thực nghiệm và đánh giá`.
- Loại bỏ mô tả unit test, integration test, coverage, Vitest, production build
  và các lệnh chạy bộ kiểm thử.
- Giữ thiết kế dataset, metric precision/recall/F1, kết quả regression và
  holdout, phân tích độ nhạy, đe dọa tới tính hợp lệ và khả năng tái lập.
- Diễn đạt việc nối audit Nova Bank với pipeline như một thực nghiệm luồng dữ
  liệu đầu-cuối, không gọi là integration test.
- Rà soát các chương khác để thay cách diễn đạt liên quan đến test/kiểm thử khi
  chúng mô tả bằng chứng của báo cáo.
- Giữ các lệnh tạo dataset, chạy pipeline và sinh metric trong phụ lục vì đây
  là quy trình tái lập thực nghiệm.

## Nguyên tắc biên tập

Không xóa số liệu chỉ vì số liệu được xác minh bằng mã nguồn. Báo cáo phân biệt
rõ kiểm thử phần mềm với đánh giá thực nghiệm: phần thứ nhất không được trình
bày, phần thứ hai vẫn là cơ sở cho kết luận. Các tuyên bố về hiệu quả phải tiếp
tục bị giới hạn bởi dữ liệu tổng hợp, số campaign nhỏ và phạm vi PoC.

## Tiêu chí hoàn thành

1. Mục lục và tiêu đề chương không còn cụm `Kiểm thử và kết quả`.
2. Phần thân báo cáo không mô tả framework kiểm thử, coverage hoặc lệnh test.
3. Kết quả định lượng và các hạn chế thực nghiệm vẫn đầy đủ, nhất quán.
4. Tài liệu LaTeX biên dịch thành công, không có reference/citation chưa xác
   định hoặc overfull box.
5. PDF mới được kiểm tra nhanh về số trang và bố cục chương đã sửa.
