# script_character

Writes the video script for each ticker and renders it through a consistent
AI host persona (the "character" — same face/voice across every episode so
the channel builds a recognizable identity).

**Input**: `TickerBrief` objects from `ticker_intake`.

**Output**: a script (with the disclaimer already injected via
`shared/compliance.py`) plus the character reference to hand to
`video_generator`.

**Needs**: `ANTHROPIC_API_KEY` — `write_script()` calls Claude
(`claude-opus-5-5`) with the ticker's price/change/volume/headlines and a
system prompt that bans buy/sell language and future price predictions.
Every script then passes through `shared/compliance.py`'s `finalize_script()`,
which rejects banned promotional phrases and appends the disclosure block
before anything reaches `video_generator`.

Still needed: a fixed character reference image/seed so the AI host persona
doesn't drift between videos (`CHARACTER_REFERENCE_ID` is a placeholder until
a video-gen provider is chosen — see `bots/video_generator`).
