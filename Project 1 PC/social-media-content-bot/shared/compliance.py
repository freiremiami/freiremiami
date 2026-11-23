DISCLAIMER_TEXT = (
    "Not financial advice. For informational and entertainment purposes only. "
    "Do your own research before making any investment decision."
)


def inject_disclaimer(script: str, held_positions: list[str] | None = None) -> str:
    """Appends the required disclosure block to a video script before rendering."""
    lines = [script.strip(), "", DISCLAIMER_TEXT]
    if held_positions:
        tickers = ", ".join(held_positions)
        lines.append(f"Disclosure: the creator holds a position in {tickers}.")
    return "\n".join(lines)


BANNED_PHRASES = [
    "guaranteed return",
    "guaranteed profit",
    "can't lose",
    "buy now",
    "sure thing",
]


def check_script(script: str) -> list[str]:
    """Returns a list of banned phrases found in the script, empty if clean."""
    lowered = script.lower()
    return [phrase for phrase in BANNED_PHRASES if phrase in lowered]
