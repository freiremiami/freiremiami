# publisher

Posts the finished video to TikTok first, then YouTube Shorts, using each
platform's official API — never through browser automation or third-party
"growth" services, both of which risk account bans.

**Input**: rendered `.mp4` + caption/hashtags.

**Output**: the published post IDs/URLs, logged for `audience_growth` and
for your own tracking of what's been posted.

## Code status

`tiktok_client.py` and `youtube_client.py` are fully implemented against
each platform's real API — OAuth token exchange/refresh, upload, and (for
TikTok) publish-status polling. `publisher.py` calls them. None of this can
run until you complete the one-time manual setup below — the accounts, app
registrations, and approvals are steps only you can do.

## Manual setup you need to do (in order)

### 1. TikTok — developer app + audit (~1-2 weeks for audit)

1. Create a TikTok for Business login at [developers.tiktok.com](https://developers.tiktok.com)
2. Create a new app, add the **Content Posting API** product
3. Request scopes `video.publish` and `video.upload`
4. Set a redirect URI for OAuth (any HTTPS URL you control, or `http://localhost:PORT` for local testing)
5. Put `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_REDIRECT_URI` in `.env`
6. Run the one-time auth flow locally: `python authorize_tiktok.py <your redirect_uri>` — it prints a URL, you approve in the browser, paste back the code
7. **Submit for audit** before going live: a privacy policy URL, a demo video showing the full OAuth + upload flow, and a data-handling description. **Until audited, every post lands as private-only** regardless of what `privacy_level` you request — that's a TikTok platform restriction, not a bug here. `publish_video()` defaults to `SELF_ONLY` for exactly this reason.

### 2. YouTube — Google Cloud project + OAuth consent

1. Create a project in [Google Cloud Console](https://console.cloud.google.com)
2. APIs & Services → Library → enable **YouTube Data API v3**
3. APIs & Services → OAuth consent screen → configure it, add scope `youtube.upload`
4. APIs & Services → Credentials → Create Credentials → OAuth client ID → type **Desktop app**
5. Download the JSON, save it as `bots/publisher/youtube_client_secret.json` (gitignored)
6. Run the one-time auth flow locally: `python authorize_youtube.py` — it opens a browser for consent and stores a refresh token
7. A new Cloud project gets **100 video uploads/day** by default — plenty for one video a day; request a quota increase only if you scale up posting frequency

## Needs

- `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_REDIRECT_URI` (env)
- `bots/publisher/youtube_client_secret.json` (downloaded from Google Cloud, gitignored)
- Both one-time `authorize_*.py` scripts run successfully once, locally, before the daily pipeline can post headlessly
