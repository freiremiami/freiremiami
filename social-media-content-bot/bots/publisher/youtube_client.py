from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = Path(__file__).parent / ".youtube_token.json"
CLIENT_SECRET_FILE = Path(__file__).parent / "youtube_client_secret.json"


def _get_credentials() -> Credentials:
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise RuntimeError(
                "No valid YouTube token. Run the one-time authorize_youtube.py flow first."
            )
        TOKEN_FILE.write_text(creds.to_json())
    return creds


def run_authorization_flow() -> None:
    """One-time setup: opens a browser for consent, stores a refresh token."""
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_FILE.write_text(creds.to_json())
    print(f"Saved token to {TOKEN_FILE}")


def publish_video(video_path: Path, title: str, description: str, privacy_status: str = "private") -> dict:
    """Uploads a video as a YouTube Short (vertical video under 3 minutes)."""
    creds = _get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["shorts", "stocks", "investing"],
                "categoryId": "25",  # News & Politics; adjust if finance content fits another category better
            },
            "status": {"privacyStatus": privacy_status, "selfDeclaredMadeForKids": False},
        },
        media_body=MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4"),
    )

    response = None
    while response is None:
        _, response = request.next_chunk()
    return response
