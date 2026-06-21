# Meeting Record → YouTube

For **fixed Zoom meetings** where you attend with a password and record locally (no Zoom cloud file access).

## How it works

```
open_meeting.bat  →  join Zoom (fixed link + password)
OBS / Zoom record →  save .mp4 to RECORDINGS_DIR
watch_and_upload  →  auto-upload to YouTube + update meetings.json
```

Runs on **your PC** — not Vercel or GitHub Pages.

## One-time setup

### 1. Google / YouTube

1. [Google Cloud Console](https://console.cloud.google.com/) → new project
2. Enable **YouTube Data API v3**
3. OAuth consent screen (External is fine for personal channel)
4. Create **Desktop app** OAuth credentials → download JSON
5. Save as `scripts/meeting_publish/client_secrets.json`

### 2. Config

```bash
cd scripts/meeting_publish
copy config.example.env .env
# Edit .env — meeting ID, passcode, folder paths
pip install -r ../../requirements.txt
python youtube_auth.py
```

Browser opens once; authorize the YouTube channel that will host recordings.

### 3. OBS (recommended)

| Setting | Value |
|---------|-------|
| Output → Recording format | MP4 |
| Recording path | Same as `RECORDINGS_DIR` in `.env` |
| Capture | Zoom window + desktop audio |

Zoom's built-in **Record to this computer** also works if the host allows recording.

## Each meeting

**Terminal 1** — leave running:
```bash
python watch_and_upload.py
```

**Before meeting:**
```bash
open_meeting.bat
```
Start OBS recording when the meeting begins. Stop when it ends. The watcher uploads automatically.

## Output

- Video on YouTube (`YOUTUBE_PRIVACY` in `.env`, default `unlisted`)
- Entry in `data/meetings.json` for a future meeting hub page on the citizen site

## Files (never commit)

| File | Purpose |
|------|---------|
| `.env` | Meeting ID, passcode, paths |
| `client_secrets.json` | Google OAuth |
| `youtube_token.json` | Saved YouTube auth |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Upload fails auth | Re-run `youtube_auth.py` |
| File never uploads | Confirm save path matches `RECORDINGS_DIR`; wait ~15s after export |
| Huge file / slow upload | Normal for long meetings; resumable upload is built in |
| Host blocks Zoom record | Use OBS instead |