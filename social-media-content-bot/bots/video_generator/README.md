# video_generator

Renders the final vertical video from the finalized script + character
reference: TTS voiceover, visuals, on-screen disclaimer text burned into
the frame (not just in the description, so it survives re-uploads/clips).

**Input**: finalized script + character reference from `script_character`.

**Output**: an `.mp4` file ready for `publisher`.

## Provider: HeyGen

Chosen over Sora/Runway because this use case is "one consistent host
narrating a script," which is exactly what avatar-video platforms are built
for — a persistent `avatar_id` guarantees the same face across every
episode, and the script's TTS voiceover comes from the same API call. (Sora's
developer API was also shut down by OpenAI on 2026-09-24, so it's off the
table regardless.)

`generate_video()` calls `POST /v2/video/generate` with the avatar + voice +
script, polls `GET /v1/video_status.get` until the render completes, then
downloads the result. Captions are burned into the frame
(`caption: {"file_format": "srt", "style": "default"}`) so the spoken
disclaimer — already appended to every script by `compliance.py` — shows up
as on-screen text too, not just in the audio.

## One-time setup you need to do

1. Sign up at [heygen.com](https://heygen.com) and buy API access (separate
   pay-as-you-go balance, starts at $5 — the web subscription doesn't include
   API credits)
2. Create a reusable avatar once (photo/video avatar upload, ~$1 one-time) —
   this becomes your fixed host persona. Copy its `avatar_id`.
3. Pick a voice from HeyGen's voice library (`GET /v2/voices`) and copy its
   `voice_id`.
4. Put `HEYGEN_API_KEY`, `HEYGEN_AVATAR_ID`, `HEYGEN_VOICE_ID` in `.env` —
   `script_character.py` reads `HEYGEN_AVATAR_ID` automatically as
   `CHARACTER_REFERENCE_ID`.

## Cost

Roughly $0.02–$0.07/second depending on avatar tier — a 45-second daily
video runs about $1–$3. Confirm current rates on HeyGen's pricing page
before running this at scale.

**Needs**: `HEYGEN_API_KEY`, `HEYGEN_AVATAR_ID`, `HEYGEN_VOICE_ID`.
