"""
Watch a local recordings folder and upload new videos to YouTube.

Workflow:
  1. Run open_meeting.bat → join Zoom
  2. Record with OBS or Zoom "Record to this computer"
  3. Save/export into RECORDINGS_DIR
  4. This script detects the new file and uploads automatically

Run once and leave open during/after meetings:
  python watch_and_upload.py
"""

from __future__ import annotations

import os
import shutil
import time
from pathlib import Path

from dotenv import load_dotenv
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from manifest import append_entry
from youtube_upload import upload_video

load_dotenv(Path(__file__).parent / ".env")

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".m4v"}
SETTLE_SECONDS = 15  # wait for file to finish writing


class RecordingHandler(FileSystemEventHandler):
    def __init__(self, recordings_dir: Path, processed_dir: Path) -> None:
        self.recordings_dir = recordings_dir
        self.processed_dir = processed_dir
        self._pending: dict[str, float] = {}

    def on_created(self, event):
        if event.is_directory:
            return
        self._queue(Path(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            return
        self._queue(Path(event.src_path))

    def _queue(self, path: Path) -> None:
        if path.suffix.lower() not in VIDEO_EXTENSIONS:
            return
        if path.parent.resolve() != self.recordings_dir.resolve():
            return
        self._pending[str(path)] = time.time()

    def process_ready(self) -> None:
        now = time.time()
        for key, seen_at in list(self._pending.items()):
            if now - seen_at < SETTLE_SECONDS:
                continue
            path = Path(key)
            del self._pending[key]
            if not path.exists() or path.stat().st_size < 1024 * 1024:
                continue
            self._upload(path)

    def _upload(self, path: Path) -> None:
        print(f"\nNew recording: {path.name} ({path.stat().st_size // (1024*1024)} MB)")
        try:
            result = upload_video(path)
            print(f"Published: {result['url']}")
            manifest = append_entry(result, path)
            print(f"Manifest updated: {manifest}")
            dest = self.processed_dir / path.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(dest))
            print(f"Moved to {dest}")
        except Exception as exc:  # noqa: BLE001
            print(f"FAILED {path.name}: {exc}")


def main() -> None:
    recordings = Path(os.getenv("RECORDINGS_DIR", "")).expanduser()
    processed = Path(os.getenv("PROCESSED_DIR", "")).expanduser()

    if not recordings:
        raise SystemExit("Set RECORDINGS_DIR in .env")
    if not processed:
        processed = recordings.parent / "processed"

    recordings.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)

    handler = RecordingHandler(recordings, processed)
    observer = Observer()
    observer.schedule(handler, str(recordings), recursive=False)
    observer.start()

    print(f"Watching: {recordings}")
    print(f"Processed: {processed}")
    print("Join meeting with open_meeting.bat, record, save here. Ctrl+C to stop.\n")

    try:
        while True:
            handler.process_ready()
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()