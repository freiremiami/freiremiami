from pathlib import Path

from bots.ticker_intake.ticker_intake import build_daily_briefs
from bots.script_character.script_character import CHARACTER_REFERENCE_ID, finalize_script, write_script
from bots.video_generator.video_generator import generate_video
from bots.publisher.publisher import publish_daily_video
from bots.audience_growth.audience_growth import suggest_hashtags

OUTPUT_DIR = Path("output")


def run_daily_pipeline(tickers: list[str], held_positions: list[str] | None = None) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    briefs = build_daily_briefs(tickers)

    for brief in briefs:
        raw_script = write_script(brief)
        script = finalize_script(raw_script, held_positions)
        video_path = generate_video(script, CHARACTER_REFERENCE_ID, OUTPUT_DIR / f"{brief.symbol}.mp4")
        hashtags = " ".join(suggest_hashtags([brief.symbol]))
        publish_daily_video(video_path, caption=f"{brief.symbol} update {hashtags}")


if __name__ == "__main__":
    import sys

    run_daily_pipeline(sys.argv[1:])
