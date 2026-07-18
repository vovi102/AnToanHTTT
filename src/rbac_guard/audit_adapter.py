"""Export Nova Bank audit records into the normalized Event contract."""

import csv
from pathlib import Path

from rbac_guard.parser import REQUIRED_FIELDS
from rbac_guard.rbac import RBACRepository


def export_audit_events(
    db_path: Path, output_path: Path, source_ip: str = "nova-bank-local"
) -> int:
    """Write all Nova Bank audit records as chronological CSV security events."""
    records = RBACRepository(db_path).audit_log_records()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted(REQUIRED_FIELDS)
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for record in records:
            is_login = record["resource"] == "session" and record["action"] == "login"
            details = (
                f"role={record['role_at_event'] or ''}; outcome={record['outcome']}; "
                f"transaction_reference={record['transaction_reference'] or ''}; "
                f"detail={record['detail']}"
            )
            writer.writerow(
                {
                    "event_id": f"nova-audit-{record['id']}",
                    "timestamp": record["created_at"],
                    "event_type": "authentication" if is_login else "authorization",
                    "user": record["username"] or "",
                    "ip": source_ip,
                    "resource": record["resource"],
                    "action": record["action"],
                    "status": record["outcome"],
                    "request": record["detail"],
                    "details": details,
                    "expected_label": "",
                }
            )
    return len(records)
