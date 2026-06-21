"""Append published meeting URLs to a JSON manifest for the citizen hub."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


def append_entry(video: dict, source_file: Path) -> Path:
    rel = os.getenv("MANIFEST_PATH", "../../data/meetings.json")
    manifest_path = (Path(__file__).parent / rel).resolve()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    if manifest_path.exists():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        data = {"meetings": []}

    entry = {
        "published_at": datetime.now(timezone.utc).isoformat(),
        "title": video["title"],
        "youtube_url": video["url"],
        "youtube_id": video["video_id"],
        "source_file": source_file.name,
    }
    data["meetings"].insert(0, entry)
    manifest_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest_path