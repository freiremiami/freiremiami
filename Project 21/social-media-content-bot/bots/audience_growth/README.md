# audience_growth

Finds and grows a **real** audience of people interested in stocks. This is
the "find viewers" role, done legitimately:

- Reads the account's own recent posts on each platform (real engagement
  data, no third-party scraping) and surfaces the best-performing posting
  hour and hashtags from actual view counts
- Cross-promotion (e.g. a TikTok clip teasing the fuller YouTube Short)
- Replying to genuine comments to build community, which platform algorithms
  reward with organic reach

**What this bot never does**: buy views/followers, run bot accounts that
watch/like/comment, or use engagement-pod style reciprocal-view schemes.
Platforms detect and filter that traffic before it counts toward payouts,
and it's a bannable ToS violation on every platform in scope.

## Code status

`analyze_performance(platform)` calls `list_recent_videos()` on
`bots/publisher/tiktok_client.py` / `youtube_client.py` — reusing the same
OAuth tokens `publisher` already holds, just with read-only scopes added
(`video.list` for TikTok, `youtube.readonly` for YouTube; re-run the
relevant `authorize_*.py` if you set those up before this was added). It
groups the account's real posts by hour-of-day to find the best-performing
posting time and ranks hashtags by the total views of posts that used them.
With no post history yet, it falls back to `suggest_hashtags()`'s defaults
and reports "insufficient data" rather than guessing.

## Needs

Same `publisher` setup (see `bots/publisher/README.md`) plus the two extra
read-only scopes above.
