# Kế hoạch xây dựng bài báo hoàn chỉnh

> **Trạng thái:** Đang triển khai. `TASKS.md` là backlog thực thi chuẩn;
> `PROGRESS.md` lưu tiến độ và quyết định theo từng lần làm việc. Tệp này giữ
> vai trò kế hoạch tổng thể.

## Điều kiện hoàn thành

Bài báo chỉ được xem là hoàn chỉnh khi đồng thời đạt các điều kiện sau:

- Nội dung tiếng Việt, khoảng 4.000--5.000 từ, theo dạng conference paper.
- Câu hỏi nghiên cứu, claim và số liệu không vượt quá phạm vi nguyên mẫu.
- Có ít nhất 12 nguồn kiểm chứng được, ưu tiên DOI hoặc URL của tổ chức/chủ
  quản xuất bản.
- Có hai hình, tối thiểu bốn bảng và một case study về incident.
- Mọi số liệu trong phần đánh giá tái sinh được từ kho mã nguồn.
- `latexmk -pdf main.tex` biên dịch thành công và không còn placeholder.

## Cách tiếp tục ở các lần sau

1. Đọc `PROGRESS.md` trước để xem checkpoint mới nhất, quyết định đã chốt và
   lệnh cần chạy lại.
2. Mở `TASKS.md`, chọn task **Đang làm** hoặc task khả dụng kế tiếp; không mở
   rộng sang task sau khi chưa có đầu ra/tiêu chí chấp nhận của task hiện tại.
3. Sau mỗi lần triển khai, cập nhật `PROGRESS.md` với ngày, tệp thay đổi, kết
   quả kiểm chứng và việc cần làm kế tiếp.

## 1. Hiện trạng

Thư mục `paper/risk_based_access_monitoring/` đã có khung bài báo LaTeX tiếng
Việt và đã build PDF thành công bằng:

```bash
latexmk -pdf main.tex
```

Khung hiện tại phù hợp để phát triển thành bài báo dạng IMRaD hoặc conference
paper ngắn về chủ đề:

> Giám sát truy cập dựa trên rủi ro bằng cách kết hợp RBAC, phân tích nhật ký
> bảo mật và chấm điểm ngữ cảnh có khả năng giải thích.

Luận điểm chính cần phát triển: hệ thống không chỉ phát hiện tấn công theo luật,
mà còn cải thiện khả năng phân loại cảnh báo nhờ ngữ cảnh hành vi và cơ chế gom
nhóm sự cố.

## 2. Mục tiêu bài báo

- Ngôn ngữ: tiếng Việt.
- Hình thức: IMRaD / conference-style paper.
- Độ dài mục tiêu: khoảng 4.000-5.000 từ.
- Đầu ra chính: `main.pdf` build từ LaTeX.
- Đóng góp học thuật cần nhấn mạnh:
  - Kiến trúc kết hợp RBAC và phân tích nhật ký bảo mật.
  - Lớp chấm điểm rủi ro theo ngữ cảnh.
  - Cơ chế gom nhóm cảnh báo thành sự cố theo người dùng, IP và cửa sổ thời
    gian.
  - Bộ dữ liệu tổng hợp và kiểm thử tự động hỗ trợ tái lập.

## 3. Giai đoạn 1: Chốt khung nghiên cứu [Hoàn thành]

Mục tiêu là làm rõ xương sống nghiên cứu trước khi mở rộng nội dung.

Việc cần làm:

- Củng cố vấn đề nghiên cứu: RBAC truyền thống trả lời "có quyền hay không",
  nhưng chưa đủ để đánh giá rủi ro hành vi.
- Làm rõ khoảng trống: nhiều nguyên mẫu tách riêng kiểm soát truy cập và phân
  tích nhật ký, dẫn đến cảnh báo khó giải thích.
