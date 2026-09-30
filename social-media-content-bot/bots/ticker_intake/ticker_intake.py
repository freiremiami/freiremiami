import os
from dataclasses import dataclass

import requests

MASSIVE_API_BASE = "https://api.massive.com"


@dataclass
class TickerBrief:
    symbol: str
    price: float
    day_change_pct: float
    volume: int
    headlines: list[str]


def _massive_get(path: str, params: dict | None = None) -> dict:
    api_key = os.environ["MASSIVE_API_KEY"]
    response = requests.get(
        f"{MASSIVE_API_BASE}{path}",
        params=params,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def fetch_ticker_brief(symbol: str, headline_count: int = 3) -> TickerBrief:
    snapshot = _massive_get(f"/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}")["ticker"]
    news = _massive_get("/v2/reference/news", {"ticker": symbol, "limit": headline_count})["results"]
    return TickerBrief(
        symbol=symbol,
        price=snapshot["day"]["c"],
        day_change_pct=snapshot["todaysChangePerc"],
        volume=snapshot["day"]["v"],
        headlines=[article["title"] for article in news],
    )


def build_daily_briefs(tickers: list[str]) -> list[TickerBrief]:
    return [fetch_ticker_brief(symbol) for symbol in tickers]
