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


if __name__ == "__main__":
    test_fetch_ticker_brief_parses_real_response_shape()
    print("OK: fetch_ticker_brief parses the real Massive response shape correctly")
