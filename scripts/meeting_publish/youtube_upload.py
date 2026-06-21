"""Upload a video file to YouTube."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv(Path(__file__).parent / ".env")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_credentials() -> Credentials:
    token_path = Path(__file__).parent / os.getenv("YOUTUBE_TOKEN_PATH", "youtube_token.json")
    if not token_path.exists():
        raise FileNotFoundError(f"Run youtube_auth.py first. Missing {token_path}")

    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def build_title(source_name: str) -> str:
    prefix = os.getenv("MEETING_TITLE_PREFIX", "Public Meeting")
    date_str = datetime.now().strftime("%Y-%m-%d")
    stem = Path(source_name).stem
    if date_str in stem:
        return f"{prefix} — {stem}"
    return f"{prefix} — {date_str}"


def upload_video(file_path: Path) -> dict:
    creds = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": build_title(file_path.name),
            "description": os.getenv(
                "MEETING_DESCRIPTION",
                "Public meeting recording.",
            ),
            "categoryId": "25",  # News & Politics
        },
        "status": {
            "privacyStatus": os.getenv("YOUTUBE_PRIVACY", "unlisted"),
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        str(file_path),
        chunksize=8 * 1024 * 1024,
        resumable=True,
        mimetype="video/*",
    )

    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"  Upload {pct}%", flush=True)

    video_id = response["id"]
    return {
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": body["snippet"]["title"],
    }