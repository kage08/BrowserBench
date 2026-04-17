"""Shared helpers for CLI commands."""

from __future__ import annotations

import csv
from pathlib import Path

from .config import BROWSERS


def parse_browser_selection(browser_option: str | None) -> list[str]:
    if not browser_option or browser_option.lower() == "all":
        return list(BROWSERS.keys())

    selected: list[str] = []
    for browser_key in browser_option.split(","):
        key = browser_key.strip().lower()
        if key not in BROWSERS:
            valid = ", ".join(BROWSERS.keys())
            raise ValueError(
                f"Unsupported browser '{browser_key}'. Valid options: {valid}"
            )
        selected.append(key)

    return list(dict.fromkeys(selected))


def get_browser_info(browser_key: str) -> dict[str, str]:
    return BROWSERS[browser_key]


def load_sites(sites_file: str | Path) -> list[str]:
    path = Path(sites_file)
    with path.open("r", encoding="utf-8") as file_handle:
        return [line.strip() for line in file_handle if line.strip()]


def ensure_results_file_for_selected_browsers(
    output_file: str | Path,
    result_columns: list[str],
    selected_browsers: list[str],
) -> None:
    output_path = Path(output_file)
    selected_display_names = {
        get_browser_info(browser_key)["display_name"]
        for browser_key in selected_browsers
    }

    if not output_path.exists():
        with output_path.open("w", newline="", encoding="utf-8") as file_handle:
            writer = csv.DictWriter(file_handle, fieldnames=result_columns)
            writer.writeheader()
        return

    try:
        with output_path.open(newline="", encoding="utf-8") as file_handle:
            reader = csv.DictReader(file_handle)
            if reader.fieldnames is None or any(
                column not in reader.fieldnames for column in result_columns
            ):
                raise ValueError("Unexpected CSV header format")
            rows = list(reader)
    except (OSError, csv.Error, ValueError) as exc:
        print(f"Warning: resetting {output_path} due to read error: {exc}")
        with output_path.open("w", newline="", encoding="utf-8") as file_handle:
            writer = csv.DictWriter(file_handle, fieldnames=result_columns)
            writer.writeheader()
        return

    filtered_rows = [
        row for row in rows if row.get("Browser", "") not in selected_display_names
    ]
    replaced_rows = len(rows) - len(filtered_rows)

    with output_path.open("w", newline="", encoding="utf-8") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=result_columns)
        writer.writeheader()
        writer.writerows(filtered_rows)

    if replaced_rows > 0:
        print(
            f"Replaced {replaced_rows} previous measurements for selected browsers in {output_path}."
        )
    else:
        print(f"No previous measurements found for selected browsers in {output_path}.")

