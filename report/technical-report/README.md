# Báo cáo kỹ thuật LaTeX

Đây là báo cáo kỹ thuật độc lập cho dự án RBAC Guard và demo Nova Bank. Trước
khi nộp, điền các trường trong `metadata.tex`.

Biên dịch PDF từ thư mục này:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Dọn hiện vật biên dịch:

```bash
latexmk -C main.tex
```

Nguồn mã, cấu hình, dữ liệu thử nghiệm và hướng dẫn vận hành được giữ ở thư
mục gốc dự án. Báo cáo chỉ ghi nhận các kết quả tái lập từ những nguồn đó.
