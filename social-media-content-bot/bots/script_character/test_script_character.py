import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent))

from script_character import finalize_script, write_script  # noqa: E402


@dataclass
class FakeTickerBrief:
    symbol: str
    price: float
    day_change_pct: float
    volume: int
    headlines: list[str]


def _fake_response(text: str) -> MagicMock:
    block = MagicMock()
    block.type = "text"
    block.text = text
    response = MagicMock()
    response.content = [block]
    return response


def test_write_script_includes_ticker_data_in_prompt():
    brief = FakeTickerBrief(
        symbol="AAPL",
        price=336.56,
        day_change_pct=2.19,
        volume=22442965,
        headlines=["Stock Market Indexes Rally on Inflation Data"],
    )
    with patch("script_character.anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = mock_anthropic_cls.return_value
        mock_client.messages.create.return_value = _fake_response(
            "Apple shares closed up 2.19% today at $336.56 on strong volume..."
        )
        script = write_script(brief)

    assert script.startswith("Apple shares closed up 2.19%")
    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-opus-5-5"
    user_prompt = call_kwargs["messages"][0]["content"]
    assert "AAPL" in user_prompt
    assert "336.56" in user_prompt
    assert "Stock Market Indexes Rally" in user_prompt


def test_finalize_script_rejects_banned_phrases():
    try:
        finalize_script("This is a guaranteed return, buy now!")
        assert False, "expected ValueError"
    except ValueError as e:
        assert "guaranteed return" in str(e)
        assert "buy now" in str(e)


def test_finalize_script_injects_disclaimer_and_disclosure():
    result = finalize_script("Apple shares closed up today.", held_positions=["AAPL"])
    assert "Not financial advice" in result
    assert "the creator holds a position in AAPL" in result


if __name__ == "__main__":
    test_write_script_includes_ticker_data_in_prompt()
    test_finalize_script_rejects_banned_phrases()
    test_finalize_script_injects_disclaimer_and_disclosure()
    print("OK: script_character write_script + finalize_script behave correctly")
