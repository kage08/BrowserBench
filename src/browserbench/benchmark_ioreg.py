"""ioreg-based BrowserBench runner."""

from __future__ import annotations

import random
import re
import subprocess
import time
from pathlib import Path
from threading import Thread

from .common import ensure_results_file_for_selected_browsers, get_browser_info, load_sites
from .config import BROWSERS, DEFAULT_BASELINE_DURATION_SEC, DEFAULT_IORERG_DURATION_SEC, IORREG_COLUMNS
from .doctor import run_doctor

BROWSING_PATTERNS = [
    "quick_scan",
    "detailed_read",
    "search_mode",
    "link_navigation",
    "reload_page",
    "zoom_adjust",
]


def open_tabs_in_browser(browser_key: str, sites: list[str]) -> None:
    browser = get_browser_info(browser_key)
    display_name = browser["display_name"]
    app_name = browser["app_name"]

    print(f"Opening {len(sites)} tabs in {display_name}...")
    subprocess.run(["open", "-a", app_name], check=False)
    time.sleep(2)

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
        subprocess.run(["osascript", "-e", maximize_script], check=False)
    except Exception as exc:
        print(f"Warning: Could not maximize {display_name} window: {exc}")

    for site in sites:
        subprocess.run(["open", "-a", app_name, site], check=False)
        time.sleep(0.3)
    print(f"Tabs opened in {display_name}.")


def get_browsing_behavior(browser_key: str, pattern: str) -> str:
    browser_process = get_browser_info(browser_key)["process_name"]
    behaviors = {
        "quick_scan": f'''
        tell application "System Events"
            tell process "{browser_process}"
                key code 125 using {{command down}}
                delay 0.8
                key code 125 using {{command down}}
                delay 0.8
                key code 125 using {{command down}}
                delay 0.5
                key code 126 using {{command down}}
                delay 0.5
            end tell
        end tell
        ''',
        "detailed_read": f'''
        tell application "System Events"
            tell process "{browser_process}"
                key code 125
                delay 2.5
                key code 125
                delay 2.5
                key code 125
                delay 2.0
                key code 126
                delay 1.5
                key code 126
                delay 1.5
            end tell
        end tell
        ''',
        "search_mode": f'''
        tell application "System Events"
            tell process "{browser_process}"
                key code 3 using {{command down}}
                delay 1.0
                keystroke "news"
                delay 1.0
                key code 36
                delay 1.0
                key code 53
                delay 0.5
                key code 125 using {{command down}}
                delay 1.5
            end tell
        end tell
        ''',
        "link_navigation": f'''
        tell application "System Events"
            tell process "{browser_process}"
                key code 48
                delay 0.8
                key code 48
                delay 0.8
                key code 48
                delay 0.8
                key code 125
                delay 1.0
                key code 48
                delay 0.8
            end tell
        end tell
        ''',
        "reload_page": f'''
        tell application "System Events"
            tell process "{browser_process}"
                key code 15 using {{command down}}
                delay 3.0
                key code 125 using {{command down}}
                delay 1.5
            end tell
        end tell
        ''',
        "zoom_adjust": f'''
        tell application "System Events"
            tell process "{browser_process}"
                key code 24 using {{command down}}
                delay 1.0
                key code 125
                delay 1.5
                key code 27 using {{command down}}
                delay 1.0
                key code 125
                delay 1.5
            end tell
        end tell
        ''',
    }
    return behaviors.get(pattern, behaviors["quick_scan"])


def focus_tab(browser_key: str, tab_index: int) -> None:
    browser = get_browser_info(browser_key)
    app_name = browser["app_name"]
    process_name = browser["process_name"]
    keycodes = {1: 18, 2: 19, 3: 20, 4: 21, 5: 23, 6: 22, 7: 26, 8: 28, 9: 25}
    key_code = keycodes.get(tab_index, 25)
    focus_script = f"""
    tell application "{app_name}" to activate
    tell application "System Events"
        tell process "{process_name}"
            key code {key_code} using {{command down}}
        end tell
    end tell
    """
    subprocess.run(["osascript", "-e", focus_script], check=False)


