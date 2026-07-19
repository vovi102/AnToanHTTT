# RBAC Database Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mở rộng báo cáo kỹ thuật bằng hai ERD và phần giải thích đầy đủ, chính xác về Core RBAC cùng các bảng vận hành của Nova Bank.

**Architecture:** Giữ `chapters/02-architecture.tex` làm nơi giải thích mô hình dữ liệu, nhưng tách hình vẽ thành hai tệp TikZ độc lập để mỗi hình có một trách nhiệm rõ ràng. ERD thứ nhất mô tả năm bảng Core RBAC; ERD thứ hai mô tả năm bảng hỗ trợ và các liên kết thực tế với `users`. Nội dung chỉ phản ánh schema hiện có trong `src/rbac_guard/rbac.py`, không thay đổi mã nguồn hay database.

**Tech Stack:** LaTeX, TikZ, `tabularx`, `booktabs`, SQLite schema trong Python, `latexmk`/pdfLaTeX.

## Global Constraints

- Chỉ sửa báo cáo kỹ thuật; không thay đổi schema SQLite, seed data, API hoặc giao diện.
- Trình bày mô hình theo hai lớp: Core RBAC và tích hợp Nova Bank.
- Không mô tả `audit_logs.username` hoặc `audit_logs.role_at_event` là khóa ngoại.
- Không tuyên bố PoC đã triển khai role hierarchy, session activation hay Separation of Duty tổng quát.
- Tên bảng, cột, miền `CHECK` và quan hệ phải khớp hằng `SCHEMA` trong `src/rbac_guard/rbac.py`.

## File Structure

- Create: `report/technical-report/figures/rbac-core-erd.tex` — ERD của năm bảng Core RBAC.
- Create: `report/technical-report/figures/nova-bank-data-erd.tex` — ERD của năm bảng hỗ trợ và liên kết với `users`.
- Modify: `report/technical-report/chapters/02-architecture.tex` — văn bản giải thích, bảng từ điển dữ liệu, hình và luồng kiểm tra quyền.

---

### Task 1: Bổ sung ERD và giải thích Core RBAC

**Files:**
- Create: `report/technical-report/figures/rbac-core-erd.tex`
- Modify: `report/technical-report/chapters/02-architecture.tex:66-79`

**Interfaces:**
- Consumes: hằng `SCHEMA` và truy vấn `RBACRepository.has_permission()` trong `src/rbac_guard/rbac.py`.
- Produces: hình có label `fig:rbac-core-erd` và bảng có label `tab:rbac-core-schema` để chương kiến trúc tham chiếu.

- [ ] **Step 1: Tạo ERD Core RBAC**

Tạo `report/technical-report/figures/rbac-core-erd.tex` với nội dung:

```tex
\begin{tikzpicture}[
  entity/.style={draw, rounded corners, align=left, font=\scriptsize,
    inner sep=2.5mm, minimum height=27mm, text width=27mm, fill=blue!5},
  link/.style={-Latex, thick},
  node distance=7mm
]
\node[entity] (users) {\textbf{users}\\
  \underline{id}\\username [UQ]\\status\\display\_name\\password\_hash};
\node[entity, right=of users] (userroles) {\textbf{user\_roles}\\
  \underline{user\_id} [FK]\\\underline{role\_id} [FK]\\PK(user\_id, role\_id)};
\node[entity, right=of userroles] (roles) {\textbf{roles}\\
  \underline{id}\\name [UQ]};
\node[entity, right=of roles] (rolepermissions) {\textbf{role\_permissions}\\
  \underline{role\_id} [FK]\\\underline{permission\_id} [FK]\\PK(role\_id, permission\_id)};
\node[entity, right=of rolepermissions] (permissions) {\textbf{permissions}\\
  \underline{id}\\resource\\action\\UQ(resource, action)};
\draw[link] (users) -- node[above, font=\scriptsize]{1:N} (userroles);
\draw[link] (roles) -- node[above, font=\scriptsize]{1:N} (userroles);
\draw[link] (roles) -- node[above, font=\scriptsize]{1:N} (rolepermissions);
\draw[link] (permissions) -- node[above, font=\scriptsize]{1:N} (rolepermissions);
\end{tikzpicture}
```

- [ ] **Step 2: Thay phần mở đầu của mục “Mô hình dữ liệu RBAC”**

Giữ tiêu đề section hiện tại và thay hai đoạn tại dòng 68--79 bằng nội dung sau:

