"""CSV reporting utilities for BrowserBench."""

from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path
from statistics import mean, median, stdev

from .config import IORREG_REQUIRED_COLUMNS, POWERMETRICS_COLUMNS


def detect_report_format(file_name: str | Path) -> str:
    path = Path(file_name)
    with path.open(newline="", encoding="utf-8") as file_handle:
        reader = csv.DictReader(file_handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file {path} has no header row")
        columns = set(reader.fieldnames)
    if set(IORREG_REQUIRED_COLUMNS).issubset(columns):
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


def _select_latest_ioreg_run(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], str | None]:
    if not rows or "Run ID" not in rows[0]:
        return rows, None

    run_ids = [row.get("Run ID", "").strip() for row in rows if row.get("Run ID", "").strip()]
    if not run_ids:
        return rows, None

    latest_run_id = run_ids[-1]
    filtered_rows = [row for row in rows if row.get("Run ID", "").strip() == latest_run_id]
    return filtered_rows, latest_run_id


def _browser_display_order(
    rows: list[dict[str, str]], grouped: dict[str, list[float]]
) -> list[str]:
    if not rows:
        return list(grouped.keys())

    if "Browser Order" in rows[0]:
        order_pairs: list[tuple[int, str]] = []
        seen: set[str] = set()
        for row in rows:
            browser = row["Browser"]
            if browser in seen:
                continue
            raw_order = row.get("Browser Order", "").strip()
            try:
                order_pairs.append((int(raw_order), browser))
                seen.add(browser)
            except ValueError:
                continue
        if order_pairs:
            ordered = [browser for _, browser in sorted(order_pairs)]
            for browser in grouped:
                if browser not in ordered:
                    ordered.append(browser)
            return ordered

    ordered: list[str] = []
    for row in rows:
        browser = row["Browser"]
        if browser not in ordered:
            ordered.append(browser)
    for browser in grouped:
        if browser not in ordered:
            ordered.append(browser)
    return ordered


def _summarize(values: list[float]) -> dict[str, float]:
    return {
        "mean": mean(values),
        "median": median(values),
        "min": min(values),
        "max": max(values),
        "stddev": stdev(values) if len(values) > 1 else 0.0,
    }


