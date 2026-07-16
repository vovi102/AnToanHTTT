"use client";

import type { FeedbackState, Transaction } from "../lib/types";

export function BackendProof({ transaction, running, result, onRun }: {
  transaction: Transaction;
  running: boolean;
  result: FeedbackState | null;
  onRun: () => void;
}) {
  return (
    <details className="proof-panel">
      <summary><span>Kiểm tra bảo vệ backend</span><small>Dành riêng cho phần chứng minh RBAC</small></summary>
      <div className="proof-body">
        <p>Giao diện bình thường đã ẩn nút duyệt. Thao tác dưới đây cố ý gọi trực tiếp endpoint được bảo vệ.</p>
        <code>POST /transactions/{transaction.reference}/approve</code>
        <button className="button danger" disabled={running} onClick={onRun}>{running ? "Đang gửi request…" : "Gửi thử request vượt quyền"}</button>
        {result && <div className="proof-result"><b>{result.title}</b><span>{result.endpoint} → HTTP {result.status} · cần {result.permission}</span><p>{result.message}</p></div>}
      </div>
    </details>
  );
}
