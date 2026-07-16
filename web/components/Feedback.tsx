import type { FeedbackState } from "../lib/types";

export function Feedback({ value, onClose }: { value: FeedbackState | null; onClose?: () => void }) {
  if (!value) return null;
  return (
    <section className={`feedback feedback-${value.kind}`} role="status">
      <div>
        <strong>{value.title}</strong>
        <p>{value.message}</p>
      </div>
      {onClose && <button type="button" onClick={onClose} aria-label="Đóng thông báo">×</button>}
    </section>
  );
}
