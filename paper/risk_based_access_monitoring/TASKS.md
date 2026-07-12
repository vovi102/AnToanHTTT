# Danh sách công việc bài báo

Tệp này là backlog thực thi chuẩn của bài báo. Mỗi lần tiếp tục, đọc
`PROGRESS.md`, chọn task có trạng thái **Đang làm** hoặc task **Chưa làm** đầu
tiên có các phụ thuộc đã hoàn thành, rồi cập nhật cả hai tệp sau khi xong.

## Quy ước trạng thái

- **Hoàn thành:** có đầu ra và bằng chứng kiểm chứng đã lưu.
- **Đang làm:** chỉ có một task được mang trạng thái này.
- **Chưa làm:** chưa bắt đầu hoặc đang chờ phụ thuộc.
- **Bị chặn:** nêu rõ nguyên nhân và thông tin cần bổ sung trong `PROGRESS.md`.

## Backlog

| Mã | Công việc | Phụ thuộc | Tệp/đầu ra chính | Tiêu chí nghiệm thu | Trạng thái |
|---|---|---|---|---|---|
| T01 | Chốt câu hỏi nghiên cứu, phạm vi và đóng góp | -- | `sections/01_introduction.tex` | Có RQ1--RQ3; claim giới hạn ở nguyên mẫu và dữ liệu tổng hợp | Hoàn thành |
| T02 | Kiểm tra tương thích giữa paper và chương trình demo | T01 | `PLAN.md`, các section kỹ thuật | Không còn claim mâu thuẫn với parser, scoring hoặc incident model | Hoàn thành |
| T03 | Xây dựng tài liệu liên quan và thư mục tham khảo | T01 | `references.bib`, `sections/02_related_work.tex` | Có 12 nguồn kiểm chứng; literature review có so sánh khoảng trống | Hoàn thành |
| T04 | Chạy regression test của mã nguồn | T02 | Bằng chứng trong `PROGRESS.md` | `.venv/bin/pytest -q` thành công; ghi số test và ngày chạy | Hoàn thành |
| T05 | Tái sinh baseline detection | T04 | `artifacts/cp3-baseline/`, `tables/baseline_results.tex` | Có lệnh, JSON đầu ra, số event/alert và precision, recall, F1 theo từng nhãn | Hoàn thành |
| T06 | Tái sinh phân tích rủi ro ngữ cảnh | T05 | `artifacts/cp3-context/`, `tables/context_findings.tex` | Có số event hợp lệ, alert, finding theo từng rule context; mọi số lấy từ artifact | Hoàn thành |
| T07 | Tái sinh và tóm tắt incident grouping | T06 | `tables/incident_summary.tex` | Có số incident, severity, khoảng thời gian, evidence và quy tắc nhóm; không tuyên bố timeline chi tiết nếu code không có | Hoàn thành |
| T08 | Viết case study từ incident thực tế | T07 | `sections/06_evaluation.tex` | Mô tả một incident bằng ID/evidence thực tế và nêu giới hạn dữ liệu tổng hợp | Hoàn thành |
| T09 | Hoàn thiện mô tả dataset và thiết kế đánh giá | T05, T06 | `tables/dataset_description.tex`, `sections/06_evaluation.tex` | Tách rõ baseline/risk dataset, nhãn, metric, cấu hình và tính tái lập | Hoàn thành |
| T10 | Vẽ hình kiến trúc pipeline | T02 | `figures/architecture.*`, `sections/03_system_model.tex` | Hình thể hiện log, parser, RBAC/rule, context profiler, scorer, reporter; caption và label biên dịch đúng | Hoàn thành |
| T11 | Vẽ hình luồng event--alert--incident | T07 | `figures/event_alert_incident.*`, `sections/04_methodology.tex` | Hình phản ánh đúng luồng code và quy tắc nhóm user--IP/cửa sổ thời gian | Hoàn thành |
| T12 | Viết đầy đủ mô hình hệ thống và threat model | T02, T03 | `sections/03_system_model.tex` | Nêu input/output, trust boundary, attack scope và các điều không xử lý | Hoàn thành |
| T13 | Viết đầy đủ phương pháp | T02, T03, T11 | `sections/04_methodology.tex` | Diễn giải RBAC, rule detection, context scoring và grouping; ký hiệu/thuật toán khớp code | Hoàn thành |
| T14 | Viết phần cài đặt tái lập | T04--T07 | `sections/05_implementation.tex` | Mô tả module, CLI, config và cách tái sinh kết quả từ repo | Hoàn thành |
| T15 | Hoàn thiện phần đánh giá | T05--T09 | `sections/06_evaluation.tex` | Có tối thiểu bốn bảng tổng cộng trong paper, metric/case study và diễn giải không vượt dữ liệu | Hoàn thành |
| T16 | Viết thảo luận và threats to validity | T12--T15 | `sections/07_discussion.tex` | Nêu trade-off, dữ liệu tổng hợp, heuristic/rule-based, giới hạn tổng quát hóa và hướng mở rộng | Hoàn thành |
| T17 | Viết lại tóm tắt và kết luận sau số liệu cuối | T15, T16 | `sections/00_abstract.tex`, `sections/08_conclusion.tex` | Tóm tắt/kết luận phản ánh số liệu cuối, không có claim mới hay placeholder | Hoàn thành |
| T18 | Kiểm toán citation, claim và định dạng | T03, T12--T17 | Toàn bộ source LaTeX | Mỗi claim quan trọng có nguồn/bằng chứng; không citation/reference undefined; đủ 2 hình và ít nhất 4 bảng | Hoàn thành |
| T19 | Biên dịch và kiểm tra bản nộp | T18 | `main.pdf`, ghi nhận trong `PROGRESS.md` | `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` thành công; không còn placeholder | Hoàn thành |

## Thứ tự thực thi hiện tại

1. T10: vẽ hình kiến trúc pipeline.
2. T11--T19: hoàn thiện luồng sự kiện, nội dung, kiểm toán và bản PDF nộp.

## Quy tắc lưu bằng chứng

- Artifact sinh tự động đặt trong `artifacts/` theo checkpoint; không sửa tay
  JSON hay metric sau khi chạy.
- Giá trị đưa vào bảng LaTeX phải truy nguyên được đến artifact và lệnh trong
  `PROGRESS.md`.
- Khi một task hoàn thành, ghi ngày, lệnh kiểm chứng, kết quả và task tiếp theo
  vào đầu phần nhật ký của `PROGRESS.md`.
