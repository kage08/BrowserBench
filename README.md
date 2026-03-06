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

- `browser_bench.py` - Enhanced benchmark script with advanced browsing patterns
- `sites.txt` - List of websites to test with (customizable)
- `report.py` - Enhanced analysis and reporting tool with battery life estimates
- `browser_power_results.csv` - Generated power measurement data (created after benchmark)

## Sample Results

Recent benchmark results show significant differences in browser efficiency:

| Browser | Average Power | Min Power | Max Power | Battery Life* | Efficiency |
|---------|---------------|-----------|-----------|---------------|------------|
| Brave   | 743 mW        | 41 mW     | 8,293 mW  | ~67 hours     | 45% better |
| Safari  | 1,356 mW      | 44 mW     | 10,551 mW | ~37 hours     | Baseline   |

*Based on 50Wh battery capacity during active browsing

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
