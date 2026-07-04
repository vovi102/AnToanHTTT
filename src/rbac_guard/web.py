"""Optional Streamlit adapter for the shared analysis service."""

import json
from pathlib import Path
import tempfile
from typing import Any, Iterable

import pandas as pd
import streamlit as st

from rbac_guard.service import analyze


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


def main() -> None:
    st.set_page_config(page_title="RBAC Guard", layout="wide")
    st.title("RBAC Guard – Security Log Analysis")
    uploaded = st.file_uploader("Log CSV/JSON", type=["csv", "json"])
    db_path = Path(st.text_input("SQLite RBAC database", "demo.db"))
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
