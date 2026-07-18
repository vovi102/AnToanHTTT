# Bài báo về mô hình RBAC và phân tích log theo luật

Thư mục này chứa bản thảo LaTeX về thiết kế mô hình RBAC và hệ thống phân tích
log theo luật trong dự án RBAC Guard. SQL injection và dò đoán mật khẩu là hai
kịch bản phát hiện chính; dữ liệu tổng hợp chỉ kiểm chứng nguyên mẫu.

## Tệp tin

- `main.tex`: tệp chính của bản thảo.
- `PLAN.md`: kế hoạch phát triển khung hiện tại thành bài báo hoàn chỉnh.
- `sections/`: các tệp nội dung theo từng mục.
- `references.bib`: danh mục tài liệu tham khảo ban đầu.
- `figures/`: đặt hình sinh ra hoặc hình thiết kế tại đây.
- `tables/`: đặt các bảng ngoài tại đây nếu cần.

## Biên dịch

Từ thư mục này:

```bash
latexmk -pdf main.tex
```

Dọn các hiện vật build:

```bash
latexmk -C main.tex
```

## Ghi chú viết bài

- Bản thảo hiện đã được chuyển sang tiếng Việt.
- Lệnh `latexmk -pdf main.tex` dùng pdfLaTeX với mã hóa T5 cục bộ, để hiển thị
  đầy đủ dấu tiếng Việt trong môi trường TeX hiện tại của repo.
- Tái sinh số liệu thực nghiệm từ kho mã nguồn trước khi nộp bản cuối.
- Kiểm chứng mọi tài liệu tham khảo trước khi nộp.
- Thay khối tác giả mẫu trong `main.tex`.
- Bổ sung ảnh chụp màn hình hoặc sơ đồ kiến trúc trong `figures/` nếu cần.