```tex
Mô hình dữ liệu được chia thành lớp Core RBAC và lớp hỗ trợ vận hành Nova Bank.
Lớp Core RBAC trong Hình~\ref{fig:rbac-core-erd} gồm năm quan hệ
\texttt{users}, \texttt{roles}, \texttt{permissions},
\texttt{user\_roles} và \texttt{role\_permissions}. Hai bảng liên kết chuyển
hai quan hệ nhiều--nhiều user--role và role--permission thành các quan hệ
một--nhiều có khóa ngoại rõ ràng. Cấu trúc này tránh gán permission trực tiếp
cho từng user và giữ role làm đơn vị quản trị chính sách.

\begin{figure}[htbp]
\centering
\resizebox{\textwidth}{!}{\input{figures/rbac-core-erd}}
\caption{ERD của lớp Core RBAC. UQ ký hiệu ràng buộc duy nhất.}
\label{fig:rbac-core-erd}
\end{figure}

\begin{table}[htbp]
\centering
\small
\begin{tabularx}{\textwidth}{p{0.19\textwidth}p{0.25\textwidth}X}
\toprule
Quan hệ & Khóa và ràng buộc chính & Vai trò trong mô hình \\
\midrule
\texttt{users} & PK \texttt{id}; UQ \texttt{username}; \texttt{status} thuộc \texttt{active}/\texttt{disabled} & Lưu định danh, trạng thái, tên hiển thị và password hash của người dùng. \\
\texttt{roles} & PK \texttt{id}; UQ \texttt{name} & Đại diện chức năng nghiệp vụ như Administrator, Teller, Controller và Auditor. \\
\texttt{permissions} & PK \texttt{id}; UQ(\texttt{resource}, \texttt{action}) & Biểu diễn một quyền dưới dạng cặp tài nguyên--hành động. \\
\texttt{user\_roles} & PK(\texttt{user\_id}, \texttt{role\_id}); hai FK & Gán role cho user và ngăn một phép gán bị lặp. \\
\texttt{role\_permissions} & PK(\texttt{role\_id}, \texttt{permission\_id}); hai FK & Gán permission cho role và ngăn một quyền bị cấp lặp. \\
\bottomrule
\end{tabularx}
\caption{Từ điển dữ liệu của lớp Core RBAC.}
\label{tab:rbac-core-schema}
\end{table}
```

- [ ] **Step 3: Bổ sung luồng kiểm tra quyền ngay sau bảng Core RBAC**

Chèn nội dung sau trước phần lớp tích hợp Nova Bank:

```tex
Khi API cần kiểm tra quyền, repository nối đường
\texttt{users $\rightarrow$ user\_roles $\rightarrow$ role\_permissions
$\rightarrow$ permissions}, lọc theo \texttt{username}, trạng thái
\texttt{active} và cặp \texttt{resource:action}, rồi chỉ cần xác nhận có ít
nhất một hàng phù hợp. \texttt{roles} không xuất hiện trực tiếp trong truy vấn
quyết định vì hai bảng liên kết đã chia sẻ \texttt{role\_id}; bảng này vẫn cần
thiết để quản trị tên role và hiển thị ma trận quyền. Backend thực hiện truy vấn
này trước hành động được bảo vệ, do đó việc frontend ẩn nút chỉ cải thiện trải
nghiệm và không phải là cơ chế phân quyền.

Trong Nova Bank, \texttt{transactions:read\_own} giới hạn Teller ở giao dịch
do chính họ tạo, còn \texttt{transactions:read\_all} cho phép Controller,
Auditor hoặc Administrator đọc phạm vi rộng hơn. Permission
\texttt{transactions:approve} chỉ được seed cho Controller. Đây là chính sách
Maker--Checker cụ thể ở API, không phải mô hình Separation of Duty tổng quát;
schema hiện tại chưa có bảng constraint để biểu diễn xung đột nhiệm vụ.
```

- [ ] **Step 4: Biên dịch để kiểm tra Task 1**

Run:

```bash
cd report/technical-report
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Expected: exit code `0`, sinh `main.pdf`, không có lỗi `Undefined control sequence` hoặc `LaTeX Error`.

- [ ] **Step 5: Commit Task 1**

```bash
git add report/technical-report/figures/rbac-core-erd.tex report/technical-report/chapters/02-architecture.tex
git commit -m "docs: document core RBAC database design"
```

### Task 2: Bổ sung ERD tích hợp và các ràng buộc bảo mật

**Files:**
- Create: `report/technical-report/figures/nova-bank-data-erd.tex`
- Modify: `report/technical-report/chapters/02-architecture.tex`

**Interfaces:**
- Consumes: section Core RBAC và node logic `users` từ Task 1; hằng `SCHEMA`, `hash_password()`, `create_session()` và `_connect()` trong `src/rbac_guard/rbac.py`.
- Produces: hình có label `fig:nova-bank-data-erd` và bảng có label `tab:nova-bank-data-schema`.

- [ ] **Step 1: Tạo ERD lớp tích hợp Nova Bank**

Tạo `report/technical-report/figures/nova-bank-data-erd.tex`:

```tex
\begin{tikzpicture}[
  entity/.style={draw, rounded corners, align=left, font=\scriptsize,
    inner sep=2.5mm, minimum height=24mm, text width=36mm, fill=orange!9},
  core/.style={entity, fill=blue!8},
  link/.style={-Latex, thick},
  snapshot/.style={-Latex, thick, dashed},
  note/.style={font=\scriptsize, align=center},
  node distance=9mm and 17mm
]
\node[core] (users) {\textbf{users}\\\underline{id}\\username [UQ]\\status};
\node[entity, above left=of users] (sessions) {\textbf{sessions}\\
  \underline{token\_hash}\\user\_id [FK]\\expires\_at};
