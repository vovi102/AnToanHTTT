"""Optional Streamlit adapter for the shared analysis service."""

import json
from pathlib import Path
import tempfile
from typing import Any, Iterable

import pandas as pd
import streamlit as st

from rbac_guard.service import analyze
from rbac_guard.rbac import RBACRepository


def permission_label(resource: str, action: str) -> str:
    """Translate demo permissions into actions in the banking application."""
    labels = {
        ("accounts", "read"): "Xem tài khoản khách hàng",
        ("accounts", "update"): "Cập nhật thông tin tài khoản",
        ("users", "delete"): "Xóa tài khoản người dùng",
        ("audit_logs", "read"): "Xem nhật ký kiểm toán",
    }
    return labels.get((resource, action), f"{action} {resource}")


def person_label(username: str) -> str:
    people = {
        "admin01": "Minh — Quản trị viên",
        "teller01": "Lan — Giao dịch viên",
        "auditor01": "Hà — Kiểm toán viên",
        "disabled01": "Nam — Tài khoản đã khóa",
    }
    return people.get(username, username)


def inject_app_style() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #f6f8fc; }
        .block-container { max-width: 1120px; padding-top: 2.2rem; }
        .bank-hero { background: linear-gradient(120deg, #102a43, #176b87); color: white;
          padding: 2rem; border-radius: 20px; margin-bottom: 1.4rem; }
        .bank-hero h1 { margin: 0 0 .4rem; font-size: 2rem; }
        .bank-hero p { margin: 0; font-size: 1.05rem; opacity: .92; }
        .story-card { background: white; border-radius: 16px; padding: 1.25rem;
          border: 1px solid #e4e9f2; min-height: 248px; }
        .story-card h3 { margin-top: 0; }
        .story-card.before { border-top: 5px solid #e85d75; }
        .story-card.after { border-top: 5px solid #27a36a; }
        .flow { font-size: 1.05rem; font-weight: 600; padding: .75rem; margin: .8rem 0;
          border-radius: 10px; background: #f4f7fb; }
        .chip { display: inline-block; background: #e6f6ec; color: #146c43;
          border-radius: 99px; padding: .35rem .65rem; margin: .2rem .15rem .2rem 0; }
        .denied { display: inline-block; background: #fde8e8; color: #ad2431;
          border-radius: 99px; padding: .35rem .65rem; margin-top: .45rem; }
        .persona { background: white; border: 1px solid #e4e9f2; border-radius: 16px;
          padding: 1.25rem; margin-top: .7rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def filter_alert_rows(
    rows: Iterable[dict[str, Any]], risk_types: set[str], severities: set[str]
) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if row["risk_type"] in risk_types and row["severity"] in severities
    ]


def count_alerts(rows: Iterable[dict[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row[field])
        counts[value] = counts.get(value, 0) + 1
    return counts


def filter_incident_rows(
    rows: Iterable[dict[str, Any]],
    users: set[str],
    risk_types: set[str],
    severities: set[str],
    context_signals: set[str],
) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for row in rows:
        row_risks = set(row.get("risk_types", []))
        row_signals = set(row.get("context_signals", []))
        user = str(row.get("user") or "")
        if users and user not in users:
            continue
        if risk_types and not (row_risks & risk_types):
            continue
        if severities and row.get("severity") not in severities:
            continue
        if context_signals and not (row_signals & context_signals):
            continue
        filtered.append(row)
    return filtered


def rbac_graph(rows: Iterable[dict[str, str]]) -> str:
    """Build a Graphviz diagram for one user's RBAC access path."""
    links = list(rows)
    if not links:
        return "digraph RBAC { label=\"No permissions assigned\"; }"
    user = links[0]["username"]
    role_nodes = sorted({row["role"] for row in links})
    permission_nodes = sorted(
        {f'{row["resource"]}:{row["action"]}' for row in links}
    )
    lines = [
        "digraph RBAC {",
        "rankdir=LR; bgcolor=transparent;",
        'node [shape=box style="rounded,filled" fontname="Arial"];',
        f'"user:{user}" [label="User\\n{user}" fillcolor="#DCEEFF"];',
    ]
    for role in role_nodes:
        lines.append(f'"role:{role}" [label="Role\\n{role}" fillcolor="#FFF0C2"];')
        lines.append(f'"user:{user}" -> "role:{role}" [label="assigned"];')
    for permission in permission_nodes:
        resource, action = permission.split(":", maxsplit=1)
        lines.append(
            f'"permission:{permission}" [label="Quyền\\n{permission_label(resource, action)}" '
            'fillcolor="#DDF5E4"];'
        )
    for row in links:
        permission = f'{row["resource"]}:{row["action"]}'
        lines.append(f'"role:{row["role"]}" -> "permission:{permission}" [label="grants"];')
    lines.append("}")
    return "\n".join(lines)


def render_before_after_comparison() -> None:
    """Show the security effect of adding RBAC before a demo database exists."""
    st.markdown("### Vì sao ngân hàng cần RBAC?")
    st.caption("Cùng một thao tác, nhưng hệ thống phải biết người thực hiện là ai.")
    before, after = st.columns(2)
    with before:
        st.markdown(
            """
            <div class="story-card before">
              <h3>❌ Trước khi có RBAC</h3>
              <p>Lan là giao dịch viên, nhưng ứng dụng không kiểm tra chức danh.</p>
              <div class="flow">Lan → Xóa tài khoản người dùng</div>
              <p>Hệ thống chỉ thấy một người đã đăng nhập, nên thao tác nhạy cảm có thể lọt qua.</p>
              <span class="denied">Rủi ro: cho phép sai</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with after:
        st.markdown(
            """
            <div class="story-card after">
              <h3>✓ Sau khi có RBAC</h3>
              <p>Ứng dụng xác định Lan là <b>Giao dịch viên</b> trước khi mở chức năng.</p>
              <div class="flow">Lan → Giao dịch viên → Kiểm tra quyền</div>
              <span class="chip">✓ Xem tài khoản khách hàng</span>
              <span class="chip">✓ Cập nhật thông tin tài khoản</span><br>
              <span class="denied">✕ Xóa tài khoản người dùng: bị chặn</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_rbac_demo(db_path: Path) -> None:
    st.markdown(
        """
        <div class="bank-hero">
          <h1>BankSafe</h1>
          <p>Demo: mỗi nhân viên ngân hàng chỉ thấy các chức năng phù hợp với công việc của mình.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_before_after_comparison()
    st.divider()
    st.markdown("### Hãy thử như một nhân viên ngân hàng")
    st.caption("Chọn nhân viên và chức năng. Kết quả thay đổi ngay lập tức.")
    repository = RBACRepository(db_path)
    if not db_path.exists():
        st.warning("Chưa có dữ liệu nhân viên để thử.")
        if st.button("Tạo dữ liệu demo RBAC", type="primary"):
            repository.initialize()
            repository.seed(Path("data/rbac_seed.json"))
            st.rerun()
        return

    try:
        access_rows = repository.list_access_rows()
    except ValueError as error:
        st.error(f"Không thể đọc cơ sở dữ liệu RBAC: {error}")
        return
    if not access_rows:
        st.warning("Cơ sở dữ liệu chưa có user, role hoặc permission để hiển thị.")
        return

    users = sorted({row["username"] for row in access_rows})
    selected_user = st.selectbox(
        "Bạn đang là nhân viên nào?", users, format_func=person_label, key="rbac_user"
    )
    selected_rows = [row for row in access_rows if row["username"] == selected_user]
    status = selected_rows[0]["status"]
    roles = ", ".join(sorted({row["role"] for row in selected_rows}))
    permissions = sorted({permission_label(row["resource"], row["action"]) for row in selected_rows})

    st.markdown('<div class="persona">', unsafe_allow_html=True)
    status_column, role_column, permission_column = st.columns(3)
    status_column.metric("Trạng thái tài khoản", "Đang hoạt động" if status == "active" else "Đã khóa")
    role_column.metric("Vai trò", roles)
    permission_column.metric("Chức năng được phép", len(permissions))
    st.markdown("<b>Chức năng của bạn:</b><br>" + " ".join(
        f'<span class="chip">{permission}</span>' for permission in permissions
    ) + "</div>", unsafe_allow_html=True)
    if status != "active":
        st.error("Tài khoản bị vô hiệu hóa: mọi yêu cầu truy cập đều bị từ chối.")
    st.markdown("#### Thử mở một chức năng")
    permission_options = sorted(
        {(row["resource"], row["action"]) for row in access_rows},
        key=lambda item: permission_label(*item),
    )
    selected_permission = st.selectbox(
        "Chức năng muốn thực hiện",
        permission_options,
        format_func=lambda item: permission_label(*item),
        key="rbac_permission",
    )
    resource, action = selected_permission
    if repository.has_permission(selected_user, resource, action):
        st.success(f"Được phép — {person_label(selected_user)} có thể: {permission_label(resource, action)}.")
    else:
        st.error(f"Bị chặn — {person_label(selected_user)} không thể: {permission_label(resource, action)}.")


def main() -> None:
    st.set_page_config(page_title="RBAC Guard", layout="wide")
    inject_app_style()
    db_path = Path(st.text_input("SQLite RBAC database", "demo.db"))
    render_rbac_demo(db_path)
    st.divider()
    st.header("Phân tích nhật ký bảo mật")
    uploaded = st.file_uploader("Log CSV/JSON", type=["csv", "json"])
    config_path = Path(st.text_input("Configuration", "config/default.toml"))
    context_risk = st.checkbox("Context-aware risk analysis")

    if st.button("Analyze", type="primary", disabled=uploaded is None):
        try:
            assert uploaded is not None
            with tempfile.TemporaryDirectory() as temporary:
                temporary_path = Path(temporary)
                log_path = temporary_path / uploaded.name
                log_path.write_bytes(uploaded.getvalue())
                output_dir = temporary_path / "artifacts"
                result = analyze(
                    db_path, log_path, config_path, output_dir, context_risk=context_risk
                )
                st.session_state["alerts"] = json.loads(
                    (output_dir / "alerts.json").read_text(encoding="utf-8")
                )
                st.session_state["incidents"] = (
                    json.loads((output_dir / "incidents.json").read_text(encoding="utf-8"))
                    if (output_dir / "incidents.json").exists()
                    else []
                )
                st.session_state["alerts_csv"] = (output_dir / "alerts.csv").read_bytes()
                st.session_state["alerts_json"] = (output_dir / "alerts.json").read_bytes()
                if (output_dir / "incidents.csv").exists():
                    st.session_state["incidents_csv"] = (
                        output_dir / "incidents.csv"
                    ).read_bytes()
                    st.session_state["incidents_json"] = (
                        output_dir / "incidents.json"
                    ).read_bytes()
                st.success(
                    f"{result.metadata.valid_rows} valid events; "
                    f"{result.metadata.alert_count} alerts; "
                    f"{len(result.incidents)} incidents"
                )
        except (AssertionError, FileNotFoundError, KeyError, ValueError) as error:
            st.error(str(error) or "No input file was provided")

    rows = st.session_state.get("alerts", [])
    if not rows:
        st.info("Run an analysis to display alerts.")
        return

    risk_options = sorted({row["risk_type"] for row in rows})
    severity_options = sorted({row["severity"] for row in rows})
    selected_risks = set(st.multiselect("Risk type", risk_options, default=risk_options))
    selected_severities = set(
        st.multiselect("Severity", severity_options, default=severity_options)
    )
    filtered = filter_alert_rows(rows, selected_risks, selected_severities)
    st.dataframe(pd.DataFrame(filtered), use_container_width=True, hide_index=True)

    left, right = st.columns(2)
    left.subheader("Alerts by risk type")
    left.bar_chart(pd.Series(count_alerts(filtered, "risk_type")))
    right.subheader("Alerts by severity")
    right.bar_chart(pd.Series(count_alerts(filtered, "severity")))

    st.download_button("Download CSV", st.session_state["alerts_csv"], "alerts.csv")
    st.download_button(
        "Download JSON", st.session_state["alerts_json"], "alerts.json", "application/json"
    )

    incidents = st.session_state.get("incidents", [])
    if incidents:
        st.subheader("Incidents")
        user_options = sorted({str(row.get("user") or "") for row in incidents})
        incident_risk_options = sorted(
            {risk for row in incidents for risk in row.get("risk_types", [])}
        )
        incident_severity_options = sorted({row["severity"] for row in incidents})
        signal_options = sorted(
            {signal for row in incidents for signal in row.get("context_signals", [])}
        )
        selected_users = set(st.multiselect("Incident user", user_options, default=user_options))
        selected_incident_risks = set(
            st.multiselect(
                "Incident risk type",
                incident_risk_options,
                default=incident_risk_options,
            )
        )
        selected_incident_severities = set(
            st.multiselect(
                "Incident severity",
                incident_severity_options,
                default=incident_severity_options,
            )
        )
        selected_signals = set(
            st.multiselect("Context signal", signal_options, default=signal_options)
        )
        filtered_incidents = filter_incident_rows(
            incidents,
            selected_users,
            selected_incident_risks,
            selected_incident_severities,
            selected_signals,
        )
        st.dataframe(pd.DataFrame(filtered_incidents), use_container_width=True, hide_index=True)
        st.download_button(
            "Download Incidents CSV",
            st.session_state["incidents_csv"],
            "incidents.csv",
        )
        st.download_button(
            "Download Incidents JSON",
            st.session_state["incidents_json"],
            "incidents.json",
            "application/json",
        )


if __name__ == "__main__":
    main()
