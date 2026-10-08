import os
import time
from pathlib import Path

import requests

HEYGEN_API_BASE = "https://api.heygen.com"
VERTICAL_ASPECT_RATIO = "9:16"


def _headers() -> dict:
    return {"X-Api-Key": os.environ["HEYGEN_API_KEY"], "Content-Type": "application/json"}


def _start_generation(script: str, avatar_id: str, voice_id: str) -> str:
    # v3 replaces POST /v2/video/generate, which HeyGen removes on 2026-10-31.
    response = requests.post(
        f"{HEYGEN_API_BASE}/v3/videos",
        headers=_headers(),
        json={
            "type": "avatar",
            "avatar_id": avatar_id,
            "script": script,
            "voice_id": voice_id,
            "aspect_ratio": VERTICAL_ASPECT_RATIO,
            "resolution": "720p",
            "background": {"value": "#000000"},
            # Renders a second copy with the spoken script (disclaimer included) burned in
            # as captions, so it survives re-uploads/clips rather than living only in the description.
            "caption": {"file_format": "srt", "style": "default"},
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["data"]["video_id"]


def _poll_until_complete(video_id: str, max_attempts: int = 60, poll_interval_sec: int = 10) -> str:
    for _ in range(max_attempts):
        response = requests.get(f"{HEYGEN_API_BASE}/v3/videos/{video_id}", headers=_headers(), timeout=10)
        response.raise_for_status()
        data = response.json()["data"]
        if data["status"] == "completed":
            # video_url is the clean render; only captioned_video_url carries the on-screen disclaimer.
            if not data.get("captioned_video_url"):
                raise RuntimeError(f"HeyGen video {video_id} completed without a captioned version")
            return data["captioned_video_url"]
        if data["status"] == "failed":
            raise RuntimeError(f"HeyGen video generation failed: {data.get('failure_message')}")
        time.sleep(poll_interval_sec)
    raise TimeoutError(f"HeyGen video {video_id} did not complete in time")


def generate_video(script: str, character_reference_id: str, output_path: Path) -> Path:
    """character_reference_id is a HeyGen avatar_id, created once (see README) so the
    same host persona is reused across every episode. HEYGEN_VOICE_ID pins the voice
    the same way.
    """
    if not character_reference_id or character_reference_id == "PLACEHOLDER":
        raise RuntimeError("HEYGEN_AVATAR_ID is not set. Create the host avatar once (see README) and put its id in .env.")
    voice_id = os.environ["HEYGEN_VOICE_ID"]
    video_id = _start_generation(script, character_reference_id, voice_id)
    video_url = _poll_until_complete(video_id)

    video_response = requests.get(video_url, timeout=60)
    video_response.raise_for_status()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(video_response.content)
    return output_path
