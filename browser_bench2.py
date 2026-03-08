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
import re
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
# Configuration defaults
DEFAULT_DURATION_SEC = 1200  # 20 minutes default power monitoring
SITES_FILE = "sites.txt"
OUTPUT_FILE = "browser_power_results2.csv"
RESULT_COLUMNS = [
    "Browser",
    "Timestamp",
    "Total Power(mW)",
    "Idle Baseline(mW)",
    "Net Browser Power(mW)",
]

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
    time.sleep(2)

    # Maximize the window (not full-screen space)
    try:
        maximize_script = f"""
        tell application "Finder"
            set desktopSize to bounds of window of desktop
        end tell
        tell application "{app_name}"
            activate
            set bounds of front window to desktopSize
        end tell
        """
        subprocess.run(["osascript", "-e", maximize_script])
    except Exception as e:
        print(f"Warning: Could not maximize {display_name} window: {e}")

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


def get_system_power_mw():
    """Get the current total system power draw in milliwatts using ioreg."""
    try:
        # Run ioreg to get AppleSmartBattery data
        result = subprocess.run(
            ["ioreg", "-r", "-n", "AppleSmartBattery"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

        output = result.stdout

        # Check if plugged in (ExternalConnected = Yes)
        if "ExternalConnected" in output and '"ExternalConnected" = Yes' in output:
            return None  # Cannot measure negative drain when plugged in

        # Parse Voltage and Amperage
        voltage_match = re.search(r'"Voltage" = (\d+)', output)
        amperage_match = re.search(r'"Amperage" = (-?\d+)', output)

        if voltage_match and amperage_match:
            voltage_mv = int(voltage_match.group(1))
            amperage_raw = int(amperage_match.group(1))

            # ioreg sometimes outputs negative numbers as 64-bit unsigned integers
            if amperage_raw > 2**63:
                amperage_ma = amperage_raw - 2**64
            else:
                amperage_ma = amperage_raw

            # Power in milliwatts = Voltage(mV) * Amperage(mA) / 1000
            # Amperage is negative when discharging, so taking the absolute value
            power_mw = abs((voltage_mv * amperage_ma) / 1000.0)
            return power_mw

        return 0.0
    except subprocess.CalledProcessError:
        return 0.0
    except Exception as e:
        print(f"  Warning: Error reading ioreg: {e}")
        return 0.0


def measure_idle_baseline(duration_sec=60):
    """Measures the baseline power draw with no browsers running."""
    print(f"\nMeasuring baseline idle power for {duration_sec} seconds...")
    print("Please do not interact with the computer.")

    start_time = time.time()
    readings = []

    while time.time() - start_time < duration_sec:
        power = get_system_power_mw()
        if power is None:
            raise RuntimeError(
                "MacBook is plugged into power! Please unplug to measure battery drain."
            )

        if power > 0:
            readings.append(power)

        time.sleep(1.0)

    if not readings:
        print("Warning: Could not measure idle baseline. Proceeding with 0mW baseline.")
        return 0.0

    baseline_mw = sum(readings) / len(readings)
    print(f"Measured {len(readings)} readings.")
    print(f"Baseline Idle Power: {baseline_mw:.2f} mW")
    return baseline_mw


def run_power_monitoring(browser_key, num_tabs, idle_baseline_mw, duration_sec):
    """Run ioreg power monitoring while simulating browsing"""
    browser = get_browser_info(browser_key)
    display_name = browser["display_name"]
    print(f"Running power monitoring for {display_name}...")

    tab_activity_duration = int(duration_sec * 0.8)

    # Start browsing simulation in separate thread
    browsing_thread = Thread(
        target=simulate_active_browsing,
        args=(browser_key, num_tabs, tab_activity_duration),
    )
    browsing_thread.daemon = True
    browsing_thread.start()

    start_time = time.time()
    power_readings = 0

    with open(OUTPUT_FILE, "a") as f:
        while time.time() - start_time < duration_sec:
            power_mw = get_system_power_mw()

            if power_mw is None:
                print("Warning: MacBook plugged in mid-test. Invalidating reading.")
            elif power_mw > 0:
                net_power = max(0, power_mw - idle_baseline_mw)
                timestamp = int(time.time())

                # ["Browser", "Timestamp", "Total Power(mW)", "Idle Baseline(mW)", "Net Browser Power(mW)"]
                f.write(
                    f"{display_name},{timestamp},{power_mw:.2f},{idle_baseline_mw:.2f},{net_power:.2f}\n"
                )
                f.flush()

                power_readings += 1
                if power_readings % 15 == 0:
                    print(
                        f"  Collected {power_readings} power readings (Current Net: {net_power:.2f} mW)..."
                    )

            time.sleep(1.0)

    browsing_thread.join(timeout=5)
    print(
        f"Monitoring for {display_name} finished. Collected {power_readings} readings."
    )


def close_browser_tabs(browser_key):
    """Fully quit the browser application"""
    browser = get_browser_info(browser_key)
    display_name = browser["display_name"]
    app_name = browser["app_name"]
    print(f"Quitting {display_name}...")
    try:
        close_script = f"""
        tell application "{app_name}" to quit
        """

        subprocess.run(["osascript", "-e", close_script])
        print(f"{display_name} quit successfully.")
    except Exception as e:
        print(f"Error quitting {display_name}: {e}")


def main():
    """Main benchmark execution"""
    # Prevent system and display sleep during the entire benchmark run
    caffeinate_proc = subprocess.Popen(["caffeinate", "-di"])

    try:
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
        parser.add_argument(
            "--duration",
            type=int,
            default=DEFAULT_DURATION_SEC,
            help=f"Total duration in seconds to test each browser (default: {DEFAULT_DURATION_SEC})",
        )
        args = parser.parse_args()

        if args.list_browsers:
            print("Available browsers:")
            for key, data in BROWSERS.items():
                print(f"  {key}: {data['display_name']}")
            return

        selected_browsers = parse_browser_selection(args.browsers)
        duration_sec = args.duration
        tab_activity_duration = int(duration_sec * 0.8)

        print("=== Enhanced Browser Power Benchmark ===")
        print(f"Power monitoring: {duration_sec}s")
        print(f"Active browsing: {tab_activity_duration}s")
        print(f"Browsing patterns: {', '.join(BROWSING_PATTERNS)}")
        print(f"Selected browsers: {', '.join(selected_browsers)}")

        # Load test sites
        sites = []
        with open(SITES_FILE, "r") as f:
            sites = [line.strip() for line in f if line.strip()]

        print(f"Testing with {len(sites)} websites")

        # Ensure the laptop is unplugged before starting
        initial_check = get_system_power_mw()
        if initial_check is None:
            print("\nERROR: MacBook is currently plugged into a power source.")
            print("Total system power can only be measured via ioreg when discharging.")
            print("Please UNPLUG the laptop and run the benchmark again.")
            return

        # Measure the baseline idle power
        # We fully quit all possible browsers first to get a true idle baseline
        print(
            "\nPreparing for idle baseline measurement. Quitting all known browsers..."
        )
        for b_key in BROWSERS.keys():
            close_browser_tabs(b_key)
        time.sleep(5)  # Give applications time to fully terminate

        idle_baseline_mw = measure_idle_baseline(duration_sec=60)

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

            # Close all restored windows to ensure a clean slate
            print(f"Closing restored windows in {display_name}...")
            close_windows_script = f"""
            tell application "{app_name}"
                repeat with w in windows
                    close w
                end repeat
            end tell
            """
            subprocess.run(["osascript", "-e", close_windows_script])
            time.sleep(2)

            open_tabs_in_browser(browser_key, sites)
            print(f"Waiting 12 seconds for {display_name} to load content...")
            time.sleep(12)

            run_power_monitoring(
                browser_key, len(sites), idle_baseline_mw, duration_sec
            )
            close_browser_tabs(browser_key)

            print(f"=== Finished {display_name} test ===")
            if browser_key != selected_browsers[-1]:
                print("Waiting 15 seconds before next browser...")
                time.sleep(15)

        print("\n=== Enhanced Benchmark Complete! ===")
        print(f"Results saved to {OUTPUT_FILE}")
        print("Advanced browsing patterns were used for realistic power measurements.")

    finally:
        # Kill caffeinate to allow normal sleep again
        caffeinate_proc.terminate()
        caffeinate_proc.wait()


if __name__ == "__main__":
    main()
