#!/usr/bin/env python3
"""
Setup Benchmark Environment

This script standardizes the macOS environment before running the browser benchmark.
It handles screen brightness and ensures background tasks are paused.
"""

import subprocess


def set_brightness_50():
    print("Setting screen brightness to ~50%...")
    # Using AppleScript to simulate media keys for brightness (145 = down, 144 = up)
    applescript = """
    tell application "System Events"
        -- Press Brightness Down 32 times to ensure it's at zero 
        repeat 32 times
            key code 145
        end repeat
        
        delay 0.5
        
        -- Press Brightness Up 8 times (assuming 16 total steps for standard macOS)
        repeat 8 times
            key code 144
        end repeat
    end tell
    """
    try:
        subprocess.run(["osascript", "-e", applescript], check=True)
        print("Screen brightness set.")
    except subprocess.CalledProcessError as e:
        print(
            f"Warning: Could not automatically set screen brightness. Please do it manually. Error: {e}"
        )


def prompt_user_background_processes():
    print("=" * 60)
    print("ENVIRONMENT STANDARDIZATION CHECKLIST")
    print("=" * 60)
    print("To ensure benchmark accuracy, please complete the following:")
    print("1. Turn ON 'Do Not Disturb' (Focus Mode).")
    print("2. Disable Auto-Brightness / True Tone in System Settings > Displays.")
    print("3. Close unnecessary menu bar apps (e.g., Dropbox, OneDrive, Spotify).")
    print("4. Close completely any background apps that are not being tested.")
    print("=" * 60)

    while True:
        response = input("Have you completed these steps? (Y/n): ").strip().lower()
        if response in ("y", "yes", ""):
            break
        elif response in ("n", "no"):
            print("Please complete the steps before continuing.")
        else:
            print("Please enter 'Y' or 'N'.")


def main():
    print("Starting environment preparation...")
    prompt_user_background_processes()
    set_brightness_50()
    print("Environment is now standardized. You can proceed to run browser_bench.py.")


if __name__ == "__main__":
    main()
