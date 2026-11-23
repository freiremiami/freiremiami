import os
import time
from pathlib import Path

import requests

TIKTOK_API_BASE = "https://open.tiktokapis.com/v2"
TOKEN_FILE = Path(__file__).parent / ".tiktok_token.json"


def exchange_code_for_token(auth_code: str, redirect_uri: str) -> dict:
    """One-time step: trade the browser-consent code for access + refresh tokens."""
    response = requests.post(
        f"{TIKTOK_API_BASE}/oauth/token/",
        data={
            "client_key": os.environ["TIKTOK_CLIENT_KEY"],
            "client_secret": os.environ["TIKTOK_CLIENT_SECRET"],
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def _refresh_access_token(refresh_token: str) -> dict:
    response = requests.post(
        f"{TIKTOK_API_BASE}/oauth/token/",
        data={
            "client_key": os.environ["TIKTOK_CLIENT_KEY"],
            "client_secret": os.environ["TIKTOK_CLIENT_SECRET"],
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_access_token() -> str:
    import json

    if not TOKEN_FILE.exists():
        raise RuntimeError(
            "No stored TikTok token. Run the one-time authorize_tiktok.py flow first."
        )
    stored = json.loads(TOKEN_FILE.read_text())
    refreshed = _refresh_access_token(stored["refresh_token"])
    TOKEN_FILE.write_text(json.dumps(refreshed))
    return refreshed["access_token"]


def publish_video(video_path: Path, caption: str, privacy_level: str = "SELF_ONLY") -> dict:
    """Uploads and publishes a video via the Content Posting API.

    privacy_level defaults to SELF_ONLY (private) because posts from an
    unaudited app are restricted to private visibility by TikTok regardless
    of what's requested here — see bots/publisher/README.md.
    """
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    video_size = video_path.stat().st_size

    init_response = requests.post(
        f"{TIKTOK_API_BASE}/post/publish/video/init/",
        headers=headers,
        json={
            "post_info": {"title": caption, "privacy_level": privacy_level},
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": video_size,
                "chunk_size": video_size,
                "total_chunk_count": 1,
            },
        },
        timeout=10,
    )
    init_response.raise_for_status()
    init_data = init_response.json()["data"]
    publish_id = init_data["publish_id"]
    upload_url = init_data["upload_url"]

    with open(video_path, "rb") as video_file:
        video_bytes = video_file.read()
    requests.put(
        upload_url,
        data=video_bytes,
        headers={
            "Content-Type": "video/mp4",
            "Content-Range": f"bytes 0-{video_size - 1}/{video_size}",
        },
        timeout=60,
    ).raise_for_status()

    return _poll_publish_status(publish_id, access_token)


def list_recent_videos(max_count: int = 20) -> list[dict]:
    """Read-only: the account's own recent posts with engagement stats.

    Requires the video.list scope (see authorize_tiktok.py).
    """
    access_token = get_access_token()
    fields = "id,create_time,video_description,view_count,like_count,comment_count,share_count"
    response = requests.post(
        f"{TIKTOK_API_BASE}/video/list/?fields={fields}",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        json={"max_count": max_count},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["data"]["videos"]


def _poll_publish_status(publish_id: str, access_token: str, max_attempts: int = 30) -> dict:
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    for _ in range(max_attempts):
        response = requests.post(
            f"{TIKTOK_API_BASE}/post/publish/status/fetch/",
            headers=headers,
            json={"publish_id": publish_id},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()["data"]
        if data["status"] == "PUBLISH_COMPLETE":
            return data
        if data["status"] == "FAILED":
            raise RuntimeError(f"TikTok publish failed: {data}")
        time.sleep(2)
    raise TimeoutError(f"TikTok publish {publish_id} did not complete in time")
