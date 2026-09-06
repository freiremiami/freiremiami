from dataclasses import dataclass


@dataclass
class TickerBrief:
    symbol: str
    price: float
    day_change_pct: float
    volume: int
    headlines: list[str]


def fetch_ticker_brief(symbol: str) -> TickerBrief:
    # TODO: wire to Alpha Vantage GLOBAL_QUOTE + NEWS_SENTIMENT (or Polygon/IEX)
    raise NotImplementedError


def build_daily_briefs(tickers: list[str]) -> list[TickerBrief]:
    return [fetch_ticker_brief(symbol) for symbol in tickers]
