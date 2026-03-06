#!/usr/bin/env python3
"""
Enhanced Browser Power Benchmark with Advanced Browsing Simulation

This tool measures real-world power consumption of different web browsers on macOS
by simulating various realistic browsing behaviors and patterns.
"""

import argparse
import csv
import os
import random
import subprocess
import time
from threading import Thread

# Configuration
BROWSERS = {
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
    "chromebeta": {
        "display_name": "Chrome Beta",
        "app_name": "Google Chrome Beta",
        "process_name": "Google Chrome Beta",
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
POWERMETRICS_DURATION_SEC = 1200  # 20 minutes of power monitoring
TAB_ACTIVITY_DURATION = int(POWERMETRICS_DURATION_SEC * 0.8)  # 80% of total test time
SITES_FILE = "sites.txt"
OUTPUT_FILE = "browser_power_results.csv"
RESULT_COLUMNS = ["Browser", "Timestamp", "Power(mW)"]

# Enhanced browsing patterns
BROWSING_PATTERNS = [
    "quick_scan",  # Fast scrolling through content
    "detailed_read",  # Slower, deliberate reading
    "search_mode",  # Using Cmd+F to search
    "link_navigation",  # Tab navigation between links
    "reload_page",  # Refreshing content
    "zoom_adjust",  # Changing zoom levels
]


def parse_browser_selection(browser_option):
    """Parse browser list from CLI option"""
    if not browser_option or browser_option.lower() == "all":
        return list(BROWSERS.keys())

    selected = []
    for browser_key in browser_option.split(","):
        key = browser_key.strip().lower()
        if key not in BROWSERS:
            valid = ", ".join(BROWSERS.keys())
            raise ValueError(
                f"Unsupported browser '{browser_key}'. Valid options: {valid}"
            )
        selected.append(key)

    # Preserve order while removing duplicates
    return list(dict.fromkeys(selected))


def get_browser_info(browser_key):
    """Return normalized browser metadata"""
    return BROWSERS[browser_key]


def ensure_results_file_for_selected_browsers(selected_browsers):
    """Preserve existing results and replace rows for selected browsers."""
    selected_display_names = {
        get_browser_info(browser_key)["display_name"]
        for browser_key in selected_browsers
    }

    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "w", newline="") as file_handle:
            writer = csv.DictWriter(file_handle, fieldnames=RESULT_COLUMNS)
            writer.writeheader()
        return

    try:
        with open(OUTPUT_FILE, newline="") as file_handle:
            reader = csv.DictReader(file_handle)
            if reader.fieldnames is None or any(
                column not in reader.fieldnames for column in RESULT_COLUMNS
            ):
                raise ValueError("Unexpected CSV header format")
            rows = list(reader)
    except (OSError, csv.Error, ValueError) as exc:
        print(f"Warning: resetting {OUTPUT_FILE} due to read error: {exc}")
        with open(OUTPUT_FILE, "w", newline="") as file_handle:
            writer = csv.DictWriter(file_handle, fieldnames=RESULT_COLUMNS)
            writer.writeheader()
        return

    filtered_rows = [
        row for row in rows if row.get("Browser", "") not in selected_display_names
    ]
    replaced_rows = len(rows) - len(filtered_rows)

    with open(OUTPUT_FILE, "w", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        writer.writerows(filtered_rows)

    if replaced_rows > 0:
        print(
            f"Replaced {replaced_rows} previous measurements for selected browsers in {OUTPUT_FILE}."
        )
    else:
        print(f"No previous measurements found for selected browsers in {OUTPUT_FILE}.")


def open_tabs_in_browser(browser_key, sites):
    """Open multiple tabs with specified websites"""
    browser = get_browser_info(browser_key)
    display_name = browser["display_name"]
    app_name = browser["app_name"]

    print(f"Opening {len(sites)} tabs in {display_name}...")
    subprocess.run(["open", "-a", app_name])
    time.sleep(1)
    for site in sites:
        subprocess.run(["open", "-a", app_name, site])
        time.sleep(0.3)
    print(f"Tabs opened in {display_name}.")


def get_browsing_behavior(browser_key, pattern):
    """Generate AppleScript for different browsing behaviors"""
    browser_process = get_browser_info(browser_key)["process_name"]

    behaviors = {
        "quick_scan": f'''
        tell application "System Events"
            tell process "{browser_process}"
                key code 125 using {{command down}}  -- Page Down
                delay 0.8
                key code 125 using {{command down}}  -- Page Down again
                delay 0.8
                key code 125 using {{command down}}  -- Page Down third time
                delay 0.5
                key code 126 using {{command down}}  -- Page Up
                delay 0.5
            end tell
        end tell
        ''',
        "detailed_read": f'''
        tell application "System Events"
            tell process "{browser_process}"
                key code 125  -- Small scroll down
                delay 2.5
                key code 125  -- Small scroll down
                delay 2.5
                key code 125  -- Small scroll down
                delay 2.0
                key code 126  -- Small scroll up
                delay 1.5
                key code 126  -- Small scroll up
                delay 1.5
            end tell
        end tell
        ''',
        "search_mode": f'''
        tell application "System Events"
            tell process "{browser_process}"
                key code 3 using {{command down}}  -- Cmd+F (Find)
                delay 1.0
                keystroke "news"  -- Type search term
                delay 1.0
                key code 36  -- Enter
                delay 1.0
                key code 53  -- Escape to close find
                delay 0.5
                key code 125 using {{command down}}  -- Page Down
                delay 1.5
            end tell
        end tell
        ''',
        "link_navigation": f'''
        tell application "System Events"
            tell process "{browser_process}"
                key code 48  -- Tab to navigate to links
                delay 0.8
                key code 48  -- Tab again
                delay 0.8
                key code 48  -- Tab again
                delay 0.8
                key code 125  -- Small scroll
                delay 1.0
                key code 48  -- Tab to more links
                delay 0.8
            end tell
        end tell
        ''',
        "reload_page": f'''
        tell application "System Events"
            tell process "{browser_process}"
                key code 15 using {{command down}}  -- Cmd+R (Reload)
                delay 3.0  -- Wait for page to reload
                key code 125 using {{command down}}  -- Page Down after reload
                delay 1.5
            end tell
        end tell
        ''',
        "zoom_adjust": f'''
        tell application "System Events"
            tell process "{browser_process}"
                key code 24 using {{command down}}  -- Cmd++ (Zoom in)
                delay 1.0
                key code 125  -- Scroll with new zoom
                delay 1.5
                key code 27 using {{command down}}  -- Cmd+- (Zoom out)
                delay 1.0
                key code 125  -- Scroll with reset zoom
                delay 1.5
            end tell
        end tell
        ''',
    }

    return behaviors.get(pattern, behaviors["quick_scan"])


def focus_tab(browser_key, tab_index):
    """Focus a tab by index using browser-agnostic keyboard shortcuts"""
    browser = get_browser_info(browser_key)
    app_name = browser["app_name"]
    process_name = browser["process_name"]

    keycodes = {1: 18, 2: 19, 3: 20, 4: 21, 5: 23, 6: 22, 7: 26, 8: 28, 9: 25}
    key_code = keycodes.get(tab_index, 25)  # Cmd+9 for tab 9+

    focus_script = f"""
    tell application "{app_name}" to activate
    tell application "System Events"
        tell process "{process_name}"
            key code {key_code} using {{command down}}
        end tell
    end tell
    """
    subprocess.run(["osascript", "-e", focus_script])


def simulate_active_browsing(browser_key, num_tabs, duration_sec):
    """Enhanced browsing simulation with multiple realistic behaviors"""
    browser = get_browser_info(browser_key)
    display_name = browser["display_name"]
    process_name = browser["process_name"]

    print(f"Starting enhanced browsing simulation for {display_name}...")

    start_time = time.time()
    tab_index = 1
    iteration = 0

    while time.time() - start_time < duration_sec:
        try:
            iteration += 1

            # Focus on current tab
            focus_tab(browser_key, tab_index)

            # Choose browsing pattern based on iteration to ensure variety
            if iteration % 8 == 0:
                pattern = "reload_page"  # Occasionally reload pages
            elif iteration % 6 == 0:
                pattern = "search_mode"  # Occasionally search
            elif iteration % 4 == 0:
                pattern = "zoom_adjust"  # Occasionally adjust zoom
            else:
                pattern = random.choice(
                    ["quick_scan", "detailed_read", "link_navigation"]
                )

            # Get the behavior script
            behavior_script = get_browsing_behavior(browser_key, pattern)

            # Execute the scripts
            time.sleep(random.uniform(0.5, 1.2))  # Variable pause after tab switch
            subprocess.run(["osascript", "-e", behavior_script])

            # Move to next tab
            tab_index = (tab_index % num_tabs) + 1

            # Variable wait time based on pattern
            wait_times = {
                "detailed_read": random.uniform(4, 7),
                "search_mode": random.uniform(3, 5),
                "reload_page": random.uniform(4, 6),
                "quick_scan": random.uniform(2, 4),
                "link_navigation": random.uniform(3, 5),
                "zoom_adjust": random.uniform(2, 4),
            }

            wait_time = wait_times.get(pattern, 3)
            time.sleep(wait_time)

            # Occasionally simulate back/forward navigation
            if random.random() < 0.1:  # 10% chance
                back_forward_script = f'''
                tell application "System Events"
                    tell process "{process_name}"
                        key code 123 using {{command down}}  -- Cmd+Left (Back)
                        delay 1.5
                        key code 124 using {{command down}}  -- Cmd+Right (Forward)
                        delay 1.5
                    end tell
                end tell
                '''
                subprocess.run(["osascript", "-e", back_forward_script])

        except Exception as e:
            print(f"Error during browsing simulation: {e}")
            time.sleep(1)

    print(f"Enhanced browsing simulation completed for {display_name}.")


def run_powermetrics(browser_key, num_tabs):
    """Run power monitoring while simulating browsing"""
    browser = get_browser_info(browser_key)
    display_name = browser["display_name"]
    print(f"Running powermetrics for {display_name}...")

    # Start browsing simulation in separate thread
    browsing_thread = Thread(
        target=simulate_active_browsing,
        args=(browser_key, num_tabs, TAB_ACTIVITY_DURATION),
    )
    browsing_thread.daemon = True
    browsing_thread.start()

    with open(OUTPUT_FILE, "a") as f:
        proc = subprocess.Popen(
            [
                "sudo",
                "powermetrics",
                "-i",
                "1000",
                "--samplers",
                "cpu_power,gpu_power",
                "-a",
                "--hide-cpu-duty-cycle",
                "--show-usage-summary",
                "--show-extra-power-info",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        start_time = time.time()
        power_readings = 0

        if proc.stdout is None:
            raise RuntimeError("powermetrics stdout was not captured")

        while time.time() - start_time < POWERMETRICS_DURATION_SEC:
            line = proc.stdout.readline()
            if "Combined Power (CPU + GPU + ANE):" in line:
                try:
                    value = int(line.split(":")[1].strip().replace("mW", "").strip())
                    timestamp = int(time.time())
                    f.write(f"{display_name},{timestamp},{value}\n")
                    f.flush()
                    power_readings += 1
                    if power_readings % 15 == 0:
                        print(f"  Collected {power_readings} power readings...")
                except ValueError:
                    print(f"  Warning: Could not parse power value: {line.strip()}")

        proc.terminate()
        proc.wait()

    browsing_thread.join(timeout=5)
    print(
        f"powermetrics for {display_name} finished. Collected {power_readings} readings."
    )


def close_browser_tabs(browser_key):
    """Close all browser tabs and windows"""
    browser = get_browser_info(browser_key)
    display_name = browser["display_name"]
    app_name = browser["app_name"]
    print(f"Closing tabs in {display_name}...")
    try:
        close_script = f"""
        tell application "{app_name}"
            repeat with w in windows
                close w
            end repeat
        end tell
        """

        subprocess.run(["osascript", "-e", close_script])
        print(f"Tabs closed in {display_name}.")
    except Exception as e:
        print(f"Error closing tabs in {display_name}: {e}")


def main():
    """Main benchmark execution"""
    parser = argparse.ArgumentParser(
        description="Run browser power benchmark with realistic browsing simulation."
    )
    parser.add_argument(
        "--browsers",
        default="all",
        help=(
            "Comma-separated browser keys to test "
            f"(e.g. chrome,firefox,edge). Use 'all' for every browser. "
            f"Available: {', '.join(BROWSERS.keys())}"
        ),
    )
    parser.add_argument(
        "--list-browsers",
        action="store_true",
        help="List available browser keys and exit.",
    )
    args = parser.parse_args()

    if args.list_browsers:
        print("Available browsers:")
        for key, data in BROWSERS.items():
            print(f"  {key}: {data['display_name']}")
        return

    selected_browsers = parse_browser_selection(args.browsers)

    print("=== Enhanced Browser Power Benchmark ===")
    print(f"Power monitoring: {POWERMETRICS_DURATION_SEC}s")
    print(f"Active browsing: {TAB_ACTIVITY_DURATION}s")
    print(f"Browsing patterns: {', '.join(BROWSING_PATTERNS)}")
    print(f"Selected browsers: {', '.join(selected_browsers)}")

    # Load test sites
    sites = []
    with open(SITES_FILE, "r") as f:
        sites = [line.strip() for line in f if line.strip()]

    print(f"Testing with {len(sites)} websites")

    # Initialize CSV for browser-level upsert behavior.
    ensure_results_file_for_selected_browsers(selected_browsers)

    # Test each browser
    for browser_key in selected_browsers:
        display_name = get_browser_info(browser_key)["display_name"]
        app_name = get_browser_info(browser_key)["app_name"]
        print(f"\n=== Starting {display_name} test ===")

        # Launch the browser first to trigger any session restore, then wait
        print(f"Launching {display_name} and waiting for session restore...")
        subprocess.run(["open", "-a", app_name])
        time.sleep(5)

        close_browser_tabs(browser_key)
        time.sleep(2)

        open_tabs_in_browser(browser_key, sites)
        print(f"Waiting 12 seconds for {display_name} to load content...")
        time.sleep(12)

        run_powermetrics(browser_key, len(sites))
        close_browser_tabs(browser_key)

        print(f"=== Finished {display_name} test ===")
        if browser_key != selected_browsers[-1]:
            print("Waiting 15 seconds before next browser...")
            time.sleep(15)

    print("\n=== Enhanced Benchmark Complete! ===")
    print(f"Results saved to {OUTPUT_FILE}")
    print("Advanced browsing patterns were used for realistic power measurements.")


if __name__ == "__main__":
    main()
