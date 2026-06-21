"""Open the fixed Zoom meeting link (browser or Zoom app)."""

import os
import sys
import webbrowser
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

MEETING_ID = os.getenv("ZOOM_MEETING_ID", "").strip()
PASSCODE = os.getenv("ZOOM_PASSCODE", "").strip()


def zoom_url() -> str:
    if not MEETING_ID:
        raise SystemExit("Set ZOOM_MEETING_ID in .env")
    base = f"https://zoom.us/j/{MEETING_ID}"
    return f"{base}?pwd={PASSCODE}" if PASSCODE else base


def main() -> None:
    url = zoom_url()
    print(f"Opening: {url}")
    if not webbrowser.open(url):
        print("Could not open browser. Copy the URL above manually.", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()