- Chốt câu hỏi nghiên cứu:
  - RQ1: Làm sao kết hợp quyết định RBAC và sự kiện nhật ký bảo mật thành một
    pipeline giám sát rủi ro truy cập có khả năng giải thích?
  - RQ2: Những tín hiệu ngữ cảnh đơn giản nào giúp cải thiện phân loại cảnh báo
    so với phát hiện theo luật?
  - RQ3: Nguyên mẫu phát hiện các kịch bản tấn công tổng hợp và tóm tắt chúng
    thành sự cố hiệu quả đến mức nào?
- Mở rộng phần đóng góp trong `sections/01_introduction.tex`.

Kết quả đầu ra:

- `sections/01_introduction.tex` có lập luận sắc hơn, nêu rõ vấn đề, khoảng
  trống, RQ và đóng góp.

## 4. Giai đoạn 2: Mở rộng tài liệu liên quan [Hoàn thành]

Hiện bibliography còn mỏng. Cần bổ sung khoảng 12-18 nguồn có thể kiểm chứng,
ưu tiên nguồn nền tảng hoặc nguồn có DOI/URL chính thức.

Nhóm tài liệu cần tìm:

- RBAC nền tảng: Ferraiolo, Kuhn, Sandhu, NIST RBAC.
- Quản lý nhật ký bảo mật: NIST SP 800-92, SIEM/log management.
- Phát hiện tấn công ứng dụng web: OWASP, SQL injection prevention/detection.
- Risk-based authentication/access control.
- Context-aware security monitoring.
- Explainable security analytics hoặc alert triage.

Nguyên tắc:

- Không tạo citation giả.
- Mỗi nguồn thêm vào `references.bib` phải có DOI, URL chính thức hoặc metadata
  đủ rõ để kiểm chứng.
- `sections/02_related_work.tex` phải so sánh và chỉ ra khoảng trống, không chỉ
  liệt kê tài liệu.

Kết quả đầu ra:

- `references.bib` có danh mục tài liệu mạnh hơn.
- `sections/02_related_work.tex` có 4-5 tiểu mục với lập luận liên kết trực
  tiếp tới bài báo.

## 5. Giai đoạn 3: Làm thực nghiệm thuyết phục hơn [Chưa bắt đầu]

Phần đánh giá quyết định chất lượng bài. Không chỉ báo rằng hệ thống chạy được,
mà cần có đánh giá có cấu trúc.

Các lớp đánh giá đề xuất:

- Baseline detection:
  - SQL injection.
  - Password guessing.
  - Unauthorized access.
- Context-layer ablation:
  - So sánh không bật `--context-risk` và có bật `--context-risk`.
  - Đếm số context findings theo từng loại tín hiệu.
- Incident grouping:
  - Số cảnh báo được gom thành sự cố.
  - Số sự cố theo severity.
  - Ví dụ chuỗi sự kiện tạo thành một incident timeline.

Lệnh kiểm chứng cần chạy lại trước khi viết số liệu cuối:

```bash
.venv/bin/pytest -q
rbac-guard analyze --context-risk ...
rbac-guard evaluate ...
```

Kết quả đầu ra:

- Bảng baseline precision/recall/F1.
- Bảng context findings theo loại tín hiệu.
- Bảng incident summary.
- Một case study ngắn mô tả chuỗi đăng nhập lỗi, IP mới và truy cập trái phép.
- `sections/06_evaluation.tex` được mở rộng dựa trên số liệu tái sinh từ repo.

## 6. Giai đoạn 4: Thêm hình và bảng [Chưa bắt đầu]

Bài nên có ít nhất 2 hình và 4-5 bảng để tăng tính chuyên nghiệp.

Hình đề xuất:

- Hình kiến trúc pipeline: log input -> parser -> detection engine -> context
  profiler -> risk scorer -> incident reporter.
- Hình luồng xử lý từ event -> alert -> incident.

Bảng đề xuất:

- Bảng mô tả tín hiệu ngữ cảnh và trọng số.
- Bảng mô tả dataset.
- Bảng baseline detection.
- Bảng context findings.
- Bảng incident summary.

Vị trí lưu:

