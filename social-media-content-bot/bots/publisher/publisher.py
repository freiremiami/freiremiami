import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import tiktok_client  # noqa: E402
import youtube_client  # noqa: E402


@dataclass
class PublishResult:
    platform: str
    post_id: str
    url: str


def publish_to_tiktok(video_path: Path, caption: str) -> PublishResult:
    result = tiktok_client.publish_video(video_path, caption)
    return PublishResult(platform="tiktok", post_id=result["publish_id"], url=result.get("share_url", ""))


def publish_to_youtube_shorts(video_path: Path, title: str, description: str) -> PublishResult:
    result = youtube_client.publish_video(video_path, title, description)
    video_id = result["id"]
    return PublishResult(
        platform="youtube",
        post_id=video_id,
        url=f"https://youtube.com/shorts/{video_id}",
    )


def publish_daily_video(video_path: Path, caption: str) -> list[PublishResult]:
    results = [publish_to_tiktok(video_path, caption)]
    results.append(publish_to_youtube_shorts(video_path, caption, caption))
    return results
