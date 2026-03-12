# Browser Power Benchmark

A comprehensive tool to measure and compare real-world power consumption of different web browsers on macOS using advanced browsing simulation patterns.

## Overview

This benchmark simulates realistic browsing behavior (tab switching, scrolling, searching, page reloading) while measuring power via two workflows:
- `browser_bench2.py` (recommended): `ioreg`-based total system drain with idle-baseline subtraction
- `browser_bench.py`: `powermetrics`-based CPU/GPU/ANE power sampling
The tool provides statistical analysis to compare browser efficiency and real-world battery life impact.

## Features

- **🤖 Advanced browser automation** using AppleScript with 6 different browsing patterns
- **🧭 Selective browser testing** via CLI (`--browsers`) for Chrome/Firefox/Edge/Safari/Brave/Comet
- **⚡ Dual measurement workflows** (`ioreg` net-browser power and `powermetrics` component power)  
- **🌐 Active browsing simulation** (tab cycling, scrolling, searching, reloading, zoom adjustments)
- **📊 Statistical analysis** with mean, min, max, standard deviation, and efficiency comparisons
- **🧹 Clean test isolation** between different browsers with automated cleanup
- **🔋 Battery life estimation** based on actual power consumption data

## Browsing Patterns

The benchmark simulates six realistic browsing behaviors:

1. **Quick Scan** - Fast scrolling through content (like skimming news)
2. **Detailed Read** - Slower, deliberate reading with small scrolls
3. **Search Mode** - Using Cmd+F to search within pages
4. **Link Navigation** - Tab key navigation between clickable elements
5. **Page Reload** - Refreshing content (common on news/social sites)
6. **Zoom Adjust** - Changing zoom levels for better readability

## Requirements

- macOS (tested on macOS 12+)
- Python 3.7+
- At least one supported browser installed (Safari, Brave, Chrome, Firefox, Edge, or Comet)
- Administrator privileges (for `powermetrics` in `browser_bench.py`)
- MacBook on battery power (required for `browser_bench2.py`)
- Pandas library for report generation

## Quick Start

