import "@testing-library/jest-dom/vitest";

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const approvalMocks = vi.hoisted(() => ({
  push: vi.fn(),
  request: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useParams: () => ({ reference: "TXN-2026-0001" }),
  useRouter: () => ({ push: approvalMocks.push }),
}));

vi.mock("../components/AuthProvider", () => ({
  useAuth: () => ({
    user: {
      id: "controller-1",
      username: "controller01",
      display_name: "Kiem Soat Vien",
      roles: ["controller"],
    },
    request: approvalMocks.request,
  }),
}));

import ApprovalDetailPage from "../app/(portal)/approvals/[reference]/page";
import { Feedback } from "../components/Feedback";
import { TransactionList } from "../components/TransactionList";
import { ApiError } from "../lib/api";
import type { FeedbackState, Transaction } from "../lib/types";

const transaction: Transaction = {
  id: 1,
  reference: "TXN-2026-0001",
  source_account: "1234567890",
  destination_account: "9876543210",
  beneficiary_name: "Nguyen Van B",
  amount_vnd: 1_500_000,
  description: "Thanh toan hoa don",
  status: "pending",
  created_by: "teller01",
  created_at: "2026-07-16T08:00:00Z",
  approved_by: null,
  approved_at: null,
};

beforeEach(() => {
  approvalMocks.push.mockReset();
  approvalMocks.request.mockReset();
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("approval product UI", () => {
  it("keeps feedback focused on the business title and message", () => {
    const value = {
      kind: "error",
      title: "Không thể phê duyệt",
      message: "Bạn không có quyền xử lý giao dịch này.",
      endpoint: "POST /transactions/TXN-2026-0001/approve",
      status: 403,
      permission: "transactions.approve",
    } as FeedbackState;

    const { container } = render(createElement(Feedback, { value }));

    expect(screen.getByText(value.title)).toBeInTheDocument();
    expect(screen.getByText(value.message)).toBeInTheDocument();
    expect(container.querySelector("code")).not.toBeInTheDocument();
  });

  it("links controllers to the approval detail route", () => {
    render(createElement(TransactionList, {
      transactions: [transaction],
      mode: "rbac",
      roles: ["controller"],
    }));

    expect(screen.getByRole("link", { name: /Xem và phê duyệt/ }))
      .toHaveAttribute("href", `/approvals/${transaction.reference}`);
  });

  it("shows tellers that an RBAC transaction is waiting for approval", () => {
    render(createElement(TransactionList, {
      transactions: [transaction],
      mode: "rbac",
      roles: ["teller"],
    }));

    expect(screen.getByText("Đang chờ Kiểm soát viên phê duyệt")).toBeInTheDocument();
  });

  it("offers the baseline business action and handles an absent callback", () => {
    const onApprove = vi.fn();
    const { rerender } = render(createElement(TransactionList, {
      transactions: [transaction],
      mode: "baseline",
      roles: ["teller"],
      onApprove,
    }));

    fireEvent.click(screen.getByRole("button", { name: "Hoàn tất giao dịch" }));
    expect(onApprove).toHaveBeenCalledWith(transaction);

    rerender(createElement(TransactionList, {
      transactions: [transaction],
      mode: "baseline",
      roles: ["teller"],
    }));
    expect(() => fireEvent.click(screen.getByRole("button", { name: "Hoàn tất giao dịch" })))
      .not.toThrow();
  });

  it("uses a product empty state without scenario language", () => {
    render(createElement(TransactionList, {
      transactions: [],
      mode: "rbac",
      roles: ["controller"],
    }));

    expect(screen.getByText("Chưa phát sinh giao dịch")).toBeInTheDocument();
    expect(screen.queryByText(/kịch bản/i)).not.toBeInTheDocument();
  });
});

describe("approval detail route", () => {
  it("maps a forbidden approval resource to the denied state", async () => {
    approvalMocks.request.mockRejectedValueOnce(new ApiError(403, "Forbidden"));

    render(createElement(ApprovalDetailPage));

    expect(await screen.findByRole("heading", { name: "Không có quyền truy cập" }))
      .toBeInTheDocument();
  });

  it("maps a missing approval resource to the not-found state", async () => {
    approvalMocks.request.mockRejectedValueOnce(new ApiError(404, "Not found"));

    render(createElement(ApprovalDetailPage));

    expect(await screen.findByRole("heading", { name: "Không tìm thấy giao dịch" }))
      .toBeInTheDocument();
  });

  it("maps other load failures to the retryable error state", async () => {
    approvalMocks.request.mockRejectedValueOnce(new ApiError(500, "Server error"));

    render(createElement(ApprovalDetailPage));

    expect(await screen.findByRole("heading", { name: "Không thể tải giao dịch" }))
      .toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Thử lại" })).toBeInTheDocument();
  });

  it("approves a ready transaction and displays success", async () => {
    const approved = {
      ...transaction,
      status: "approved" as const,
      approved_by: "controller01",
      approved_at: "2026-07-16T08:05:00Z",
    };
    approvalMocks.request
      .mockResolvedValueOnce(transaction)
      .mockResolvedValueOnce(approved);
    vi.spyOn(window, "confirm").mockReturnValue(true);
    render(createElement(ApprovalDetailPage));

    fireEvent.click(await screen.findByRole("button", { name: "Phê duyệt giao dịch" }));

    expect(await screen.findByText("Phê duyệt thành công")).toBeInTheDocument();
    expect(screen.getByText("Đã phê duyệt")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Phê duyệt giao dịch" }))
      .not.toBeInTheDocument();
  });

  it("preserves conflict feedback after refreshing a transaction processed elsewhere", async () => {
    const approved = {
      ...transaction,
      status: "approved" as const,
      approved_by: "controller02",
      approved_at: "2026-07-16T08:06:00Z",
    };
    approvalMocks.request
      .mockResolvedValueOnce(transaction)
      .mockRejectedValueOnce(new ApiError(409, "Giao dịch đã được phê duyệt"))
      .mockResolvedValueOnce(approved);
    vi.spyOn(window, "confirm").mockReturnValue(true);
    render(createElement(ApprovalDetailPage));

    fireEvent.click(await screen.findByRole("button", { name: "Phê duyệt giao dịch" }));

    await waitFor(() => expect(approvalMocks.request).toHaveBeenCalledTimes(3));
    expect(await screen.findByText("Đã phê duyệt")).toBeInTheDocument();
    expect(screen.getByText("Giao dịch đã được xử lý")).toBeInTheDocument();
  });
});
