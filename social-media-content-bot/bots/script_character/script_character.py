import sys
from pathlib import Path

import anthropic

sys.path.append(str(Path(__file__).resolve().parents[2] / "shared"))

from compliance import check_script, inject_disclaimer  # noqa: E402

SCRIPT_MODEL = "claude-opus-5-5"

SYSTEM_PROMPT = (
    "You write scripts for a daily short-form video covering one stock ticker. "
    "The video is 30-60 seconds spoken aloud, vertical format, for a general audience. "
    "Write ONLY the spoken narration — no scene directions, no markdown, no headings. "
    "Be factual and grounded in the numbers and headlines given. Never predict future "
    "price moves, never tell the viewer to buy or sell, never claim a return is "
    "guaranteed or safe. Frame it as 'here's what happened today', not advice."
)


def write_script(ticker_brief) -> str:
    client = anthropic.Anthropic()
    headlines = "\n".join(f"- {headline}" for headline in ticker_brief.headlines)
    user_prompt = (
        f"Ticker: {ticker_brief.symbol}\n"
        f"Price: ${ticker_brief.price:.2f}\n"
        f"Day change: {ticker_brief.day_change_pct:+.2f}%\n"
        f"Volume: {ticker_brief.volume:,}\n"
        f"Today's headlines:\n{headlines}\n\n"
        "Write the narration script now."
    )
    response = client.messages.create(
        model=SCRIPT_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return next(block.text for block in response.content if block.type == "text").strip()


def finalize_script(raw_script: str, held_positions: list[str] | None = None) -> str:
    flagged = check_script(raw_script)
    if flagged:
        raise ValueError(f"Script contains banned phrases: {flagged}")
    return inject_disclaimer(raw_script, held_positions)


CHARACTER_REFERENCE_ID = "PLACEHOLDER"  # fixed persona used across every episode
