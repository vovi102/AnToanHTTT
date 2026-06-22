# CHƯƠNG 5. THỰC NGHIỆM VÀ ĐÁNH GIÁ

## 5.1. Thiết lập

Thực nghiệm dùng `data/logs_demo.csv`, `data/rbac_seed.json` và `config/default.toml`. Password guessing dùng ngưỡng 5 lần trong 300 giây; severity dùng ba mốc 30, 60 và 85. CLI sinh alert trước, sau đó lệnh evaluate đối chiếu event IDs với nhãn kỳ vọng; số liệu không được nhập thủ công.

## 5.2. Kết quả

| Risk type | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| SQL Injection | 9 | 0 | 1 | 50 | 1.0000 | 0.9000 | 0.9474 |
| Password guessing | 10 | 0 | 0 | 50 | 1.0000 | 1.0000 | 1.0000 |
| Unauthorized access | 10 | 0 | 0 | 50 | 1.0000 | 1.0000 | 1.0000 |
| Macro average | — | — | — | — | 1.0000 | 0.9667 | 0.9825 |

Run metadata ghi nhận 60 dòng hợp lệ, 0 dòng lỗi và 20 alert. Password guessing tạo một alert cấp chuỗi nhưng alert chứa 10 event IDs, vì vậy metric tính đúng cả mười event tấn công.

## 5.3. Phân tích

Hai luật password guessing và unauthorized access đạt kết quả tuyệt đối trên dataset có chủ đích. Kết quả này chứng minh implementation phù hợp đặc tả và scenario, không chứng minh khả năng khái quát trên log thực. SQL Injection bỏ sót một trong mười biến thể, cho thấy tập regex giải thích được nhưng giới hạn; mở rộng pattern có thể tăng recall nhưng cũng có nguy cơ làm giảm precision.

Không có FP trong tập demo vì benign scenario được thiết kế rõ ràng. Đánh giá tiếp theo nên bổ sung request chứa từ khóa SQL trong ngôn ngữ tự nhiên, encoding, comment lồng nhau, login phân tán qua nhiều IP và quyền thay đổi theo phiên để tạo bài toán gần thực tế hơn.

## 5.4. Khả năng tái lập

README cung cấp đủ lệnh khởi tạo, phân tích, đánh giá và chạy test. `run_metadata.json` giữ nguồn dữ liệu và config; `metrics.json` giữ confusion matrix. Artifact được tái sinh từ CLI thay vì chỉnh sửa bằng tay.

