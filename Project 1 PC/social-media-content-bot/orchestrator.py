import argparse
import traceback
from pathlib import Path

from bots.ticker_intake.ticker_intake import fetch_ticker_brief
from bots.script_character.script_character import CHARACTER_REFERENCE_ID, finalize_script, write_script
from bots.video_generator.video_generator import generate_video
from bots.publisher.publisher import publish_daily_video
from bots.audience_growth.audience_growth import suggest_hashtags

OUTPUT_DIR = Path("output")
POST_DISCLAIMER = "Not financial advice."


def build_caption(symbol: str) -> str:
    hashtags = " ".join(suggest_hashtags([symbol]))
    return f"{symbol} update. {POST_DISCLAIMER} {hashtags}"


def run_ticker(symbol: str, held_positions: list[str] | None, publish: bool) -> None:
    brief = fetch_ticker_brief(symbol)
    print(f"[{symbol}] intake: ${brief.price:.2f} {brief.day_change_pct:+.2f}% vol {brief.volume:,}")

    script = finalize_script(write_script(brief), held_positions)
    (OUTPUT_DIR / f"{symbol}.txt").write_text(script)
    print(f"[{symbol}] script written to {OUTPUT_DIR / f'{symbol}.txt'}")

    video_path = generate_video(script, CHARACTER_REFERENCE_ID, OUTPUT_DIR / f"{symbol}.mp4")
    print(f"[{symbol}] video rendered to {video_path}")

    if not publish:
        print(f"[{symbol}] --no-publish set, skipping TikTok/YouTube")
        return
    for result in publish_daily_video(video_path, caption=build_caption(symbol)):
        print(f"[{symbol}] published to {result.platform}: {result.url or result.post_id}")


def run_daily_pipeline(
    tickers: list[str], held_positions: list[str] | None = None, publish: bool = True
) -> list[str]:
    """Runs every ticker independently so one bad ticker doesn't stop the rest. Returns the failed symbols."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    failed = []
    for symbol in tickers:
        try:
            run_ticker(symbol.upper(), held_positions, publish)
        except Exception:
            print(f"[{symbol}] FAILED")
            traceback.print_exc()
            failed.append(symbol)
    return failed


if __name__ == "__main__":
    import sys

    parser = argparse.ArgumentParser(description="Turn today's tickers into published short videos.")
    parser.add_argument("tickers", nargs="+", help="e.g. AAPL TSLA")
    parser.add_argument("--held", nargs="*", default=None, help="tickers you hold, disclosed in the video")
    parser.add_argument("--no-publish", action="store_true", help="render the video but don't post it")
    args = parser.parse_args()

    failures = run_daily_pipeline(args.tickers, args.held, publish=not args.no_publish)
    sys.exit(1 if failures else 0)
