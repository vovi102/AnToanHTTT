# Thiết kế UI RBAC Nova Bank theo hướng sản phẩm

## Mục tiêu

Biến giao diện demo Nova Bank thành một cổng vận hành gần với sản phẩm thật:
chữ đủ lớn để trình chiếu, toàn bộ typography dùng sans-serif hiện đại, các màn
hình nghiệp vụ không hiển thị hướng dẫn demo hoặc chi tiết API, nhưng vẫn chứng
minh được backend thực thi RBAC bằng một trang truy cập bị từ chối.

## Vấn đề hiện tại

- Nhiều thành phần dùng cỡ chữ 8–11px: menu, nút, nhãn form, metadata giao dịch,
  audit và badge. Chúng khó đọc trên laptop và màn hình trình chiếu.
- Body dùng Arial nhưng tiêu đề dùng Georgia/Times New Roman, làm giao diện thiếu
  nhất quán.
- Login, banner, trang quản trị, giao dịch và panel proof hiển thị các cụm từ
  dành cho người phát triển như FastAPI URL, backend, endpoint, HTTP status,
  permission, SQLite, demo và kịch bản.
- Teller phải dùng panel “Kiểm tra bảo vệ backend”, một thao tác không tồn tại
  trong sản phẩm thực tế.
- Audit hiển thị raw outcome và `resource:action`, phù hợp cho debug hơn là cho
  nhân viên vận hành.

## Phạm vi

- Thay typography và spacing trên toàn bộ Next.js portal.
- Làm sạch nội dung hiển thị trên login, shell, giao dịch, phê duyệt, quản trị
  chính sách, quản trị nhân viên và audit.
- Thay panel proof bằng truy cập trực tiếp vào trang chi tiết phê duyệt.
- Bổ sung API đọc hồ sơ phê duyệt có kiểm tra quyền và ghi audit.
- Bổ sung route Next.js `/approvals/[reference]`.
- Đổi route quản trị hiển thị từ `/admin/demo-control` thành
  `/admin/policies`; endpoint nội bộ hiện có có thể giữ nguyên vì không hiển thị
  cho người dùng.
- Cập nhật tài liệu demo hợp nhất để dùng luồng mới và thuật ngữ mới.
- Không thay đổi role, permission, tài khoản seed, schema giao dịch hoặc mục
  tiêu nghiệp vụ của demo.

## Typography

Toàn bộ UI dùng một font stack duy nhất:

```css
Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif
```

Không tải font từ mạng và không dùng Georgia/Times New Roman. Nếu máy không có
Inter, hệ điều hành tự dùng Segoe UI hoặc font sans-serif tiếp theo.

Thang chữ:

| Thành phần | Cỡ chữ |
| --- | --- |
| Body và nội dung chính | 16px |
| Label, nút, metadata, badge, audit | tối thiểu 14px |
| Menu điều hướng | 15px |
| Tiêu đề section | 20–22px |
| Tiêu đề trang | 34–40px |
| Tiêu đề login | `clamp(48px, 5vw, 64px)` |
| Số tiền giao dịch | 30px |

Line-height của nội dung nằm trong khoảng 1.45–1.6. Tăng padding nút, card,
form và khoảng cách giữa các trường theo cỡ chữ mới. Không còn `font-size: 0`
để ẩn nhãn menu ở mobile; mobile giữ nhãn và cho phép cuộn ngang.

## Ngôn ngữ sản phẩm

### Login

Giữ thương hiệu Nova Bank, tiêu đề “Cổng nghiệp vụ nội bộ”, form tên đăng nhập,
mật khẩu và nút “Đăng nhập”. Xóa:

- URL FastAPI và health check;
- các bước user journey;
- tài khoản chuẩn bị sẵn và nút tự điền;
- “phiên đăng nhập thật”, “đăng nhập qua backend” và mô tả demo;
- hướng dẫn kỹ thuật trong thông báo lỗi.

Lỗi kết nối chỉ hiển thị: “Không thể kết nối hệ thống. Vui lòng thử lại hoặc
liên hệ quản trị viên.”

### Portal shell và chính sách

