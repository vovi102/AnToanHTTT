# Complete Section 4.2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bổ sung phần diễn giải kiến trúc cho mục 4.2 để mục này không còn phụ thuộc hoàn toàn vào vị trí của bảng LaTeX.

**Architecture:** Thêm ba đoạn văn ngay sau tiêu đề “Các thành phần chính” và trước bảng hiện có. Các đoạn lần lượt mô tả phân lớp thành phần, ranh giới trách nhiệm bảo mật và luồng dữ liệu đầu-cuối; bảng tiếp tục đóng vai trò tổng hợp.

**Tech Stack:** LaTeX, `report` document class, `latexmk`.

## Global Constraints

- Giữ nguyên bảng thành phần, sơ đồ kiến trúc, mô hình dữ liệu và số liệu thực nghiệm.
- Chỉ mô tả các khả năng đã có trong mã nguồn và báo cáo.
- Dùng tiếng Việt theo văn phong báo cáo kỹ thuật và thuật ngữ nhất quán với các chương khác.
- Bản PDF phải biên dịch thành công, không có tham chiếu chưa xác định hoặc lỗi tràn dòng mới.

---

### Task 1: Bổ sung phần diễn giải mục 4.2

**Files:**
- Modify: `report/technical-report/chapters/02-architecture.tex`
- Verify: `report/technical-report/main.pdf`

**Interfaces:**
- Consumes: cấu trúc thành phần và luồng dữ liệu đã trình bày tại mục 4.1.
- Produces: ba đoạn văn dẫn nhập cho Bảng `tab:components` và cầu nối sang mục 4.3.

- [ ] **Step 1: Chèn nội dung sau tiêu đề mục 4.2**

Chèn ngay sau `\section{Các thành phần chính}`:

```latex
Các thành phần của hệ thống được tổ chức thành bốn lớp trách nhiệm. Lớp trình
bày gồm giao diện Next.js, tiếp nhận thao tác của người dùng nhưng không tự đưa
ra quyết định phân quyền. Lớp nghiệp vụ và kiểm soát truy cập nằm tại FastAPI,
nơi xác thực phiên, kiểm tra permission, áp dụng chính sách nghiệp vụ và tạo
bản ghi audit cho mỗi hành động cần theo dõi. Lớp lưu trữ sử dụng SQLite cùng
\texttt{RBACRepository} để duy trì nhất quán giữa user, role, permission, phiên
đăng nhập và trạng thái giao dịch.

Ranh giới trách nhiệm này bảo đảm dữ liệu do trình duyệt gửi lên chỉ được xem
là yêu cầu, không phải bằng chứng về quyền hạn. FastAPI tra cứu quyền từ
repository trước khi thực thi thao tác; frontend chỉ hiển thị kết quả do API
trả về. Vì vậy, việc ẩn một nút trên giao diện không thay thế cho kiểm soát ở
backend, và một yêu cầu gọi trực tiếp endpoint vẫn phải đi qua cùng cơ chế xác
thực và phân quyền.

Ở nhánh giám sát, audit adapter chuyển các sự kiện xác thực và phân quyền trong
Nova Bank sang hợp đồng Event chung. Parser chuẩn hóa dữ liệu, tập luật phát
hiện chỉ báo, bộ chấm điểm gán mức rủi ro và reporter ghi các artifact phục vụ
điều tra. Chuỗi xử lý này tách schema nghiệp vụ khỏi logic phát hiện, đồng thời
cho phép truy vết từ một quyết định tại API tới cảnh báo hoặc incident tương
ứng. Bảng~\ref{tab:components} tổng hợp trách nhiệm cụ thể của từng thành phần.
```

- [ ] **Step 2: Kiểm tra thay đổi văn bản**

Run:

```bash
git diff --check
```

Expected: lệnh kết thúc với mã `0` và không in lỗi whitespace.

- [ ] **Step 3: Biên dịch sạch tài liệu**

Run:

```bash
cd report/technical-report
latexmk -C
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Expected: `latexmk` kết thúc với mã `0` và tạo `main.pdf`.

- [ ] **Step 4: Kiểm tra cảnh báo bố cục và tham chiếu**

Run:

```bash
rg -n "Overfull|undefined references|Citation.*undefined|Reference.*undefined" main.log
```

Expected: không có kết quả mới liên quan đến mục 4.2; tham chiếu `tab:components` được giải quyết sau chu kỳ biên dịch.

- [ ] **Step 5: Kiểm tra trực quan trang chứa mục 4.2**

Mở `report/technical-report/main.pdf` và xác nhận tiêu đề mục 4.2 đi kèm ít
nhất một đoạn văn; bảng vẫn hiển thị đầy đủ và phần chuyển sang mục 4.3 không
tạo khoảng trắng bất thường.

- [ ] **Step 6: Commit thay đổi**

```bash
git add report/technical-report/chapters/02-architecture.tex \
  docs/superpowers/plans/2026-07-19-complete-section-4-2.md
git commit -m "docs: complete architecture components section"
```
