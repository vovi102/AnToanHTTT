import type { SecurityMode } from "./types";

const modes: Record<SecurityMode, { title: string; description: string }> = {
  baseline: {
    title: "Kiểm soát cơ bản",
    description: "Giao dịch viên có thể hoàn tất giao dịch trong một bước.",
  },
  rbac: {
    title: "Phân tách nhiệm vụ",
    description: "Giao dịch cần Kiểm soát viên độc lập phê duyệt.",
  },
};

const outcomes: Record<string, string> = {
  allowed: "Đã cho phép",
  denied: "Đã từ chối",
  success: "Thành công",
  failed: "Thất bại",
  baseline_bypass: "Bỏ qua kiểm soát",
  conflict: "Xung đột trạng thái",
};

const actions: Record<string, string> = {
  "transactions:create": "Tạo giao dịch",
  "transactions:read": "Tra cứu giao dịch",
  "transactions:review": "Xem hồ sơ phê duyệt",
  "transactions:approve": "Phê duyệt giao dịch",
  "users:manage": "Quản lý nhân viên",
  "demo:configure": "Cập nhật chính sách phê duyệt",
  "audit_logs:read": "Xem lịch sử hoạt động",
  "session:login": "Đăng nhập",
  "session:logout": "Đăng xuất",
};

export function modePresentation(mode: SecurityMode) {
  return modes[mode];
}

export function auditOutcomeLabel(outcome: string): string {
  return outcomes[outcome] ?? "Không xác định";
}

export function auditActionLabel(resource: string, action: string): string {
  return actions[`${resource}:${action}`] ?? "Hoạt động hệ thống";
}