- “Điều khiển demo” thành “Chính sách phê duyệt”.
- `BASELINE` thành “Kiểm soát cơ bản”.
- `SECURE MODE`/RBAC banner thành “Phân tách nhiệm vụ”.
- Banner mô tả quy trình nghiệp vụ, không nói backend hoặc buổi demo.
- Trang chính sách bỏ “Bảng điều khiển trình diễn”, “Kịch bản 5 bước”, endpoint,
  permission và bypass.
- Hai lựa chọn chính sách được trình bày là “Kiểm soát cơ bản” và “Phân tách
  nhiệm vụ”; Admin có thể áp dụng chính sách.
- Chức năng reset vẫn nằm cuối trang Admin với nhãn “Khôi phục dữ liệu” và
  confirmation rõ ràng, không dùng từ demo trên giao diện.

### Giao dịch và phê duyệt

- Xóa “Dữ liệu từ SQLite”, “bắt đầu kịch bản”, “trạng thái tại backend” và mọi
  raw API proof.
- Teller ở chế độ phân tách nhiệm vụ thấy giao dịch “Đang chờ Kiểm soát viên
  phê duyệt”, không có nút tự duyệt hoặc panel kỹ thuật.
- Ở kiểm soát cơ bản, hành vi tự duyệt vẫn được giữ để so sánh trước/sau, nhưng
  copy dùng ngôn ngữ quy trình thay vì giải thích code.
- Hàng đợi Controller liên kết tới trang chi tiết `/approvals/[reference]` bằng
  nút “Xem và phê duyệt”.

### Audit

Giao diện giữ actor, role, thời gian, mã giao dịch và kết quả nhưng dịch dữ liệu
kỹ thuật:

| Raw value | Nhãn hiển thị |
| --- | --- |
| `allowed` | Đã cho phép |
| `denied` | Đã từ chối |
| `success` | Thành công |
| `failed` | Thất bại |
| `baseline_bypass` | Bỏ qua kiểm soát |
| `conflict` | Xung đột trạng thái |
| `transactions:approve` | Phê duyệt giao dịch |
| `transactions:create` | Tạo giao dịch |

Các action khác dùng bảng mapping tương tự và fallback tiếng Việt trung tính;
không ghép raw `resource:action` trên UI.

## Luồng truy cập bị từ chối

### Backend

Bổ sung:

```http
GET /approvals/{reference}
```

Endpoint yêu cầu phiên đăng nhập và đánh giá quyền phê duyệt:

1. Controller có `transactions:approve`: audit `allowed`, trả chi tiết giao
   dịch.
2. Teller ở “Kiểm soát cơ bản”: cho phép theo chính sách so sánh hiện có và ghi
   `baseline_bypass`.
3. Người dùng khác hoặc Teller khi “Phân tách nhiệm vụ” đang bật: audit
   `denied`, trả 403 và không thay đổi giao dịch.
4. Reference không tồn tại: người đã có quyền phê duyệt nhận 404. Người không
   có quyền vẫn nhận 403 trước khi hệ thống tiết lộ giao dịch có tồn tại hay
   không.

Việc đọc hồ sơ và việc POST phê duyệt dùng cùng một quyết định chính sách hoặc
cùng helper để tránh GET/POST bất nhất. POST hiện tại tiếp tục là nơi thay đổi
trạng thái và xử lý conflict.

### Frontend

Route mới:

```text
/approvals/[reference]
```

Khi mở route:

- 200: hiển thị thông tin giao dịch, người tạo, số tiền, tài khoản, nội dung và
  nút “Phê duyệt giao dịch”.
- 403: hiển thị trang sản phẩm “Không có quyền truy cập” với nội dung “Vai trò
  hiện tại không được phép phê duyệt giao dịch này.” và nút “Quay lại giao
  dịch”. Không render endpoint, HTTP status hoặc permission.
- 404: hiển thị “Không tìm thấy giao dịch”.
- lỗi kết nối: hiển thị thông báo hệ thống trung tính và nút thử lại.