\node[entity, right=of users, text width=42mm] (transactions) {\textbf{transactions}\\
  \underline{id}; reference [UQ]\\created\_by [FK]\\approved\_by [FK, nullable]\\status; amount\_vnd};
\node[entity, below right=of users, text width=42mm] (audit) {\textbf{audit\_logs}\\
  \underline{id}\\username; role\_at\_event\\resource; action; outcome\\transaction\_reference};
\node[entity, below left=of users] (accounts) {\textbf{customer\_accounts}\\
  \underline{id}\\customer\_name\\phone; address};
\node[entity, below=18mm of users] (settings) {\textbf{demo\_settings}\\
  \underline{key}\\value};
\draw[link] (users) -- node[above left, note]{1:N\\owns} (sessions);
\draw[link] (users) -- node[above, note]{1:N\\creates} (transactions);
\draw[link] (users) to[bend left=18] node[below, note]{0..1:N\\approves} (transactions);
\draw[snapshot] (users) -- node[above, sloped, note]{text snapshot; no FK} (audit);
\node[note, below=2mm of accounts] {independent reference data};
\node[note, below=2mm of settings] {independent key--value policy};
\end{tikzpicture}
```

- [ ] **Step 2: Chèn phần lớp dữ liệu tích hợp sau phần Core RBAC**

Chèn nội dung sau trước section “Tích hợp audit log với pipeline”:

```tex
\subsection{Các bảng hỗ trợ vận hành Nova Bank}

Lớp thứ hai trong Hình~\ref{fig:nova-bank-data-erd} mở rộng Core RBAC bằng dữ
liệu phiên, giao dịch, audit và cấu hình demo. Chỉ các đường liền trong hình là
khóa ngoại. \texttt{audit\_logs.username} và \texttt{role\_at\_event} là ảnh
chụp văn bản tại thời điểm sự kiện; cách lưu này giữ được ngữ cảnh điều tra nếu
quan hệ role của user thay đổi sau đó, nhưng database không bảo đảm tham chiếu
cho hai trường này.

\begin{figure}[htbp]
\centering
\resizebox{0.95\textwidth}{!}{\input{figures/nova-bank-data-erd}}
\caption{ERD của lớp dữ liệu hỗ trợ vận hành Nova Bank.}
\label{fig:nova-bank-data-erd}
\end{figure}

\begin{table}[htbp]
\centering
\small
\begin{tabularx}{\textwidth}{p{0.20\textwidth}p{0.27\textwidth}X}
\toprule
Quan hệ & Khóa và ràng buộc chính & Vai trò trong demo \\
\midrule
\texttt{sessions} & PK \texttt{token\_hash}; FK \texttt{user\_id} & Lưu token đã băm và thời điểm hết hạn của phiên đăng nhập. \\
\texttt{transactions} & PK \texttt{id}; UQ \texttt{reference}; hai FK tới \texttt{users}; \texttt{amount\_vnd}>0; status thuộc \texttt{pending}/\texttt{approved} & Lưu giao dịch, người tạo và người phê duyệt tùy chọn. \\
\texttt{audit\_logs} & PK \texttt{id}; outcome thuộc sáu giá trị cho phép & Lưu quyết định xác thực, phân quyền, policy và dấu vết giao dịch để xuất sang pipeline. \\
\texttt{customer\_accounts} & PK \texttt{id} & Dữ liệu khách hàng tối giản phục vụ thao tác đọc/cập nhật trong demo. \\
\texttt{demo\_settings} & PK \texttt{key} & Lưu chế độ \texttt{baseline}/\texttt{rbac}; miền giá trị được kiểm tra ở tầng repository. \\
\bottomrule
\end{tabularx}
\caption{Từ điển dữ liệu của lớp hỗ trợ Nova Bank.}
\label{tab:nova-bank-data-schema}
\end{table}

\subsection{Ràng buộc toàn vẹn và bảo vệ dữ liệu xác thực}

