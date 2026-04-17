"""CSV reporting utilities for BrowserBench."""

from __future__ import annotations

import csv
from pathlib import Path
from statistics import mean, median, stdev

from .config import IORREG_COLUMNS, POWERMETRICS_COLUMNS


def detect_report_format(file_name: str | Path) -> str:
    path = Path(file_name)
    with path.open(newline="", encoding="utf-8") as file_handle:
        reader = csv.DictReader(file_handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file {path} has no header row")
        columns = set(reader.fieldnames)
    if set(IORREG_COLUMNS).issubset(columns):
        return "ioreg"
    if set(POWERMETRICS_COLUMNS).issubset(columns):
        return "powermetrics"
    raise ValueError(f"Unrecognized BrowserBench CSV schema in {path}")


def _load_rows(file_name: Path) -> list[dict[str, str]]:
    with file_name.open(newline="", encoding="utf-8") as file_handle:
        rows = list(csv.DictReader(file_handle))
    if not rows:
        raise ValueError(f"No data found in {file_name}")
    return rows


def _group_numeric(rows: list[dict[str, str]], field: str) -> dict[str, list[float]]:
    grouped: dict[str, list[float]] = {}
    for row in rows:
        browser = row["Browser"]
        grouped.setdefault(browser, []).append(float(row[field]))
    return grouped


def _summarize(values: list[float]) -> dict[str, float]:
    return {
        "mean": mean(values),
        "median": median(values),
        "min": min(values),
        "max": max(values),
        "stddev": stdev(values) if len(values) > 1 else 0.0,
    }


def _report_ioreg(file_name: Path) -> int:
    rows = _load_rows(file_name)
    grouped = _group_numeric(rows, "Net Browser Power(mW)")
    summary = {browser: _summarize(values) for browser, values in grouped.items()}

    print("BrowserBench Report (ioreg)")
    print("=" * 50)
    print(f"Measurements: {len(rows)}")
    print(f"Browsers tested: {', '.join(summary.keys())}")
    print(
        "Snapshot scope: latest run for browsers tested most recently, with prior rows retained for browsers not re-run."
    )
    print()
    print(
        "| Browser | Net Mean Power (mW) | Net Median Power (mW) | Net Min Power (mW) | Net Max Power (mW) | Std Dev (mW) | Measurements |"
    )
    print(
        "|---------|---------------------|-----------------------|--------------------|--------------------|--------------|--------------|"
    )

    for browser, stats in summary.items():
        count = len(grouped[browser])
        print(
            f"| {browser} | {stats['mean']:.2f} | {stats['median']:.2f} | {stats['min']:.0f} | {stats['max']:.0f} | {stats['stddev']:.2f} | {count} |"
        )

    if len(summary) > 1:
        most_efficient = min(summary, key=lambda name: summary[name]["mean"])
        least_efficient = max(summary, key=lambda name: summary[name]["mean"])
        efficiency_diff = summary[least_efficient]["mean"] - summary[most_efficient]["mean"]
        denom = summary[least_efficient]["mean"]
        efficiency_percent = (efficiency_diff / denom) * 100 if denom > 0 else 0

        print()
        print("Efficiency Analysis")
        print(
            f"Most efficient: {most_efficient} ({summary[most_efficient]['mean']:.0f} mW net avg)"
        )
        print(
            f"Least efficient: {least_efficient} ({summary[least_efficient]['mean']:.0f} mW net avg)"
        )
        print(
            f"Efficiency difference: {efficiency_diff:.0f} mW ({efficiency_percent:.1f}% improvement)"
        )

    return 0


def _report_powermetrics(file_name: Path) -> int:
    rows = _load_rows(file_name)
    grouped = _group_numeric(rows, "Power(mW)")
    summary = {browser: _summarize(values) for browser, values in grouped.items()}

    print("BrowserBench Report (powermetrics)")
    print("=" * 50)
    print(f"Measurements: {len(rows)}")
    print(f"Browsers tested: {', '.join(summary.keys())}")
    print()

    for browser, stats in summary.items():
        print(
            f"{browser}: mean={stats['mean']:.2f} mW, median={stats['median']:.2f} mW, min={stats['min']:.0f} mW, max={stats['max']:.0f} mW, std={stats['stddev']:.2f} mW"
        )
    return 0


def generate_report(file_name: str | Path) -> int:
    path = Path(file_name)
    if not path.exists():
        print(f"Error: {path} not found.")
        return 1

    try:
        report_format = detect_report_format(path)
        if report_format == "ioreg":
            return _report_ioreg(path)
        return _report_powermetrics(path)
    except ValueError as exc:
        print(exc)
        return 1
