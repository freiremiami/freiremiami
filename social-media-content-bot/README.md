# Social Media Content Bot — Stock Ticker Video Pipeline

Automated pipeline that turns a daily list of stock tickers into short-form
videos, publishes them to TikTok then YouTube Shorts, and grows a real
audience interested in stocks. No fake engagement, no view-botting — every
platform's payout program filters that out and bans accounts for it, so it
would defeat the purpose anyway.

## Daily flow

1. You (or your existing ticker-screener bot) drop today's tickers into
   `bots/ticker_intake/` around 9:30am.
2. `ticker_intake` pulls price/volume/news context for each ticker.
3. `script_character` writes the script and renders it through a consistent
   AI host persona.
4. `video_generator` turns the script + character into the final vertical
   video, with the compliance disclaimer burned in.
5. `publisher` posts to TikTok first, then YouTube Shorts, on schedule.
6. `audience_growth` finds and engages real stock-interested communities
   (hashtags, timing, cross-promotion) — it does not generate fake views.

## Running it

```
python orchestrator.py AAPL TSLA                # full run: intake, script, video, post
python orchestrator.py AAPL --no-publish        # everything except posting; check output/
python orchestrator.py AAPL --held AAPL         # adds the "creator holds a position" disclosure
```

Each ticker runs on its own, so one failure doesn't stop the others; the
script and video for each land in `output/`, and the command exits non-zero
if any ticker failed. `python test_orchestrator.py` runs the whole pipeline
on AAPL with every outside service faked.

## Bots

| Folder | Responsibility |
|---|---|
| `bots/ticker_intake` | Ingest today's tickers, pull price/news/volume context |
| `bots/script_character` | Generate script + consistent AI host persona |
| `bots/video_generator` | Render the final video (TTS, video-gen API) |
| `bots/publisher` | Post to TikTok/YouTube on schedule via official APIs |
| `bots/audience_growth` | Real audience discovery/engagement, not fake views |

## Required accounts / APIs — fill in `.env`

- Stock data: Massive (`MASSIVE_API_KEY`) — snapshot + news endpoints, wired in `ticker_intake.py` ✅
- Scriptwriting: Anthropic (`ANTHROPIC_API_KEY`) — wired in `script_character.py` ✅
- Video generation: HeyGen (`HEYGEN_API_KEY`, `HEYGEN_AVATAR_ID`, `HEYGEN_VOICE_ID`) — wired in `video_generator.py` ✅ (needs a one-time avatar/voice setup — see `bots/video_generator/README.md`)
- TikTok Content Posting API — client code wired (`bots/publisher/tiktok_client.py`), needs your developer app + audit
- YouTube Data API v3 — client code wired (`bots/publisher/youtube_client.py`), needs your OAuth setup
- `bots/audience_growth` — wired ✅, reuses the same TikTok/YouTube OAuth tokens with two added read-only scopes (`video.list`, `youtube.readonly`)

## Compliance — non-negotiable

Every video must:
- Carry a visible "Not financial advice" disclosure
- Disclose any position you hold in a covered ticker
- Avoid guaranteed-return language or "buy now" framing
- Avoid thinly-traded/micro-cap tickers, which draw regulatory scrutiny

See `shared/compliance.py` — every video's script must pass through
`inject_disclaimer()` before it reaches `video_generator`.

## Not included on purpose

No bot that inflates views, likes, follows, or watch time. TikTok/YouTube
payout programs only pay on views from unique real accounts and actively
detect and ban for manipulated engagement — building that would get the
account banned and forfeit any payout already earned.
