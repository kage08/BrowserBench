"""BrowserBench CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from .benchmark_ioreg import run_benchmark as run_ioreg_benchmark
from .benchmark_powermetrics import run_benchmark as run_powermetrics_benchmark
from .common import parse_browser_selection
from .config import (
    BROWSERS,
    DEFAULT_BASELINE_DURATION_SEC,
    DEFAULT_IORERG_DURATION_SEC,
    DEFAULT_POWERMETRICS_DURATION_SEC,
    default_sites_path,
)
from .doctor import run_doctor
from .prep import run_prep
from .reporting import generate_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="browserbench",
        description="Measure and compare browser power usage on macOS.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prep_parser = subparsers.add_parser(
        "prep", help="Standardize the macOS environment before benchmarking."
    )
    prep_parser.set_defaults(handler=handle_prep)

    doctor_parser = subparsers.add_parser(
        "doctor", help="Run preflight checks without starting a benchmark."
    )
    doctor_parser.add_argument(
        "--browsers",
        default="all",
        help=f"Comma-separated browser keys. Available: {', '.join(BROWSERS.keys())}",
    )
    doctor_parser.add_argument(
        "--sites-file",
        default=str(default_sites_path()),
        help="Path to the sites file used for benchmark tab loading.",
    )
    doctor_parser.add_argument(
        "--allow-plugged-in",
        action="store_true",
        help="Do not fail if the MacBook is plugged in.",
    )
    doctor_parser.set_defaults(handler=handle_doctor)

    browsers_parser = subparsers.add_parser(
        "browsers", help="List available browser keys."
    )
    browsers_parser.set_defaults(handler=handle_browsers)

    run_parser = subparsers.add_parser(
        "run", help="Run the default ioreg-based browser power benchmark."
    )
    run_parser.add_argument(
        "--browsers",
        default="all",
        help=f"Comma-separated browser keys. Available: {', '.join(BROWSERS.keys())}",
    )
    run_parser.add_argument(
        "--duration",
        type=int,
        default=DEFAULT_IORERG_DURATION_SEC,
        help=f"Duration in seconds for each browser test (default: {DEFAULT_IORERG_DURATION_SEC}).",
    )
    run_parser.add_argument(
        "--baseline-duration",
        type=int,
        default=DEFAULT_BASELINE_DURATION_SEC,
        help=f"Idle baseline duration in seconds (default: {DEFAULT_BASELINE_DURATION_SEC}).",
    )
    run_parser.add_argument(
        "--sites-file",
        default=str(default_sites_path()),
        help="Path to the file containing one URL per line.",
    )
    run_parser.add_argument(
        "--output",
        default="browser_power_results2.csv",
        help="CSV path for benchmark results.",
    )
    run_parser.set_defaults(handler=handle_run)

    power_parser = subparsers.add_parser(
        "run-powermetrics",
        help="Run the legacy powermetrics-based benchmark (requires sudo).",
    )
    power_parser.add_argument(
        "--browsers",
        default="all",
        help=f"Comma-separated browser keys. Available: {', '.join(BROWSERS.keys())}",
    )
    power_parser.add_argument(
        "--duration",
        type=int,
        default=DEFAULT_POWERMETRICS_DURATION_SEC,
        help=f"Duration in seconds for each browser test (default: {DEFAULT_POWERMETRICS_DURATION_SEC}).",
    )
    power_parser.add_argument(
        "--sites-file",
        default=str(default_sites_path()),
        help="Path to the file containing one URL per line.",
    )
    power_parser.add_argument(
        "--output",
        default="browser_power_results.csv",
        help="CSV path for powermetrics results.",
    )
    power_parser.set_defaults(handler=handle_run_powermetrics)

    report_parser = subparsers.add_parser(
        "report", help="Generate a report from a BrowserBench CSV file."
    )
    report_parser.add_argument(
        "csv_file",
        nargs="?",
        default="browser_power_results2.csv",
        help="CSV file to analyze. Defaults to the ioreg workflow output.",
    )
    report_parser.set_defaults(handler=handle_report)

    return parser


def handle_prep(args: argparse.Namespace) -> int:
    del args
    run_prep()
    return 0


def handle_doctor(args: argparse.Namespace) -> int:
    selected_browsers = parse_browser_selection(args.browsers)
    success = run_doctor(
        BROWSERS,
        selected_browsers,
        args.sites_file,
        require_battery=not args.allow_plugged_in,
    )
    return 0 if success else 1


def handle_browsers(args: argparse.Namespace) -> int:
    del args
    print("Available browsers:")
    for key, data in BROWSERS.items():
        print(f"  {key}: {data['display_name']}")
    return 0


def handle_run(args: argparse.Namespace) -> int:
    selected_browsers = parse_browser_selection(args.browsers)
    return run_ioreg_benchmark(
        selected_browsers=selected_browsers,
        sites_file=Path(args.sites_file),
        output_file=Path(args.output),
        duration_sec=args.duration,
        baseline_duration_sec=args.baseline_duration,
    )


def handle_run_powermetrics(args: argparse.Namespace) -> int:
    selected_browsers = parse_browser_selection(args.browsers)
    return run_powermetrics_benchmark(
        selected_browsers=selected_browsers,
        sites_file=Path(args.sites_file),
        output_file=Path(args.output),
        duration_sec=args.duration,
    )


def handle_report(args: argparse.Namespace) -> int:
    return generate_report(Path(args.csv_file))


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