def simulate_active_browsing(browser_key: str, num_tabs: int, duration_sec: int) -> None:
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
            focus_tab(browser_key, tab_index)
            if iteration % 8 == 0:
                pattern = "reload_page"
            elif iteration % 6 == 0:
                pattern = "search_mode"
            elif iteration % 4 == 0:
                pattern = "zoom_adjust"
            else:
                pattern = random.choice(
                    ["quick_scan", "detailed_read", "link_navigation"]
                )

            behavior_script = get_browsing_behavior(browser_key, pattern)
            time.sleep(random.uniform(0.5, 1.2))
            subprocess.run(["osascript", "-e", behavior_script], check=False)
            tab_index = (tab_index % num_tabs) + 1

            wait_times = {
                "detailed_read": random.uniform(4, 7),
                "search_mode": random.uniform(3, 5),
                "reload_page": random.uniform(4, 6),
                "quick_scan": random.uniform(2, 4),
                "link_navigation": random.uniform(3, 5),
                "zoom_adjust": random.uniform(2, 4),
            }
            time.sleep(wait_times.get(pattern, 3))

            if random.random() < 0.1:
                back_forward_script = f'''
                tell application "System Events"
                    tell process "{process_name}"
                        key code 123 using {{command down}}
                        delay 1.5
                        key code 124 using {{command down}}
                        delay 1.5
                    end tell
                end tell
                '''
                subprocess.run(["osascript", "-e", back_forward_script], check=False)
        except Exception as exc:
            print(f"Error during browsing simulation: {exc}")
            time.sleep(1)

    print(f"Enhanced browsing simulation completed for {display_name}.")


