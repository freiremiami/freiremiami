import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "shared"))

from compliance import check_script, inject_disclaimer  # noqa: E402


def write_script(ticker_brief) -> str:
    # TODO: call an LLM with ticker_brief to draft a 30-60s script
    raise NotImplementedError


def finalize_script(raw_script: str, held_positions: list[str] | None = None) -> str:
    flagged = check_script(raw_script)
    if flagged:
        raise ValueError(f"Script contains banned phrases: {flagged}")
    return inject_disclaimer(raw_script, held_positions)


CHARACTER_REFERENCE_ID = "PLACEHOLDER"  # fixed persona used across every episode