1. **Setup the environment** (using [uv](https://docs.astral.sh/uv/)):
   ```bash
   cd BrowserBench
   uv venv
   source .venv/bin/activate
   uv pip install pandas
   ```
2. **Standardize the environment before benchmarking (for precise measurements)**:
   ```bash
   uv run standardize_env.py
   ```
   Run this before `browser_bench.py` or `browser_bench2.py` to reduce measurement noise and improve consistency.

3. **Workflow A (recommended): `browser_bench2.py` (`ioreg`)**  
   This is the more useful default for most comparisons.

   **Run benchmark**:
   ```bash
   uv run browser_bench2.py
   ```

   **Run specific browsers and custom duration**:
   ```bash
   uv run browser_bench2.py --browsers chrome,safari --duration 600
   ```

   **List browser keys**:
   ```bash
   uv run browser_bench2.py --list-browsers
   ```

   **Generate report**:
   ```bash
   uv run report2.py
   ```

4. **Workflow B: `browser_bench.py` (`powermetrics`)**  
   Useful when you want component-power sampling via `powermetrics` (requires `sudo` authorization during run).

   **Run benchmark**:
   ```bash
   uv run browser_bench.py
   ```

   **Run specific browsers**:
   ```bash
   uv run browser_bench.py --browsers chrome,firefox,edge
   ```

   **List browser keys**:
   ```bash
   uv run browser_bench.py --list-browsers
   ```

   **Generate report**:
   ```bash
   uv run report.py
   ```

## Which Workflow Should I Use?

`browser_bench2.py` is generally more useful and should be your default.

- **Advantages of `browser_bench2.py`**
  - No top-level `sudo` requirement for the benchmark script
  - Measures total system drain and subtracts idle baseline (`Net Browser Power`)
  - Supports `--duration` for quick, repeatable focused tests

- **Advantages of `browser_bench.py`**
  - Uses `powermetrics` for CPU/GPU/ANE-oriented power sampling
  - Helpful as a secondary validation method when you want component-level perspective

## Files

- `browser_bench.py` - Benchmark script using `powermetrics` (requires sudo)
- `browser_bench2.py` - Benchmark script using `ioreg` (no sudo required; MacBook must be unplugged)
- `standardize_env.py` - Pre-benchmark environment setup (brightness, Focus Mode, etc.)
- `report.py` - Analysis and reporting tool for `browser_bench.py` results
- `report2.py` - Analysis and reporting tool for `browser_bench2.py` results
- `sites.txt` - List of websites to test with (customizable)
- `browser_power_results.csv` / `browser_power_results2.csv` - Generated power measurement data (created after benchmark)

## Sample Results

Recent benchmark results (via `report2.py`, measuring net browser power above idle baseline):

**Estimated battery life (50Wh battery) during active browsing:**

| Browser | Mean Estimate | Median Estimate |
|---------|---------------|-----------------|
| Brave | ~9.7h | ~10.4h |
| Chrome Beta | ~10.7h | ~15.0h |
| Comet | ~8.0h | ~10.2h |
| Edge | ~9.1h | ~11.9h |
| Firefox | ~6.5h | ~7.8h |
| Safari | ~9.6h | ~13.8h |
| Zen | ~6.1h | ~6.6h |

## Configuration

Customize defaults in `browser_bench.py`:

```python
# Test duration settings
POWERMETRICS_DURATION_SEC = 1200  # Total monitoring time
TAB_ACTIVITY_DURATION = int(POWERMETRICS_DURATION_SEC * 0.8)  # Active browsing time

# Browser configuration (keys used by --browsers)
BROWSERS = {
    "safari": {...},
    "brave": {...},
    "chromebeta": {...},
    "firefox": {...},
    "edge": {...},
    "comet": {...},
    "atlas": {...},
    "zen": {...},
}

# Browsing patterns (automatically rotated)
BROWSING_PATTERNS = [
    "quick_scan", "detailed_read", "search_mode",
    "link_navigation", "reload_page", "zoom_adjust"
]
```

For `browser_bench2.py`, use `--duration` to override runtime without editing code:
`uv run browser_bench2.py --duration 1200`

Customize test websites by editing `sites.txt` (one URL per line).

### Browser selection

- Default: all configured browsers are tested.
- Use `--browsers` with comma-separated keys to limit the run.
- Example: `uv run browser_bench2.py --browsers brave,safari,edge`

## How It Works

1. **🌐 Opens multiple tabs** with real websites from `sites.txt`
2. **🎭 Simulates realistic browsing** using 6 different behavioral patterns
3. **📏 Monitors power consumption** every second using one of two methods:
   - `browser_bench2.py`: `ioreg` + idle-baseline subtraction (`Net Browser Power`)
   - `browser_bench.py`: `powermetrics` CPU/GPU/ANE sampling
4. **📈 Collects statistical data** over configurable test periods
5. **🧮 Generates comparative analysis** with efficiency calculations and battery estimates
6. **🧹 Automatically cleans up** browser state between tests

## Technical Implementation

- **AppleScript Integration**: Native browser control for realistic automation
- **Concurrent Processing**: Browsing simulation runs parallel to power monitoring
- **Pattern Rotation**: Ensures variety with scheduled and random pattern selection
- **Robust Error Handling**: Graceful handling of automation and measurement errors
- **Real-time Data Logging**: CSV format with timestamps for detailed analysis

## Adding New Browsers

1. Add a new entry to `BROWSERS` with:
   - `display_name` (for logs/CSV)
   - `app_name` (macOS app name used with `open -a`)
   - `process_name` (name used by AppleScript System Events)
2. Verify tab switching works with Cmd+number shortcuts for the new browser.
3. Validate with a targeted run:
   ```bash
   uv run browser_bench2.py --browsers your-browser-key --duration 300
   ```

## Troubleshooting

- **Permission Issues**: `browser_bench.py` requires `sudo` authorization for `powermetrics`
- **Plugged-in Laptop**: `browser_bench2.py` requires battery-discharge mode (unplugged MacBook)
- **Empty Results**: Check that browsers are installed and accessible
- **High CPU Usage**: Normal during testing due to active browsing simulation

## Real-World Impact

The benchmark results show that browser choice can significantly impact battery life:

- **45% power difference** between most and least efficient browsers
- **~30 hour difference** in battery life for typical usage
- **Consistent patterns** across different website types and usage scenarios

This data helps users make informed decisions about browser choice based on their priorities (battery life vs. features).

## License

MIT License - Feel free to use and modify for your own browser testing needs.

---

## 🤖 For AI Agents

If you are an AI agent working on this repository, please refer to [AGENTS.md](./AGENTS.md) for a technical guide on environment setup, core scripts, and automation mechanics.

---

*Built with ❤️ for the macOS community. Contributions and improvements welcome!*
