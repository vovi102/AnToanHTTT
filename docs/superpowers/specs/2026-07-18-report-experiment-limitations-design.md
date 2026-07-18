# Bổ sung giới hạn thực nghiệm cho technical report

## Mục tiêu

Làm rõ ý nghĩa của các số liệu thực nghiệm trong technical report mà không
thay đổi kết quả, dataset hoặc định vị dự án là Proof of Concept.

## Phạm vi thay đổi

1. Trong `chapters/06-verification.tex`, bổ sung một đoạn ngay sau phần diễn
   giải bảng baseline. Đoạn này xác định metric là kiểm chứng regression trên
   scenario tổng hợp, nêu giới hạn về tập kiểm thử độc lập và phân biệt event
   với chuỗi/alert của password guessing.
2. Trong `chapters/07-conclusion.tex`, mở rộng phần giới hạn với thiếu hard
   negatives, đánh giá độc lập và metric cấp incident cho context-risk; liệt
   kê hướng đánh giá tiếp theo ở mức khái quát.
3. Biên dịch lại `main.pdf`. Không thay đổi bảng số liệu, detector, dataset,
   artifact hoặc các tệp ngoài thư mục `report/technical-report`.

## Tiêu chí đạt

- Report không diễn giải F1 như hiệu năng sản xuất hay khả năng tổng quát.
- Các giới hạn được trình bày ngắn, kỹ thuật và nhất quán với phạm vi PoC.
- PDF biên dịch thành công, không có tham chiếu chưa xác định hoặc overfull
  hbox mới.
