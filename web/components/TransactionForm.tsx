"use client";

import { FormEvent, useState } from "react";

import type { Transaction } from "../lib/types";
import { ApiError } from "../lib/api";
import { useAuth } from "./AuthProvider";

const initialForm = {
  source_account: "001100001234",
  destination_account: "002200005678",
  beneficiary_name: "Lê Bình",
  amount_vnd: "50000000",
  description: "Thanh toán hợp đồng",
};

export function TransactionForm({ onCreated }: { onCreated: (value: Transaction) => void }) {
  const { request } = useAuth();
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault(); setError(""); setSubmitting(true);
    try {
      const transaction = await request<Transaction>("/transactions", {
        method: "POST",
        body: JSON.stringify({ ...form, amount_vnd: Number(form.amount_vnd) }),
      });
      onCreated(transaction);
    } catch (failure) {
      setError(failure instanceof ApiError ? failure.message : "Không thể tạo giao dịch");
    } finally { setSubmitting(false); }
  };

  return (
    <form className="transfer-form" onSubmit={submit}>
      <div className="form-section-title"><span>01</span><div><b>Thông tin chuyển khoản</b><small>Dữ liệu sẽ được lưu vào SQLite</small></div></div>
      <div className="form-grid two-columns">
        <label>Tài khoản nguồn<input required pattern="[0-9]{10,20}" value={form.source_account} onChange={(event) => setForm({ ...form, source_account: event.target.value })} /></label>
        <label>Tài khoản nhận<input required pattern="[0-9]{10,20}" value={form.destination_account} onChange={(event) => setForm({ ...form, destination_account: event.target.value })} /></label>
        <label>Người thụ hưởng<input required minLength={2} value={form.beneficiary_name} onChange={(event) => setForm({ ...form, beneficiary_name: event.target.value })} /></label>
        <label>Số tiền (VND)<input required type="number" min="1" max="10000000000" value={form.amount_vnd} onChange={(event) => setForm({ ...form, amount_vnd: event.target.value })} /></label>
        <label className="full-field">Nội dung<input required minLength={3} value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} /></label>
      </div>
      {error && <div className="inline-alert error">{error}</div>}
      <button className="button primary" disabled={submitting}>{submitting ? "Đang tạo…" : "Tạo yêu cầu chuyển khoản"}<span>→</span></button>
    </form>
  );
}
