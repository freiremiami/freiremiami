from dataclasses import dataclass


@dataclass
class GrowthInsight:
    platform: str
    best_posting_time: str
    top_hashtags: list[str]
    notes: str


def analyze_performance(platform: str) -> GrowthInsight:
    # TODO: pull analytics from the platform's read-only analytics API
    # and surface which hashtags/times/formats are driving real watch time
    raise NotImplementedError


def suggest_hashtags(ticker_symbols: list[str]) -> list[str]:
    base = ["#stocks", "#investing", "#stockmarket", "#daytrading"]
    ticker_tags = [f"#{symbol.lower()}" for symbol in ticker_symbols]
    return base + ticker_tags