- Hình: `figures/`.
- Bảng tách ngoài nếu cần: `tables/`.
- Bảng ngắn có thể viết trực tiếp trong các file `.tex`.

## 7. Giai đoạn 5: Viết bản thảo đầy đủ [Đang làm một phần]

Thứ tự viết đề xuất:

1. Mở rộng `sections/01_introduction.tex`.
2. Viết đầy đủ `sections/02_related_work.tex`.
3. Nâng `sections/03_system_model.tex` thành mô tả rõ input, output, threat
   model và phạm vi.
4. Mở rộng `sections/04_methodology.tex` thành phần thuật toán: RBAC check,
   rule detection, context profiling, scoring và incident grouping.
5. Viết `sections/05_implementation.tex` dựa trên cấu trúc repo thật.
6. Viết `sections/06_evaluation.tex` từ số liệu thực nghiệm đã tái sinh.
7. Mở rộng `sections/07_discussion.tex` với ưu điểm, hạn chế và threats to
   validity.
8. Viết lại `sections/00_abstract.tex` và `sections/08_conclusion.tex` sau
   cùng.

Phân bổ độ dài mục tiêu:

| Phần | Mục tiêu |
|---|---:|
| Tóm tắt | 180-250 từ |
| Giới thiệu | 700-900 từ |
| Nghiên cứu liên quan | 900-1.200 từ |
| Mô hình và kiến trúc | 600-800 từ |
| Phương pháp | 900-1.100 từ |
| Cài đặt | 400-600 từ |
| Đánh giá | 900-1.200 từ |
| Thảo luận | 500-700 từ |
| Kết luận | 250-350 từ |

## 8. Giai đoạn 6: Rà soát học thuật [Chưa bắt đầu]

Checklist trước khi coi là bản hoàn chỉnh:

- Mỗi claim quan trọng có citation hoặc bằng chứng thực nghiệm.
- Không trình bày prototype như SIEM sản xuất.
- Dữ liệu tổng hợp được nêu rõ là synthetic.
- Kết quả được tái sinh từ repo, không nhập tay thiếu kiểm chứng.
- Không còn placeholder như "Tên tác giả", "Khoa / Trường đại học".
- `references.bib` không có citation giả.
- `latexmk -pdf main.tex` build thành công.
- Bảng, hình, caption và nhãn tham chiếu đều hiển thị đúng.
- Phần hạn chế nêu rõ phạm vi: dữ liệu tổng hợp, rule-based detector, heuristic
  scoring và chưa có behavior profile dài hạn.

## 9. Lộ trình triển khai theo checkpoint

| Checkpoint | Phạm vi | Đầu ra bắt buộc | Trạng thái |
|---|---|---|---|
| CP1 | Khung nghiên cứu | RQ, luận điểm, phạm vi và đóng góp đã chốt | Hoàn thành |
| CP2 | Tài liệu | 12--18 nguồn đã kiểm chứng và literature review có lập luận | Hoàn thành |
| CP3 | Thực nghiệm | Artifact tái sinh, bảng metric và case study | Đang làm |
| CP4 | Minh họa | 2 hình kiến trúc/luồng và 4--5 bảng | Chưa bắt đầu |
| CP5 | Bản thảo | Các section đầy đủ, đồng nhất claim--code--result | Chưa bắt đầu |
| CP6 | Nộp bài | Citation audit, build PDF, phản biện nội bộ và polish | Chưa bắt đầu |

## 10. Thứ tự triển khai ưu tiên

Thứ tự chi tiết, phụ thuộc, đầu ra và tiêu chí nghiệm thu được quản lý trong
`TASKS.md`. Task hiện tại là **T04 -- Chạy regression test của mã nguồn**; sau
khi hoàn thành mới chuyển sang T05 để tái sinh baseline detection.

Ưu tiên tiếp theo nên là giai đoạn 2 và 3, vì tài liệu liên quan và số liệu thực
nghiệm quyết định bài có đủ chất nghiên cứu hay chỉ dừng ở mức mô tả project.
