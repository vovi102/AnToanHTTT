from pathlib import Path

import pytest

from rbac_guard.config import load_config


def test_load_config_rejects_overlapping_severity_thresholds(tmp_path: Path) -> None:
    path = tmp_path / "bad.toml"
    path.write_text(
        "[password_guessing]\n"
        "failures = 5\n"
        "window_seconds = 300\n"
        "[severity]\n"
        "medium = 40\n"
        "high = 30\n"
        "critical = 80\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="medium < high < critical"):
        load_config(path)


def test_load_default_config() -> None:
    config = load_config(Path("config/default.toml"))

    assert config.password_failures == 5
    assert config.password_window_seconds == 300
    assert (config.medium, config.high, config.critical) == (30, 60, 85)
    assert config.context_enabled is False
    assert (config.business_start_hour, config.business_end_hour) == (8, 18)
    assert config.context_window_seconds == 300
    assert config.new_ip_bonus == 10
    assert config.after_hours_bonus == 8
    assert config.rare_resource_bonus == 8
    assert config.repeated_denial_bonus == 12
    assert config.session_chain_bonus == 15


@pytest.mark.parametrize(
    ("failures", "window_seconds", "message"),
    [(1, 300, "failures must be greater than 1"), (5, 0, "window_seconds must be positive")],
)
def test_load_config_rejects_invalid_password_settings(
    tmp_path: Path, failures: int, window_seconds: int, message: str
) -> None:
    path = tmp_path / "bad-password.toml"
    path.write_text(
        "[password_guessing]\n"
        f"failures = {failures}\n"
        f"window_seconds = {window_seconds}\n"
        "[severity]\n"
        "medium = 30\n"
        "high = 60\n"
        "critical = 85\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=message):
        load_config(path)


@pytest.mark.parametrize(
    ("start_hour", "end_hour"),
    [(18, 8), (-1, 18), (8, 24)],
)
def test_load_config_rejects_invalid_business_hours(
    tmp_path: Path, start_hour: int, end_hour: int
) -> None:
    path = tmp_path / "bad-context.toml"
    path.write_text(
        "[password_guessing]\n"
        "failures = 5\n"
        "window_seconds = 300\n"
        "[severity]\n"
        "medium = 30\n"
        "high = 60\n"
        "critical = 85\n"
        "[context]\n"
        "enabled = false\n"
        f"business_start_hour = {start_hour}\n"
        f"business_end_hour = {end_hour}\n"
        "window_seconds = 300\n"
        "new_ip_bonus = 10\n"
        "after_hours_bonus = 8\n"
        "rare_resource_bonus = 8\n"
        "repeated_denial_bonus = 12\n"
        "session_chain_bonus = 15\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="business hours"):
        load_config(path)
