"""Price data retrieval strategies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

import pandas as pd


class PriceSource(Protocol):
    """Strategy interface for downloading price data."""

    name: str

    def fetch(self, symbols: List[str], period: str, days: int) -> pd.DataFrame:
        """Return a DataFrame of prices for ``symbols``.

        Implementations should return at least ``days + 1`` rows so that daily
        returns can be computed via ``pct_change``.  A :class:`RuntimeError`
        should be raised if no market data is available.
        """


@dataclass
class YFinanceSource:
    """Download data using :mod:`yfinance`."""

    name: str = "yfinance"

    def fetch(self, symbols: List[str], period: str, days: int) -> pd.DataFrame:
        import importlib
        import requests  # type: ignore[import-untyped]

        yf = importlib.import_module("yfinance")  # type: ignore
        session = requests.Session()
        session.headers["User-Agent"] = "Mozilla/5.0"
        prices = (
            yf.download(
                " ".join(symbols),
                period=period,
                progress=False,
                session=session,
            )["Adj Close"]
            .dropna()
            .tail(days + 1)
        )
        if prices.empty:
            raise RuntimeError("no market data returned")
        return prices


@dataclass
class StooqSource:
    """Download data from the stooq dataset."""

    name: str = "stooq"

    def fetch(
        self, symbols: List[str], period: str, days: int
    ) -> pd.DataFrame:  # noqa: D401
        frames = []
        for symbol in symbols:
            url = f"https://stooq.pl/q/d/l/?s={symbol.lower()}.us&i=d"
            df = pd.read_csv(url, parse_dates=["Date"]).set_index("Date")
            frames.append(df["Close"].rename(symbol))
        prices = pd.concat(frames, axis=1).dropna().tail(days + 1)
        if prices.empty:
            raise RuntimeError("no market data returned")
        return prices


def fetch_prices(
    symbols: List[str],
    *,
    period: str,
    days: int,
    sources: List[PriceSource] | None = None,
) -> pd.DataFrame:
    """Fetch price data from the first working data source."""

    sources = sources or [YFinanceSource(), StooqSource()]
    errors: List[tuple[str, Exception]] = []
    for src in sources:
        try:
            return src.fetch(symbols, period, days)
        except Exception as exc:  # pragma: no cover - network dependent
            print(f"{src.name} download failed ({exc}); trying next")
            errors.append((src.name, exc))
    msg = " and ".join(f"{name} ({exc})" for name, exc in errors)
    raise RuntimeError(f"real data fetch failed via {msg}")
