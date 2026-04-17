"""Environment preparation helpers."""

from __future__ import annotations

import subprocess


def set_brightness_50() -> None:
    print("Setting screen brightness to ~50%...")
    applescript = """
    tell application "System Events"
        repeat 32 times
            key code 145
        end repeat

        delay 0.5

        repeat 8 times
            key code 144
        end repeat
    end tell
    """
    try:
        subprocess.run(["osascript", "-e", applescript], check=True)
        print("Screen brightness set.")
    except subprocess.CalledProcessError as exc:
        print(
            "Warning: Could not automatically set screen brightness. "
            f"Please do it manually. Error: {exc}"
        )


def prompt_user_background_processes() -> None:
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
        if response in ("n", "no"):
            print("Please complete the steps before continuing.")
            continue
        print("Please enter 'Y' or 'N'.")


def run_prep() -> None:
    print("Starting environment preparation...")
    prompt_user_background_processes()
    set_brightness_50()
    print("Environment is now standardized.")
    print("Recommended next step: browserbench doctor")
    print("Then run: browserbench run")

