# Browser Power Benchmark

A comprehensive tool to measure and compare real-world power consumption of different web browsers on macOS using advanced browsing simulation patterns.

## Overview

This benchmark simulates realistic browsing behavior (tab switching, scrolling, searching, page reloading) while measuring precise power consumption using macOS's built-in `powermetrics` utility. The tool provides statistical analysis to compare browser efficiency and real-world battery life impact.

## Features

- **🤖 Advanced browser automation** using AppleScript with 6 different browsing patterns
- **🧭 Selective browser testing** via CLI (`--browsers`) for Chrome/Firefox/Edge/Safari/Brave/Comet
- **⚡ Precise power monitoring** with CPU + GPU + ANE measurements every second  
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
- Administrator privileges (for `powermetrics`)
- Pandas library for report generation

## Quick Start

1. **Setup the environment** (using [uv](https://docs.astral.sh/uv/)):
   ```bash
   cd BrowserBench
   uv venv
   source .venv/bin/activate
   uv pip install pandas
   ```

2. **Run the benchmark** (requires sudo for power monitoring):
   ```bash
   sudo python browser_bench.py
   ```

   **Run specific browsers only**:
   ```bash
   sudo python browser_bench.py --browsers chrome,firefox,edge
   ```

   **List available browser keys**:
   ```bash
   python browser_bench.py --list-browsers
   ```

3. **Generate detailed report**:
   ```bash
   python report.py
   ```

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

| Browser | Net Mean Power (mW) | Net Median Power (mW) | Net Min Power (mW) | Net Max Power (mW) | Std Dev (mW) | Measurements |
|---------|---------------------|-----------------------|--------------------|--------------------|--------------|--------------|
| Brave | 1102.93 | 360.53 | 0 | 6,676 | 1828.28 | 1144 |
| ChatGPT Atlas | 141.65 | 0.00 | 0 | 1,731 | 437.36 | 1155 |
| Chrome Beta | 1129.84 | 0.00 | 0 | 19,749 | 3958.86 | 1139 |
| Comet | 2399.76 | 451.20 | 0 | 22,298 | 4724.15 | 1141 |
| Edge | 1655.27 | 0.00 | 0 | 22,103 | 3905.93 | 1141 |
| Firefox | 3314.93 | 1964.79 | 0 | 14,475 | 4031.72 | 1144 |
| Safari | 1467.26 | 0.00 | 0 | 16,993 | 3971.11 | 1139 |
| Zen | 4104.95 | 3109.33 | 0 | 13,080 | 4698.88 | 1144 |

**Efficiency Analysis:** ChatGPT Atlas is most efficient (142 mW net avg); Zen is least efficient (4,105 mW net avg) — a 96.5% improvement (3,963 mW difference).

**Estimated battery life (50Wh battery) during active browsing:**

| Browser | Mean Estimate | Median Estimate |
|---------|---------------|-----------------|
| Brave | ~9.7h | ~10.4h |
| ChatGPT Atlas | ~15.3h | ~17.6h |
| Chrome Beta | ~10.7h | ~15.0h |
| Comet | ~8.0h | ~10.2h |
| Edge | ~9.1h | ~11.9h |
| Firefox | ~6.5h | ~7.8h |
| Safari | ~9.6h | ~13.8h |
| Zen | ~6.1h | ~6.6h |

## Configuration

Customize test duration and behavior in `browser_bench.py`:

```python
# Test duration settings
POWERMETRICS_DURATION_SEC = 120  # Total monitoring time
TAB_ACTIVITY_DURATION = 90       # Active browsing time

# Browser configuration (keys used by --browsers)
BROWSERS = {
    "safari": {...},
    "brave": {...},
    "chrome": {...},
    "firefox": {...},
    "edge": {...},
    "comet": {...},
}

# Browsing patterns (automatically rotated)
BROWSING_PATTERNS = [
    "quick_scan", "detailed_read", "search_mode",
    "link_navigation", "reload_page", "zoom_adjust"
]
```

Customize test websites by editing `sites.txt` (one URL per line).

### Browser selection

- Default: all configured browsers are tested.
- Use `--browsers` with comma-separated keys to limit the run.
- Example: `sudo python browser_bench.py --browsers chrome,firefox,edge`

## How It Works

1. **🌐 Opens multiple tabs** with real websites from `sites.txt`
2. **🎭 Simulates realistic browsing** using 6 different behavioral patterns
3. **📏 Monitors power consumption** every second using `powermetrics`
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
   sudo python browser_bench.py --browsers your-browser-key
   ```

## Troubleshooting

- **Permission Issues**: Ensure you run with `sudo` for powermetrics access
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