def _read_battery_energy_wh() -> float | None:
    try:
        result = subprocess.run(
            ["ioreg", "-r", "-n", "AppleSmartBattery"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None

    output = result.stdout
    capacity_match = re.search(r'"AppleRawMaxCapacity"\s*=\s*(\d+)', output)
    if capacity_match is None:
        capacity_match = re.search(r'"DesignCapacity"\s*=\s*(\d+)', output)

    voltage_match = re.search(r'"AppleRawBatteryVoltage"\s*=\s*(\d+)', output)
    if voltage_match is None:
        voltage_match = re.search(r'"Voltage"\s*=\s*(\d+)', output)

    if capacity_match is None or voltage_match is None:
        return None

    capacity_mah = float(capacity_match.group(1))
    voltage_mv = float(voltage_match.group(1))
    return (capacity_mah * voltage_mv) / 1_000_000


def _estimate_battery_hours(battery_energy_wh: float, power_mw: float) -> float | None:
    if power_mw <= 0:
        return None
    return battery_energy_wh / (power_mw / 1000.0)


def _format_hours(hours: float | None) -> str:
    if hours is None:
        return "n/a"
    return f"{hours:.2f}"


def _report_ioreg(file_name: Path) -> int:
    all_rows = _load_rows(file_name)
    rows, latest_run_id = _select_latest_ioreg_run(all_rows)
    net_grouped = _group_numeric(rows, "Net Browser Power(mW)")
    total_grouped = _group_numeric(rows, "Total Power(mW)")
    summary = {browser: _summarize(values) for browser, values in net_grouped.items()}
    total_summary = {browser: _summarize(values) for browser, values in total_grouped.items()}
    baseline_field = (
        "Matched Idle Baseline(mW)"
        if rows and "Matched Idle Baseline(mW)" in rows[0]
        else "Idle Baseline(mW)"
    )
    baseline_grouped = _group_numeric(rows, baseline_field)
    baseline_summary = {
        browser: _summarize(values) for browser, values in baseline_grouped.items()
    }
    battery_energy_wh = _read_battery_energy_wh()
    browser_order = _browser_display_order(rows, total_grouped)

    print("BrowserBench Report (ioreg)")
    print("=" * 50)
    print(f"Measurements: {len(rows)}")
    print(f"Browsers tested: {', '.join(browser_order)}")
    if latest_run_id is not None:
        print(f"Run ID: {latest_run_id}")
        if len({row.get('Run ID', '').strip() for row in all_rows if row.get('Run ID', '').strip()}) > 1:
            print("Scope: only the latest ioreg run is reported to avoid cross-run comparisons.")
    print()
    print(
        "| Browser | Total Mean Power (mW) | Total Median Power (mW) | Matched Idle Mean (mW) | Net Mean Power (mW) | Net Median Power (mW) | Std Dev (mW) | Measurements | Est. Battery Hours (Mean Total) | Est. Battery Hours (Median Total) |"
    )
    print(
        "|---------|-----------------------|-------------------------|------------------------|---------------------|-----------------------|--------------|--------------|----------------------------------|------------------------------------|"
    )

    for browser in browser_order:
        stats = summary[browser]
        count = len(net_grouped[browser])
        total_stats = total_summary[browser]
        matched_baseline_stats = baseline_summary[browser]
        mean_hours = _estimate_battery_hours(battery_energy_wh, total_stats["mean"]) if battery_energy_wh else None
        median_hours = (
            _estimate_battery_hours(battery_energy_wh, total_stats["median"])
            if battery_energy_wh
            else None
        )
        print(
            f"| {browser} | {total_stats['mean']:.2f} | {total_stats['median']:.2f} | {matched_baseline_stats['mean']:.2f} | {stats['mean']:.2f} | {stats['median']:.2f} | {stats['stddev']:.2f} | {count} | {_format_hours(mean_hours)} | {_format_hours(median_hours)} |"
        )

    if battery_energy_wh is not None:
        print()
        print(f"Estimated full-charge battery energy used for runtime estimates: {battery_energy_wh:.2f} Wh")
        print("Battery-life estimates use total system power during each browser run, not net browser-only power.")

    if len(summary) > 1:
        most_efficient = min(total_summary, key=lambda name: total_summary[name]["mean"])
        least_efficient = max(total_summary, key=lambda name: total_summary[name]["mean"])
        efficiency_diff = total_summary[least_efficient]["mean"] - total_summary[most_efficient]["mean"]
        denom = total_summary[least_efficient]["mean"]
        efficiency_percent = (efficiency_diff / denom) * 100 if denom > 0 else 0

        print()
        print("Efficiency Analysis")
        print(
            f"Most efficient: {most_efficient} ({total_summary[most_efficient]['mean']:.0f} mW total avg)"
        )
        print(
            f"Least efficient: {least_efficient} ({total_summary[least_efficient]['mean']:.0f} mW total avg)"
        )
        print(
            f"Efficiency difference: {efficiency_diff:.0f} mW ({efficiency_percent:.1f}% improvement)"
        )

    return 0


def _report_powermetrics(file_name: Path) -> int:
    rows = _load_rows(file_name)
    grouped = _group_numeric(rows, "Power(mW)")
    summary = {browser: _summarize(values) for browser, values in grouped.items()}
    battery_energy_wh = _read_battery_energy_wh()

    print("BrowserBench Report (powermetrics)")
    print("=" * 50)
    print(f"Measurements: {len(rows)}")
    print(f"Browsers tested: {', '.join(summary.keys())}")
    print()

    for browser, stats in summary.items():
        mean_hours = _estimate_battery_hours(battery_energy_wh, stats["mean"]) if battery_energy_wh else None
        median_hours = _estimate_battery_hours(battery_energy_wh, stats["median"]) if battery_energy_wh else None
        print(
            f"{browser}: mean={stats['mean']:.2f} mW, median={stats['median']:.2f} mW, min={stats['min']:.0f} mW, max={stats['max']:.0f} mW, std={stats['stddev']:.2f} mW, est_hours_mean={_format_hours(mean_hours)}, est_hours_median={_format_hours(median_hours)}"
        )

    if battery_energy_wh is not None:
        print()
        print(f"Estimated full-charge battery energy used for runtime estimates: {battery_energy_wh:.2f} Wh")
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
