"""Shared configuration and browser registry for BrowserBench."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

BROWSERS: dict[str, dict[str, str]] = {
    "safari": {
        "display_name": "Safari",
        "app_name": "Safari",
        "process_name": "Safari",
    },
    "brave": {
        "display_name": "Brave",
        "app_name": "Brave Browser",
        "process_name": "Brave Browser",
    },
    "chrome": {
        "display_name": "Chrome",
        "app_name": "Google Chrome",
        "process_name": "Google Chrome",
    },
    "firefox": {
        "display_name": "Firefox",
        "app_name": "Firefox",
        "process_name": "firefox",
    },
    "edge": {
        "display_name": "Edge",
        "app_name": "Microsoft Edge",
        "process_name": "Microsoft Edge",
    },
    "comet": {
        "display_name": "Comet",
        "app_name": "Comet",
        "process_name": "Comet",
    },
    "atlas": {
        "display_name": "ChatGPT Atlas",
        "app_name": "ChatGPT Atlas",
        "process_name": "ChatGPT Atlas",
    },
    "zen": {
        "display_name": "Zen",
        "app_name": "Zen",
        "process_name": "zen",
    },
}

DEFAULT_IORERG_DURATION_SEC = 1200
DEFAULT_BASELINE_DURATION_SEC = 60
DEFAULT_POWERMETRICS_DURATION_SEC = 1200

IORREG_COLUMNS = [
    "Browser",
    "Timestamp",
    "Total Power(mW)",
    "Idle Baseline(mW)",
    "Net Browser Power(mW)",
]

POWERMETRICS_COLUMNS = ["Browser", "Timestamp", "Power(mW)"]


def default_sites_path() -> Path:
    return Path(files("browserbench.resources").joinpath("sites.txt"))

