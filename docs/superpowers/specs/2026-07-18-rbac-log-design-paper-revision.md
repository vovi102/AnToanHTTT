# Đặc tả chỉnh sửa paper: mô hình RBAC và phân tích log theo luật

## Mục tiêu

Chỉnh sửa paper LaTeX `paper/risk_based_access_monitoring/` để trọng tâm là
thiết kế giải pháp: mô hình RBAC và hệ thống phân tích log theo luật nhằm phát
hiện rủi ro SQL injection và dò đoán mật khẩu trong ngữ cảnh ngân hàng. Nguyên
mẫu, dữ liệu tổng hợp và demo chỉ là bằng chứng rằng thiết kế đã được hiện thực
hóa và có thể tái lập.

## Tiêu đề

`Thiết kế mô hình RBAC và hệ thống phân tích log dựa trên luật để phát hiện rủi ro SQL Injection và dò đoán mật khẩu trong ngân hàng`

## Phạm vi nội dung

- Dùng RBAC SQLite làm mô hình phân quyền và nguồn đối chiếu quyền trong phân
  tích hậu kiểm log.
- Đặt hai luật chính làm kịch bản phát hiện: chỉ báo SQL injection trong
  request và chuỗi xác thực thất bại (password guessing) theo ngưỡng/cửa sổ
  thời gian cấu hình.
- Giữ luật `RBAC-UNAUTHORIZED` như kiểm tra hỗ trợ, không nâng thành trọng tâm
  ngang hàng với hai luật chính.
- Giữ context-risk, chấm điểm và gom incident là phần mở rộng tùy chọn. Chúng
  phải được mô tả đúng là heuristic có thể giải thích, không phải mô hình học
  máy hoặc access control thích nghi thời gian thực.
- Dữ liệu tổng hợp, metric và artifacts chỉ là kiểm chứng nguyên mẫu; không
  dùng chúng để khẳng định hiệu năng trên log vận hành hay hệ thống ngân hàng
  sản xuất.

## Thay đổi theo cấu trúc paper

1. Đổi tiêu đề, tóm tắt, giới thiệu, đóng góp và câu hỏi nghiên cứu để phản ánh
   trọng tâm thiết kế mô hình/giải pháp.
2. Tinh chỉnh mô hình hệ thống và phương pháp: RBAC, parser, hai luật chính,
   scoring và ranh giới tin cậy phải khớp mã nguồn/configuration hiện có.
3. Rút gọn phần Cài đặt: giữ ánh xạ mô-đun, interface chạy và artifacts tối
   thiểu; bỏ chi tiết coverage/checkpoint/lệnh dài không cần cho lập luận.
4. Đổi ngữ điệu phần Đánh giá thành kiểm chứng nguyên mẫu; đối chiếu số liệu
   với artifact có trong repo và giữ các giới hạn thực nghiệm rõ ràng.
5. Chỉnh Thảo luận và Kết luận để không mở rộng phạm vi sang demo BankSafe,
   mô hình học máy, detection sản xuất hoặc zero trust hoàn chỉnh.

## Ngoài phạm vi

- Không thay đổi mã nguồn, configuration, dataset hay hành vi demo.
- Không đưa demo BankSafe (FastAPI/Next.js) thành thành phần của paper.
- Không thay đổi ngoài paper và tài liệu quy trình trong `docs/superpowers/`.
- Không ghi đè thay đổi sẵn có của người dùng trong `main.tex` (đã xóa khối
  tuyên bố về AI).

## Xác minh

- Đối chiếu các mô tả với `src/rbac_guard/`, `config/default.toml`, data và
  artifacts hiện có.
- Biên dịch `latexmk -pdf main.tex` nếu môi trường TeX có sẵn; nếu không, chạy
  kiểm tra cấu trúc LaTeX và báo rõ giới hạn môi trường.
- Chạy `git diff --check` cho các tệp chỉnh sửa.
