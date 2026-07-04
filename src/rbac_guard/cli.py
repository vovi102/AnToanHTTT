"""Command-line interface for RBAC Guard."""

import argparse
from pathlib import Path
import sqlite3
import sys

from rbac_guard.metrics import evaluate_artifacts
from rbac_guard.parser import InputFileError
from rbac_guard.rbac import RBACRepository
from rbac_guard.service import analyze


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rbac-guard")
    commands = parser.add_subparsers(dest="command", required=True)

    init_db = commands.add_parser("init-db", help="initialize and seed the RBAC database")
    init_db.add_argument("--db", type=Path, required=True)
    init_db.add_argument("--seed", type=Path, required=True)

    check = commands.add_parser("check-access", help="check one RBAC permission")
    check.add_argument("--db", type=Path, required=True)
    check.add_argument("--user", required=True)
    check.add_argument("--resource", required=True)
    check.add_argument("--action", required=True)

    analyze_command = commands.add_parser("analyze", help="analyze a CSV or JSON log")
    analyze_command.add_argument("--db", type=Path, required=True)
    analyze_command.add_argument("--log", type=Path, required=True)
    analyze_command.add_argument("--config", type=Path, required=True)
    analyze_command.add_argument("--output", type=Path, required=True)
    analyze_command.add_argument(
        "--context-risk",
        action="store_true",
        help="enable context-aware risk findings and incident reports",
    )

    evaluate = commands.add_parser("evaluate", help="evaluate alerts against labeled events")
    evaluate.add_argument("--alerts", type=Path, required=True)
    evaluate.add_argument("--events", type=Path, required=True)
    evaluate.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        if arguments.command == "init-db":
            repository = RBACRepository(arguments.db)
            repository.initialize()
            repository.seed(arguments.seed)
            print(f"Initialized RBAC database: {arguments.db}")
        elif arguments.command == "check-access":
            granted = RBACRepository(arguments.db).has_permission(
                arguments.user, arguments.resource, arguments.action
            )
            print("ALLOWED" if granted else "DENIED")
        elif arguments.command == "analyze":
            result = analyze(
                arguments.db,
                arguments.log,
                arguments.config,
                arguments.output,
                context_risk=arguments.context_risk,
            )
            message = (
                f"Analyzed {result.metadata.valid_rows} valid events; "
                f"{result.metadata.invalid_rows} invalid rows; "
                f"{result.metadata.alert_count} alerts"
            )
            if arguments.context_risk:
                message += f"; {len(result.incidents)} incidents"
            print(message)
        elif arguments.command == "evaluate":
            metrics = evaluate_artifacts(arguments.events, arguments.alerts, arguments.output)
            macro = metrics["macro_average"]
            print(
                f"Macro precision={macro['precision']:.4f}; "
                f"recall={macro['recall']:.4f}; f1={macro['f1']:.4f}"
            )
        return 0
    except (FileNotFoundError, InputFileError, KeyError, sqlite3.Error, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
