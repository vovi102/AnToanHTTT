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


def main() -> None:
    st.set_page_config(page_title="RBAC Guard", layout="wide")
    st.title("RBAC Guard – Security Log Analysis")
    uploaded = st.file_uploader("Log CSV/JSON", type=["csv", "json"])
    db_path = Path(st.text_input("SQLite RBAC database", "demo.db"))
    config_path = Path(st.text_input("Configuration", "config/default.toml"))

    if st.button("Analyze", type="primary", disabled=uploaded is None):
        try:
            assert uploaded is not None
            with tempfile.TemporaryDirectory() as temporary:
                temporary_path = Path(temporary)
                log_path = temporary_path / uploaded.name
                log_path.write_bytes(uploaded.getvalue())
                output_dir = temporary_path / "artifacts"
                result = analyze(db_path, log_path, config_path, output_dir)
                st.session_state["alerts"] = json.loads(
                    (output_dir / "alerts.json").read_text(encoding="utf-8")
                )
                st.session_state["alerts_csv"] = (output_dir / "alerts.csv").read_bytes()
                st.session_state["alerts_json"] = (output_dir / "alerts.json").read_bytes()
                st.success(
                    f"{result.metadata.valid_rows} valid events; "
                    f"{result.metadata.alert_count} alerts"
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


if __name__ == "__main__":
    main()
