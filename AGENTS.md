# AI Agent Guide for BrowserBench

This repository is designed to measure and compare real-world power consumption of web browsers on macOS. This guide helps AI agents understand the codebase, environment requirements, and common workflows.

## 🚀 Environment & Tooling

- **Python & Dependency Management**: This repo uses [uv](https://github.com/astral-sh/uv) for package and environment management.
    - Run scripts using `uv run <scriptname>.py`.
- **Hardware Requirement**: For accurate power measurement with `ioreg`, the MacBook **must be unplugged** from power.
- **Privileges**: Running `powermetrics` (used in `browser_bench.py`) requires `sudo`.
- **Environment Standardization**: Before running benchmarks, use `standardize_env.py` to set screen brightness and disable conflicting features like Auto-Brightness.

## 📂 Core Scripts

| Script | Purpose | Key Details |
| :--- | :--- | :--- |
| `standardize_env.py` | Prep the system | Sets brightness, prompts for Focus Mode, etc. |
| `browser_bench2.py` | Main Benchmark (ioreg) | Uses `ioreg` for voltage/amperage monitoring. |
| `browser_bench.py` | Benchmark (powermetrics) | Uses `powermetrics` (requires sudo). |
| `report.py` | Result Analysis (v1) | Processes `browser_power_results.csv` into statistics and estimates. |
| `report2.py` | Result Analysis (v2) | Processes `browser_power_results2.csv` from `browser_bench2.py`. |

## 🔄 Data Flow

1.  **Input**: `sites.txt` contains the list of URLs to be tested.
2.  **Execution**: `browser_bench2.py` opens tabs, rotates [AppleScript patterns](#automation-mechanics), and logs power data.
3.  **Output**: Data is logged to `browser_power_results2.csv` (for `v2`) or `browser_power_results.csv` (for `v1`).
4.  **Reporting**: `report.py` analyzes the CSV and outputs a summary.

## 🤖 Automation Mechanics

Browsers are controlled via **AppleScript** (using `osascript`).
- **Behaviors**: Defined in `get_browsing_behavior()` in `browser_bench2.py`.
- **Patterns**: Includes `quick_scan`, `detailed_read`, `search_mode`, `link_navigation`, `reload_page`, and `zoom_adjust`.
- **Tab Switching**: Uses Cmd+Number shortcuts to cycle through tabs.

## 🛠 Common Tasks for Agents

### Adding a New Browser
1.  Update the `BROWSERS` dictionary in `browser_bench2.py` (and `browser_bench.py`).
2.  Key info needed: `app_name` (for `open -a`) and `process_name` (for AppleScript `tell process`).
3.  Verify tab switching works with Cmd+Number for that browser.

### Running a Focused Test
```bash
# Example: Test only Chrome and Safari for 5 minutes
uv run browser_bench2.py --browsers chrome,safari --duration 300
```

## ⚠️ Important Considerations
- **Baseline Measurement**: Both benchmark scripts include a period of idle measurement to establish a baseline. Do not interact with the machine during this time.
- **Sleep Prevention**: The scripts use `caffeinate` to prevent the system from sleeping during tests.
