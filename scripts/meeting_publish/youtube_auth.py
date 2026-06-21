"""One-time YouTube OAuth setup. Run once before watch_and_upload.py."""

import os
from pathlib import Path

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv(Path(__file__).parent / ".env")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
SECRETS = os.getenv("YOUTUBE_CLIENT_SECRETS", "client_secrets.json")
TOKEN = os.getenv("YOUTUBE_TOKEN_PATH", "youtube_token.json")


def main() -> None:
    secrets_path = Path(__file__).parent / SECRETS
    token_path = Path(__file__).parent / TOKEN

    if not secrets_path.exists():
        raise SystemExit(
            f"Missing {secrets_path}\n"
            "Download OAuth client JSON from Google Cloud Console "
            "(YouTube Data API v3 enabled) and save as client_secrets.json"
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), SCOPES)
    creds = flow.run_local_server(port=0)
    token_path.write_text(creds.to_json(), encoding="utf-8")
    print(f"Saved token to {token_path}")


if __name__ == "__main__":
    main()