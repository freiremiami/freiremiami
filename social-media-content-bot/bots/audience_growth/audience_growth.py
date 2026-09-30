import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "bots" / "publisher"))

import tiktok_client  # noqa: E402
import youtube_client  # noqa: E402

HASHTAG_PATTERN = re.compile(r"#(\w+)")


@dataclass
class GrowthInsight:
    platform: str
    best_posting_time: str
    top_hashtags: list[str]
    notes: str


def _tiktok_posts() -> list[dict]:
    videos = tiktok_client.list_recent_videos()
    return [
        {
            "posted_at": datetime.fromtimestamp(video["create_time"], tz=timezone.utc),
            "views": video.get("view_count", 0),
            "text": video.get("video_description", ""),
        }
        for video in videos
    ]


def _youtube_posts() -> list[dict]:
    videos = youtube_client.list_recent_videos()
    return [
        {
            "posted_at": datetime.fromisoformat(video["snippet"]["publishedAt"].replace("Z", "+00:00")),
            "views": int(video["statistics"].get("viewCount", 0)),
            "text": video["snippet"].get("description", ""),
        }
        for video in videos
    ]


def _best_hour_utc(posts: list[dict]) -> tuple[int | None, int]:
    views_by_hour = defaultdict(list)
    for post in posts:
        views_by_hour[post["posted_at"].hour].append(post["views"])
    if not views_by_hour:
        return None, 0
    best_hour = max(views_by_hour, key=lambda hour: sum(views_by_hour[hour]) / len(views_by_hour[hour]))
    sample_size = len(views_by_hour[best_hour])
    return best_hour, sample_size


def _top_hashtags(posts: list[dict], limit: int = 5) -> list[str]:
    views_by_tag = defaultdict(int)
    for post in posts:
        for tag in HASHTAG_PATTERN.findall(post["text"]):
            views_by_tag[f"#{tag.lower()}"] += post["views"]
    ranked = sorted(views_by_tag.items(), key=lambda pair: pair[1], reverse=True)
    return [tag for tag, _ in ranked[:limit]]


def analyze_performance(platform: str) -> GrowthInsight:
    """Pulls the account's own recent posts and surfaces what's actually working —
    never fake engagement, just read-only analysis of real performance.
    """
    if platform == "tiktok":
        posts = _tiktok_posts()
    elif platform == "youtube":
        posts = _youtube_posts()
    else:
        raise ValueError(f"Unsupported platform: {platform}")

    if not posts:
        return GrowthInsight(
            platform=platform,
            best_posting_time="insufficient data",
            top_hashtags=suggest_hashtags([]),
            notes="No posts yet on this platform — using default hashtags until there's data to learn from.",
        )

    best_hour, sample_size = _best_hour_utc(posts)
    top_hashtags = _top_hashtags(posts)
    return GrowthInsight(
        platform=platform,
        best_posting_time=f"{best_hour:02d}:00 UTC" if best_hour is not None else "insufficient data",
        top_hashtags=top_hashtags or suggest_hashtags([]),
        notes=f"Based on {len(posts)} recent posts ({sample_size} at the best-performing hour).",
    )


def suggest_hashtags(ticker_symbols: list[str]) -> list[str]:
    base = ["#stocks", "#investing", "#stockmarket", "#daytrading"]
    ticker_tags = [f"#{symbol.lower()}" for symbol in ticker_symbols]
    return base + ticker_tags
