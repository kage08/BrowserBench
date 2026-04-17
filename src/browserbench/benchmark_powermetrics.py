"""powermetrics-based BrowserBench runner."""

from __future__ import annotations

import random
import subprocess
import time
from pathlib import Path
from threading import Thread

from .benchmark_ioreg import (
    BROWSING_PATTERNS,
    focus_tab,
    get_browsing_behavior,
)
from .common import ensure_results_file_for_selected_browsers, get_browser_info, load_sites
from .config import BROWSERS, DEFAULT_POWERMETRICS_DURATION_SEC, POWERMETRICS_COLUMNS
from .doctor import run_doctor


def open_tabs_in_browser(browser_key: str, sites: list[str]) -> None:
    browser = get_browser_info(browser_key)
    display_name = browser["display_name"]
    app_name = browser["app_name"]
    print(f"Opening {len(sites)} tabs in {display_name}...")
    subprocess.run(["open", "-a", app_name], check=False)
    time.sleep(1)
    for site in sites:
        subprocess.run(["open", "-a", app_name, site], check=False)
        time.sleep(0.3)
    print(f"Tabs opened in {display_name}.")


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


def close_browser_tabs(browser_key: str) -> None:
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
        subprocess.run(["osascript", "-e", close_script], check=False)
        print(f"Tabs closed in {display_name}.")
    except Exception as exc:
        print(f"Error closing tabs in {display_name}: {exc}")


def run_powermetrics(
    browser_key: str,
    num_tabs: int,
    output_file: str | Path,
    duration_sec: int,
) -> None:
    browser = get_browser_info(browser_key)
    display_name = browser["display_name"]
    print(f"Running powermetrics for {display_name}...")

    browsing_thread = Thread(
        target=simulate_active_browsing,
        args=(browser_key, num_tabs, int(duration_sec * 0.8)),
        daemon=True,
    )
    browsing_thread.start()

    output_path = Path(output_file)
    with output_path.open("a", encoding="utf-8") as file_handle:
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

        while time.time() - start_time < duration_sec:
            line = proc.stdout.readline()
            if "Combined Power (CPU + GPU + ANE):" not in line:
                continue
            try:
                value = int(line.split(":")[1].strip().replace("mW", "").strip())
                timestamp = int(time.time())
                file_handle.write(f"{display_name},{timestamp},{value}\n")
                file_handle.flush()
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


def run_benchmark(
    selected_browsers: list[str],
    sites_file: str | Path,
    output_file: str | Path,
    duration_sec: int = DEFAULT_POWERMETRICS_DURATION_SEC,
) -> int:
    random.shuffle(selected_browsers)
    print("=== Enhanced Browser Power Benchmark ===")
    print(f"Power monitoring: {duration_sec}s")
    print(f"Active browsing: {int(duration_sec * 0.8)}s")
    print(f"Browsing patterns: {', '.join(BROWSING_PATTERNS)}")
    print(f"Selected browsers: {', '.join(selected_browsers)}")
    print("This workflow uses powermetrics and will prompt for sudo during measurement.")
    print(f"Sites file: {sites_file}")
    print(f"Output file: {output_file}")

    if not run_doctor(BROWSERS, selected_browsers, sites_file, require_battery=False):
        print("\nAborting before the benchmark starts.")
        return 1

    sites = load_sites(sites_file)
    print(f"Testing with {len(sites)} websites")

    ensure_results_file_for_selected_browsers(
        output_file, POWERMETRICS_COLUMNS, selected_browsers
    )

    for browser_key in selected_browsers:
        display_name = get_browser_info(browser_key)["display_name"]
        app_name = get_browser_info(browser_key)["app_name"]
        print(f"\n=== Starting {display_name} test ===")
        print(f"Launching {display_name} and waiting for session restore...")
        subprocess.run(["open", "-a", app_name], check=False)
        time.sleep(5)

        close_browser_tabs(browser_key)
        time.sleep(2)

        open_tabs_in_browser(browser_key, sites)
        print(f"Waiting 10 seconds for {display_name} to load content...")
        time.sleep(10)

        run_powermetrics(browser_key, len(sites), output_file, duration_sec)
        close_browser_tabs(browser_key)

        print(f"=== Finished {display_name} test ===")
        if browser_key != selected_browsers[-1]:
            print("Waiting 15 seconds before next browser...")
            time.sleep(15)

    print("\n=== Enhanced Benchmark Complete! ===")
    print(f"Results saved to {output_file}")
    return 0

