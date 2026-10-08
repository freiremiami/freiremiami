import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))

from audience_growth import analyze_performance, suggest_hashtags  # noqa: E402

TIKTOK_VIDEOS = [
    {"create_time": 1758700800, "view_count": 500, "video_description": "AAPL update #stocks #aapl"},
    {"create_time": 1758744000, "view_count": 5000, "video_description": "TSLA news today #stocks #tsla"},
    {"create_time": 1758830400, "view_count": 4800, "video_description": "NVDA rally #stocks #nvda"},
]

YOUTUBE_VIDEOS = [
    {
        "snippet": {"publishedAt": "2026-09-24T14:00:00Z", "description": "AAPL update #stocks #aapl"},
        "statistics": {"viewCount": "200"},
    },
    {
        "snippet": {"publishedAt": "2026-09-25T14:00:00Z", "description": "TSLA news #stocks #tsla"},
        "statistics": {"viewCount": "3000"},
    },
]


def test_analyze_performance_tiktok_finds_best_hour_and_top_hashtags():
    with patch("audience_growth.tiktok_client.list_recent_videos", return_value=TIKTOK_VIDEOS):
        insight = analyze_performance("tiktok")

    assert insight.platform == "tiktok"
    # TSLA (5000) and NVDA (4800) posts share the same hour and outweigh AAPL (500)
    assert insight.best_posting_time != "insufficient data"
    assert "#stocks" in insight.top_hashtags
    assert insight.top_hashtags[0] == "#stocks"  # appears in every post, highest total views
    assert "3 recent posts" in insight.notes


def test_analyze_performance_youtube_uses_real_stats():
    with patch("audience_growth.youtube_client.list_recent_videos", return_value=YOUTUBE_VIDEOS):
        insight = analyze_performance("youtube")

    assert insight.platform == "youtube"
    assert insight.best_posting_time == "14:00 UTC"
    assert "#tsla" in insight.top_hashtags


def test_analyze_performance_handles_no_posts_yet():
    with patch("audience_growth.tiktok_client.list_recent_videos", return_value=[]):
        insight = analyze_performance("tiktok")

    assert insight.best_posting_time == "insufficient data"
    assert insight.top_hashtags == suggest_hashtags([])
    assert "No posts yet" in insight.notes


def test_analyze_performance_rejects_unsupported_platform():
    try:
        analyze_performance("instagram")
        assert False, "expected ValueError"
    except ValueError as e:
        assert "instagram" in str(e)


if __name__ == "__main__":
    test_analyze_performance_tiktok_finds_best_hour_and_top_hashtags()
    test_analyze_performance_youtube_uses_real_stats()
    test_analyze_performance_handles_no_posts_yet()
    test_analyze_performance_rejects_unsupported_platform()
    print("OK: analyze_performance computes real posting-time/hashtag insights correctly")
