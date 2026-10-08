import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))

from ticker_intake import TickerBrief, fetch_ticker_brief  # noqa: E402

SNAPSHOT_RESPONSE = {
    "ticker": {
        "ticker": "AAPL",
        "todaysChangePerc": 2.18579234972679,
        "todaysChange": 7.2,
        "day": {"c": 336.56, "v": 22442965, "o": 330.8, "h": 339.5, "l": 330.1401},
        "prevDay": {"c": 329.4},
    }
}

NEWS_RESPONSE = {
    "results": [
        {"title": "Stock Market Indexes Rally on Inflation Data"},
        {"title": "The Fed's Preferred Inflation Metric Came in Cooler Than Expected"},
        {"title": "Broadcom vs. SK Hynix: Which Technology Stock Is a Better Buy"},
    ]
}


def test_fetch_ticker_brief_parses_real_response_shape():
    with patch("ticker_intake._massive_get") as mock_get, patch.dict(
        "os.environ", {"MASSIVE_API_KEY": "fake-key-for-test"}
    ):
        mock_get.side_effect = [SNAPSHOT_RESPONSE, NEWS_RESPONSE]
        brief = fetch_ticker_brief("AAPL")

    assert brief == TickerBrief(
        symbol="AAPL",
        price=336.56,
        day_change_pct=2.18579234972679,
        volume=22442965,
        headlines=[
            "Stock Market Indexes Rally on Inflation Data",
            "The Fed's Preferred Inflation Metric Came in Cooler Than Expected",
            "Broadcom vs. SK Hynix: Which Technology Stock Is a Better Buy",
        ],
    )
    assert mock_get.call_args_list[0].args == (
        "/v2/snapshot/locale/us/markets/stocks/tickers/AAPL",
    )
    assert mock_get.call_args_list[1].args[0] == "/v2/reference/news"


def test_fetch_ticker_brief_before_market_open_uses_previous_close():
    premarket = {"ticker": {"todaysChangePerc": 0, "day": {"c": 0, "v": 0}, "min": {}, "prevDay": {"c": 336.67}}}
    with patch("ticker_intake._massive_get") as mock_get:
        mock_get.side_effect = [premarket, {"results": []}]
        brief = fetch_ticker_brief("AAPL")

    assert brief.price == 336.67
    assert brief.volume == 0


def test_fetch_ticker_brief_casts_float_volume_to_int():
    snapshot = {"ticker": {**SNAPSHOT_RESPONSE["ticker"], "day": {"c": 338.49, "v": 13947783.0}}}
    with patch("ticker_intake._massive_get") as mock_get:
        mock_get.side_effect = [snapshot, NEWS_RESPONSE]
        brief = fetch_ticker_brief("AAPL")

    assert brief.volume == 13947783
    assert isinstance(brief.volume, int)


if __name__ == "__main__":
    test_fetch_ticker_brief_parses_real_response_shape()
    test_fetch_ticker_brief_before_market_open_uses_previous_close()
    test_fetch_ticker_brief_casts_float_volume_to_int()
    print("OK: fetch_ticker_brief parses the real Massive response shape correctly")
