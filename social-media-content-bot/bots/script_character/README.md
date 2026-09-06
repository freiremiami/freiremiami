# script_character

Writes the video script for each ticker and renders it through a consistent
AI host persona (the "character" — same face/voice across every episode so
the channel builds a recognizable identity).

**Input**: `TickerBrief` objects from `ticker_intake`.

**Output**: a script (with the disclaimer already injected via
`shared/compliance.py`) plus the character reference to hand to
`video_generator`.

**Needs**: an LLM for scriptwriting, and a fixed character reference image/seed
so the persona doesn't drift between videos.
