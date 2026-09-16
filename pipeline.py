"""
GeoTwinAI - Project Pipeline

This file coordinates the major stages of the GeoTwinAI project.
It does not replace the existing analysis scripts.
"""

import subprocess
import sys
from pathlib import Path


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent


def run_script(script_path):
    """Run a Python script and display its progress."""

    script = PROJECT_ROOT / script_path

    if not script.exists():
        print(f"SKIPPED: {script_path} was not found.")
        return False

    print("\n" + "=" * 60)
    print(f"Running: {script_path}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=PROJECT_ROOT
    )

    if result.returncode == 0:
        print(f"Completed: {script_path}")
        return True
    else:
        print(f"Failed: {script_path}")
        return False


def main():
    """Run the GeoTwinAI workflow."""

    print("=" * 60)
    print("              GeoTwinAI PIPELINE")
    print("=" * 60)
    print("Project: AI-Powered Digital Twin for Smart City Planning")
    print("City: Nagpur")
    print("=" * 60)

    # Main data processing
    run_script("main.py")

    print("\n" + "=" * 60)
    print("GeoTwinAI pipeline execution completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
    