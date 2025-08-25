"""Very small backtest engine supporting real or random data."""

from __future__ import annotations

import random
from typing import Dict, List

try:  # optional quantum dependency
    from qiskit import QuantumCircuit  # type: ignore[import-untyped]
    from qiskit.primitives import Estimator  # type: ignore[import-untyped]
    from qiskit.quantum_info import SparsePauliOp  # type: ignore[import-untyped]
except Exception:  # pragma: no cover
    QuantumCircuit = None  # type: ignore
    Estimator = None  # type: ignore
    SparsePauliOp = None  # type: ignore

from ..utils.logging import get_logger

logger = get_logger(__name__)


def run_backtest(
    cfg,
    *,
    source: str = "random",
    ticker: str | None = None,
    mu: float = 0.0,
    sigma: float = 0.01,
    method: str = "classical",
) -> Dict[str, float]:
    """Run a naive backtest on either real or simulated data.

    Parameters
    ----------
    cfg : ExperimentConfig
        Configuration object used to derive default universe and test window.
    source : {"real", "random"}, optional
        Data source to use. ``"real"`` pulls prices from Yahoo Finance while
        ``"random"`` generates daily returns from ``random.gauss``.
    ticker : str, optional
        Single ticker symbol to backtest. Defaults to the first entry in the
        configured universe.
    mu : float, optional
        Mean of the Gaussian used when ``source="random"``.
    sigma : float, optional
        Standard deviation of the Gaussian used when ``source="random"``.
    method : {"classical", "quantum"}, optional
        Algorithm used for synthetic returns when ``source="random"``.
    """

    tickers: List[str] = cfg.experiment.get("universe", ["SPY"])
    if ticker:
        tickers = [ticker]

    days = (
        cfg.experiment.get("backtest", {})
        .get("walk_forward", {})
        .get("test_days", 10)
    )

    if source == "real":
        try:
            import importlib

            yf = importlib.import_module("yfinance")  # type: ignore
        except ImportError as exc:  # pragma: no cover - dependency not available
            raise RuntimeError(
                "yfinance and pandas are required for real data backtests"
            ) from exc

        prices = (
            yf.download(" ".join(tickers), period="1mo", progress=False)["Adj Close"]
            .dropna()
            .tail(days + 1)
        )
        returns = prices.pct_change().dropna().values.flatten().tolist()
        days = len(returns)
    else:
        if method == "quantum":
            if (
                QuantumCircuit is None
                or Estimator is None
                or SparsePauliOp is None
            ):
                logger.warning(
                    "Quantum backtest unavailable; using classical random returns."
                )
                returns = [random.gauss(mu, sigma) for _ in range(days)]
            else:
                op = SparsePauliOp("Z")
                est = Estimator()
                returns = []
                for _ in range(days):
                    theta = random.gauss(mu, sigma)
                    circ = QuantumCircuit(1)
                    circ.rx(theta, 0)
                    result = est.run(circ, op).result()
                    value = (1 - result.values[0]) / 2
                    returns.append(float(value))
        else:
            returns = [random.gauss(mu, sigma) for _ in range(days)]

    pnl = float(sum(returns))
    return {"days": days, "pnl": pnl}
