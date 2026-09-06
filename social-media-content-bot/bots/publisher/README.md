# publisher

Posts the finished video to TikTok first, then YouTube Shorts, using each
platform's official API — never through browser automation or third-party
"growth" services, both of which risk account bans.

**Input**: rendered `.mp4` + caption/hashtags.

**Output**: the published post IDs/URLs, logged for `audience_growth` and
for your own tracking of what's been posted.

**Needs**: an approved TikTok Content Posting API app, and a YouTube channel
authorized via OAuth for the YouTube Data API v3.