SQLite được bật \texttt{PRAGMA foreign\_keys = ON} trên từng connection. Khóa
chính ghép ngăn gán trùng user--role và role--permission; các ràng buộc
\texttt{UNIQUE}, \texttt{CHECK} và \texttt{NOT NULL} loại bỏ trạng thái cấu
trúc không hợp lệ trước khi logic ứng dụng xử lý. Các câu lệnh nhận dữ liệu động
dùng placeholder tham số của SQLite thay vì nối chuỗi SQL. Context manager của
connection bao quanh các thao tác seed và cập nhật nhiều bước để commit khi
thành công hoặc rollback khi phát sinh ngoại lệ.

Mật khẩu không được lưu trực tiếp: repository tạo salt ngẫu nhiên 16 byte và
dẫn xuất khóa bằng scrypt với $N=2^{14}$, $r=8$, $p=1$; việc so sánh digest dùng
hàm constant-time. Token phiên ngẫu nhiên chỉ trả cho client một lần, còn
database lưu SHA-256 của token cùng \texttt{expires\_at}. Đây là kiểm soát phù
hợp cho PoC cục bộ; báo cáo không suy rộng thành cơ chế quản lý khóa hoặc phiên
phân tán ở môi trường production.
```

- [ ] **Step 3: Đối chiếu toàn bộ tên và ràng buộc với schema**

Run:

```bash
rg -n "CREATE TABLE|CHECK|UNIQUE|REFERENCES|PRAGMA foreign_keys|scrypt|sha256" src/rbac_guard/rbac.py
```

Expected: thấy đủ 10 lệnh `CREATE TABLE`; các miền `users.status`, `audit_logs.outcome`, `transactions.status`; FK giao dịch và session; cùng các lời gọi `scrypt` và `sha256` được mô tả trong báo cáo.

- [ ] **Step 4: Biên dịch để kiểm tra Task 2**

Run:

```bash
cd report/technical-report
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Expected: exit code `0`; không có lỗi TikZ/LaTeX; cả `fig:rbac-core-erd`, `fig:nova-bank-data-erd`, `tab:rbac-core-schema` và `tab:nova-bank-data-schema` được resolve sau các lượt chạy của `latexmk`.

- [ ] **Step 5: Commit Task 2**

```bash
git add report/technical-report/figures/nova-bank-data-erd.tex report/technical-report/chapters/02-architecture.tex
git commit -m "docs: document Nova Bank database integration"
```

### Task 3: Kiểm tra hoàn chỉnh báo cáo

**Files:**
- Verify: `report/technical-report/chapters/02-architecture.tex`
- Verify: `report/technical-report/figures/rbac-core-erd.tex`
- Verify: `report/technical-report/figures/nova-bank-data-erd.tex`

**Interfaces:**
- Consumes: toàn bộ nội dung từ Task 1 và Task 2.
- Produces: báo cáo biên dịch được, không có placeholder, tham chiếu hỏng hoặc lỗi định dạng Git.

- [ ] **Step 1: Quét placeholder và tham chiếu cần thiết**

```bash
rg -n 'T[B]D|T[O]DO|P[L]ACEHOLDER' report/technical-report/chapters/02-architecture.tex report/technical-report/figures/rbac-core-erd.tex report/technical-report/figures/nova-bank-data-erd.tex
rg -n "fig:rbac-core-erd|fig:nova-bank-data-erd|tab:rbac-core-schema|tab:nova-bank-data-schema" report/technical-report/chapters/02-architecture.tex
```

Expected: lệnh đầu không trả kết quả vì không có cụm giữ chỗ; lệnh thứ hai cho thấy mỗi label mới xuất hiện trong định nghĩa và ít nhất một tham chiếu phù hợp.

- [ ] **Step 2: Biên dịch sạch và kiểm tra cảnh báo tham chiếu**

```bash
cd report/technical-report
latexmk -C main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
rg -n "undefined references|multiply defined|LaTeX Error|Undefined control sequence" main.log
```

Expected: hai lệnh `latexmk` exit code `0`; lệnh `rg` cuối không trả kết quả.

- [ ] **Step 3: Kiểm tra diff**

```bash
git diff --check
git status --short
```

Expected: `git diff --check` không có output; status chỉ chứa hiện vật biên dịch bị ignore hoặc không có thay đổi chưa commit.

- [ ] **Step 4: Commit sửa lỗi kiểm chứng nếu có**

Nếu Step 1--3 buộc phải chỉnh nội dung hoặc hình, stage đúng ba tệp trong phạm vi và commit:

```bash
git add report/technical-report/chapters/02-architecture.tex report/technical-report/figures/rbac-core-erd.tex report/technical-report/figures/nova-bank-data-erd.tex
git commit -m "docs: polish RBAC database report section"
```

Nếu không có thay đổi sau hai commit trước, bỏ qua commit này.
