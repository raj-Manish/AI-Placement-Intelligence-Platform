"""
Main execution entry point for AI Placement Intelligence Platform.
Runs the Streamlit application interface.
"""

import os
import sys
import subprocess


def run_app():
    """Launches the Streamlit application."""
    ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "ui", "app.py"))

    print("=" * 65)
    print("Launching AI Placement Intelligence Platform...")
    print(f"Target UI: {ui_path}")
    print("=" * 65)

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        ui_path,
        "--server.headless",
        "true",
        "--server.address",
        "localhost",
        "--server.port",
        "8501"
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")


if __name__ == "__main__":
    run_app()
