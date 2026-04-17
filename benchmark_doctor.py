#!/usr/bin/env python3
"""
Preflight checks for BrowserBench.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from typing import Any


def _run_command(command: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        return False, str(exc)

    return True, result.stdout.strip()


def _app_is_installed(app_name: str) -> bool:
    ok, _ = _run_command(["open", "-Ra", app_name])
    return ok


def get_battery_status() -> dict[str, Any]:
    ok, output = _run_command(["ioreg", "-r", "-n", "AppleSmartBattery"])
    if not ok:
        return {"ok": False, "message": output}

    unplugged = '"ExternalConnected" = No' in output
    plugged_in = '"ExternalConnected" = Yes' in output

    return {
        "ok": True,
        "plugged_in": plugged_in,
        "unplugged": unplugged,
    }


def load_sites(sites_file: str) -> list[str]:
    with open(sites_file, "r") as file_handle:
        return [line.strip() for line in file_handle if line.strip()]


def run_doctor(
    browsers: dict[str, dict[str, str]],
    selected_browsers: list[str] | None = None,
    sites_file: str = "sites.txt",
) -> bool:
    selected_browsers = selected_browsers or list(browsers.keys())
    success = True

    print("=== BrowserBench Doctor ===")

    if platform.system() == "Darwin":
        print("[ok] macOS detected")
    else:
        print(f"[fail] Unsupported OS: {platform.system()} (BrowserBench expects macOS)")
        success = False

    if shutil.which("osascript"):
        print("[ok] osascript available")
    else:
        print("[fail] osascript not found")
        success = False

    if shutil.which("caffeinate"):
        print("[ok] caffeinate available")
    else:
        print("[fail] caffeinate not found")
        success = False

    if os.path.exists(sites_file):
        try:
            sites = load_sites(sites_file)
        except OSError as exc:
            print(f"[fail] Could not read {sites_file}: {exc}")
            success = False
        else:
            if sites:
                print(f"[ok] {sites_file} contains {len(sites)} URLs")
            else:
                print(f"[fail] {sites_file} is empty")
                success = False
    else:
        print(f"[fail] {sites_file} not found")
        success = False

    installed = []
    missing = []
    for browser_key in selected_browsers:
        browser = browsers[browser_key]
        if _app_is_installed(browser["app_name"]):
            installed.append(browser_key)
        else:
            missing.append(f"{browser_key} ({browser['app_name']})")

    if installed:
        print(f"[ok] Installed selected browsers: {', '.join(installed)}")
    if missing:
        print(f"[warn] Could not verify these browser apps: {', '.join(missing)}")
        print("       If they are installed, you can still try the benchmark.")

    battery_status = get_battery_status()
    if not battery_status["ok"]:
        print(f"[warn] Could not read battery status: {battery_status['message']}")
    elif battery_status["plugged_in"]:
        print("[warn] MacBook appears to be plugged in")
        print("       Unplug it before running browser_bench2.py")
    elif battery_status["unplugged"]:
        print("[ok] MacBook appears to be on battery")

    if shutil.which("sudo") and shutil.which("powermetrics"):
        print("[ok] powermetrics command available")
    else:
        print("[warn] powermetrics not available in PATH")
        print("       browser_bench.py may not work on this machine")

    print()
    if success:
        print("Doctor completed: benchmark prerequisites look good.")
    else:
        print("Doctor completed: fix the failed checks before benchmarking.")

    return success
