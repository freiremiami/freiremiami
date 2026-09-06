# ticker_intake

Takes today's ticker list (from your existing screener bot) and enriches
each ticker with the context the script writer needs.

**Input**: a list of tickers, e.g. `["AAPL", "TSLA"]`, dropped in around 9:30am.

**Output**: one `TickerBrief` per ticker — price, day change, volume, and the
top 1-3 recent headlines — handed to `bots/script_character`.

**Needs**: `STOCK_DATA_API_KEY` (Alpha Vantage, Polygon, or IEX).