def get_system_power_mw() -> float | None:
    try:
        result = subprocess.run(
            ["ioreg", "-r", "-n", "AppleSmartBattery"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        output = result.stdout
        if '"ExternalConnected" = Yes' in output:
            return None

        voltage_match = re.search(r'"Voltage" = (\d+)', output)
        amperage_match = re.search(r'"Amperage" = (-?\d+)', output)
        if voltage_match and amperage_match:
            voltage_mv = int(voltage_match.group(1))
            amperage_raw = int(amperage_match.group(1))
            if amperage_raw > 2**63:
                amperage_ma = amperage_raw - 2**64
            else:
                amperage_ma = amperage_raw
            return abs((voltage_mv * amperage_ma) / 1000.0)
        return 0.0
    except subprocess.CalledProcessError as exc:
        print(
            "Warning: ioreg command failed. Ensure this is run on macOS with proper permissions.",
            exc,
        )
        return 0.0
    except Exception as exc:
        print(f"  Warning: Error reading ioreg: {exc}")
        return 0.0


def measure_idle_baseline(duration_sec: int = DEFAULT_BASELINE_DURATION_SEC) -> float:
    print(f"\nMeasuring baseline idle power for {duration_sec} seconds...")
    print("Please do not interact with the computer.")
    start_time = time.time()
    readings: list[float] = []

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


def run_power_monitoring(
    browser_key: str,
    num_tabs: int,
    idle_baseline_mw: float,
    duration_sec: int,
    output_file: str | Path,
) -> None:
    browser = get_browser_info(browser_key)
    display_name = browser["display_name"]
    print(f"Running power monitoring for {display_name}...")

    tab_activity_duration = int(duration_sec * 0.9)
    browsing_thread = Thread(
        target=simulate_active_browsing,
        args=(browser_key, num_tabs, tab_activity_duration),
        daemon=True,
    )
    browsing_thread.start()

    start_time = time.time()
    power_readings = 0
    output_path = Path(output_file)

    with output_path.open("a", encoding="utf-8") as file_handle:
        while time.time() - start_time < duration_sec:
            power_mw = get_system_power_mw()
            if power_mw is None:
                print("Warning: MacBook plugged in mid-test. Invalidating reading.")
            elif power_mw > 0:
                net_power = max(0, power_mw - idle_baseline_mw)
                timestamp = int(time.time())
                file_handle.write(
                    f"{display_name},{timestamp},{power_mw:.2f},{idle_baseline_mw:.2f},{net_power:.2f}\n"
                )
                file_handle.flush()
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


def close_browser(browser_key: str) -> None:
    browser = get_browser_info(browser_key)
    display_name = browser["display_name"]
    app_name = browser["app_name"]
    print(f"Quitting {display_name}...")
    try:
        subprocess.run(["osascript", "-e", f'tell application "{app_name}" to quit'], check=False)
        print(f"{display_name} quit successfully.")
    except Exception as exc:
        print(f"Error quitting {display_name}: {exc}")


def run_benchmark(
    selected_browsers: list[str],
    sites_file: str | Path,
    output_file: str | Path,
    duration_sec: int = DEFAULT_IORERG_DURATION_SEC,
    baseline_duration_sec: int = DEFAULT_BASELINE_DURATION_SEC,
) -> int:
    caffeinate_proc: subprocess.Popen[str] | None = None

    try:
        caffeinate_proc = subprocess.Popen(["caffeinate", "-di"])
        tab_activity_duration = int(duration_sec * 0.8)

        print("=== Enhanced Browser Power Benchmark ===")
        print(f"Power monitoring: {duration_sec}s")
        print(f"Active browsing: {tab_activity_duration}s")
        print(f"Browsing patterns: {', '.join(BROWSING_PATTERNS)}")
        print(f"Selected browsers: {', '.join(selected_browsers)}")
        print(f"Sites file: {sites_file}")
        print(f"Output file: {output_file}")

        if not run_doctor(BROWSERS, selected_browsers, sites_file, require_battery=True):
            print("\nAborting before the benchmark starts.")
            return 1

        sites = load_sites(sites_file)
        print(f"Testing with {len(sites)} websites")

        initial_check = get_system_power_mw()
        if initial_check is None:
            print("\nERROR: MacBook is currently plugged into a power source.")
            print("Total system power can only be measured via ioreg when discharging.")
            print("Please unplug the laptop and run the benchmark again.")
            return 1

        print("\nPreparing for idle baseline measurement. Quitting all known browsers...")
        for browser_key in BROWSERS:
            close_browser(browser_key)
        time.sleep(5)

        idle_baseline_mw = measure_idle_baseline(duration_sec=baseline_duration_sec)
        ensure_results_file_for_selected_browsers(
            output_file, IORREG_COLUMNS, selected_browsers
        )

        for browser_key in selected_browsers:
            display_name = get_browser_info(browser_key)["display_name"]
            app_name = get_browser_info(browser_key)["app_name"]
            print(f"\n=== Starting {display_name} test ===")
            print(f"Launching {display_name} and waiting for session restore...")
            subprocess.run(["open", "-a", app_name], check=False)
            time.sleep(5)

            print(f"Closing restored windows in {display_name}...")
            close_windows_script = f"""
            tell application "{app_name}"
                repeat with w in windows
                    close w
                end repeat
            end tell
            """
            subprocess.run(["osascript", "-e", close_windows_script], check=False)
            time.sleep(2)

            open_tabs_in_browser(browser_key, sites)
            print(f"Waiting 12 seconds for {display_name} to load content...")
            time.sleep(12)

            run_power_monitoring(
                browser_key,
                len(sites),
                idle_baseline_mw,
                duration_sec,
                output_file,
            )
            close_browser(browser_key)

            print(f"=== Finished {display_name} test ===")
            if browser_key != selected_browsers[-1]:
                print("Waiting 15 seconds before next browser...")
                time.sleep(15)

        print("\n=== Enhanced Benchmark Complete! ===")
        print(f"Results saved to {output_file}")
        print("Advanced browsing patterns were used for realistic power measurements.")
        return 0
    finally:
        if caffeinate_proc is not None:
            caffeinate_proc.terminate()
            caffeinate_proc.wait()

