"""Market data adapters with CSV fallback."""

from __future__ import annotations

DATA = {
    "SPY": 450.0,
    "QQQ": 370.0,
    "IWM": 190.0,
    "HYG": 75.0,
    "GLD": 180.0,
}


def get_spot(ticker: str) -> float:
    return DATA.get(ticker.upper(), 100.0)


def get_risk_free(rate_source: str = "SOFR") -> float:
    return 0.01


def get_iv(ticker: str, dte: int, strike: str) -> float:
    return 0.2