Controller queue dùng route này. Teller không có link phê duyệt trong navigation;
người trình bày nhập trực tiếp URL với mã giao dịch để chứng minh server chặn
truy cập. Audit là bằng chứng thứ hai rằng denial đã xảy ra.

## Cấu trúc component

- Xóa `web/components/BackendProof.tsx`.
- Thu gọn `FeedbackState` và `Feedback` để không render endpoint/status/permission.
- `TransactionList` chỉ render card, hành động Baseline hoặc link tới approval
  detail theo presentation; bỏ proof state/callback.
- Tạo helper presentation cho mode label, outcome label và audit action label,
  có unit test độc lập.
- Tạo trang approval detail tự quản lý loading, denied, not-found, error và
  approval success.
- Đổi đường dẫn file trang Admin từ `admin/demo-control/page.tsx` sang
  `admin/policies/page.tsx`; cập nhật navigation và role home.

## Dữ liệu và bảo mật

- Không quyết định quyền dựa trên role ở frontend. Frontend chỉ dùng role để
  xây navigation; API luôn xác minh session và permission.
- Response 403 có thể tiếp tục chứa permission cho client nội bộ, nhưng component
  sản phẩm không hiển thị trường này.
- GET approval không thay đổi trạng thái giao dịch.
- Denial phải được commit vào audit trước khi raise HTTPException.
- Teller không được đọc hồ sơ phê duyệt ở chế độ phân tách nhiệm vụ dù biết mã
  giao dịch hợp lệ.

## Error handling

- 401 tiếp tục hết phiên và chuyển về login.
- 403 trên approval detail là trạng thái trang, không phải toast kỹ thuật.
- 404 và 409 có thông báo nghiệp vụ riêng.
- Network error không nhắc FastAPI, port hoặc health endpoint.
- Nút phê duyệt bị disabled khi request đang chạy và không gửi lặp.

## Kiểm thử

### Backend

- Teller ở RBAC gọi GET approval nhận 403, giao dịch vẫn Pending và audit có
  `denied` đúng reference.
- Controller gọi GET approval nhận 200 và audit có `allowed`.
- Teller ở Baseline có hành vi nhất quán với chính sách so sánh.
- Controller truy cập reference không tồn tại nhận 404; Teller ở RBAC vẫn nhận
  403 để không dò được sự tồn tại của giao dịch.
- POST approval và conflict tests hiện có tiếp tục pass.

### Frontend

- Navigation Admin trỏ tới `/admin/policies` và không còn “Điều khiển demo”.
- Mapping mode, outcome và action trả đúng nhãn nghiệp vụ.
- Approval presentation không còn `backend_proof`.
- Build sinh route `/approvals/[reference]`.
- Rà source JSX để không còn các chuỗi hiển thị FastAPI, endpoint, HTTP,
  permission, SQLite, “Kiểm tra bảo vệ backend”, “Gửi thử request vượt quyền”,
  “kịch bản” hoặc “demo”. Internal request path và tên type không thuộc phép rà
  nội dung hiển thị.
- Rà CSS để không còn Georgia/Times New Roman, `font-size: 0`, hoặc font-size
  dưới 14px.
- Chạy toàn bộ pytest, Vitest và Next.js production build.

## Cập nhật tài liệu

`DEMO_RBAC_NOVA_BANK.md` được cập nhật theo route và thuật ngữ mới:

- Người trình bày lấy reference của giao dịch thứ hai và mở
  `/approvals/<reference>` trong tab Teller.
- Trang “Không có quyền truy cập” và giao dịch vẫn Pending là checkpoint.
- Controller mở cùng reference từ hàng đợi và phê duyệt.
- Admin dùng “Chính sách phê duyệt” và “Khôi phục dữ liệu”.
- Tài liệu có thể giải thích backend/audit cho giảng viên; giới hạn “không lộ
  API” chỉ áp dụng cho bề mặt sản phẩm Next.js.

## Ngoài phạm vi

- Không đổi cơ chế session, password hashing hoặc database.
- Không thêm role/permission mới.
- Không thiết kế trang khách hàng, số dư hoặc core banking khác.
- Không thay đổi Streamlit, CLI, paper/report hoặc dữ liệu thực nghiệm.
