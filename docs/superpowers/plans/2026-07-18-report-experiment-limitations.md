# Technical Report Experiment Limitations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Làm rõ giới hạn của metric thực nghiệm trong technical report và biên dịch PDF cập nhật.

**Architecture:** Chỉ thay đổi nội dung LaTeX của hai chương hiện hữu. Chương kiểm thử diễn giải đúng phạm vi regression của baseline; chương kết luận tổng hợp các giới hạn và hướng đánh giá kế tiếp. `latexmk` xác nhận đầu ra PDF.

**Tech Stack:** LaTeX (`latexmk`), repository documentation.

## Global Constraints

- Không thay đổi dataset, detector, artifact hay bảng metric hiện có.
- Không sửa các tệp người dùng đang thay đổi ngoài `report/technical-report`.
- Giữ định vị dự án là Proof of Concept và không diễn giải metric thành hiệu năng sản xuất.

---

### Task 1: Bổ sung diễn giải giới hạn thực nghiệm

**Files:**
- Modify: `report/technical-report/chapters/06-verification.tex:21-67`
- Modify: `report/technical-report/chapters/07-conclusion.tex:9-18`
- Verify: `report/technical-report/main.pdf`

**Interfaces:**
- Consumes: Bảng baseline từ `artifacts/metrics.json`, dataset `data/logs_demo.csv` và `data/logs_risk_demo.csv`.
- Produces: Hai đoạn LaTeX mô tả phạm vi metric, cách hiểu password guessing theo event/alert và nhu cầu đánh giá context-risk ở cấp incident.

- [ ] **Step 1: Sửa diễn giải baseline**

Thêm sau đoạn nhận xét SQL Injection trong `chapters/06-verification.tex` đoạn LaTeX nêu rõ metric là kiểm chứng regression trên scenario tổng hợp; dataset chưa độc lập với thiết kế rule và chưa có hard negative đa dạng. Nêu rõ 10 event password guessing là một chuỗi, vì vậy kết quả event-level cần được bổ sung bằng alert/campaign-level trong đánh giá tương lai.

- [ ] **Step 2: Mở rộng giới hạn và hướng đánh giá**

Trong `chapters/07-conclusion.tex`, liệt kê ngắn gọn: dataset nhỏ/tổng hợp, không có hold-out độc lập, thiếu hard negative, và context-risk chưa có metric theo finding/incident. Giữ hướng phát triển là log ẩn danh có nhãn độc lập, nhiều thời đoạn, metric false positive/negative, độ trễ và chi phí triage.

- [ ] **Step 3: Biên dịch report**

Run: `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`

Working directory: `report/technical-report`

Expected: exit code `0` và `main.pdf` được tạo hoặc cập nhật.

- [ ] **Step 4: Kiểm tra warning chất lượng LaTeX**

Run: `rg "undefined|Undefined|Overfull \\hbox" main.log`

Working directory: `report/technical-report`

Expected: không có output.

- [ ] **Step 5: Commit**

Run: `git add report/technical-report/chapters/06-verification.tex report/technical-report/chapters/07-conclusion.tex && git diff --cached --check && git commit -m "docs: clarify report experiment limitations"`
