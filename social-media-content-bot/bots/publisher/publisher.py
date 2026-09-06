from dataclasses import dataclass
from pathlib import Path


@dataclass
class PublishResult:
    platform: str
    post_id: str
    url: str


def publish_to_tiktok(video_path: Path, caption: str) -> PublishResult:
    # TODO: call the TikTok Content Posting API
    raise NotImplementedError


def publish_to_youtube_shorts(video_path: Path, title: str, description: str) -> PublishResult:
    # TODO: call the YouTube Data API v3 videos.insert
    raise NotImplementedError


def publish_daily_video(video_path: Path, caption: str) -> list[PublishResult]:
    results = [publish_to_tiktok(video_path, caption)]
    results.append(publish_to_youtube_shorts(video_path, caption, caption))
    return results
