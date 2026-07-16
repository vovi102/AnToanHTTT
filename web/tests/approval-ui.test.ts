import "@testing-library/jest-dom/vitest";

import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { createElement } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { Feedback } from "../components/Feedback";
import { TransactionList } from "../components/TransactionList";
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

afterEach(cleanup);

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
