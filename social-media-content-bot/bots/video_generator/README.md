# video_generator

Renders the final vertical video from the finalized script + character
reference: TTS voiceover, visuals, on-screen disclaimer text burned into
the frame (not just in the description, so it survives re-uploads/clips).

**Input**: finalized script + character reference from `script_character`.

**Output**: an `.mp4` file ready for `publisher`.

**Needs**: a video-gen API (Sora/Runway/HeyGen-style) + TTS voice, both keyed
in `shared/config.example.yaml`.
