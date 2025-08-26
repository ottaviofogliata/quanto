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
from ..data.prices import fetch_prices

logger = get_logger(__name__)


def run_backtest(
    cfg,
    *,
    source: str = "random",
    ticker: str | None = None,
    benchmark: str = "SPY",
    mu: float = 0.0,
    sigma: float = 0.01,
    method: str = "classical",
    asset_class: str = "options",
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
    benchmark : str, optional
        Ticker symbol used as the market benchmark for comparison.
    mu : float, optional
        Mean of the Gaussian used when ``source="random"``.
    sigma : float, optional
        Standard deviation of the Gaussian used when ``source="random"``.
    method : {"classical", "quantum"}, optional
        Algorithm used for synthetic returns when ``source="random"``.
    """

    exp_cfg = getattr(cfg, "experiment", {}) or {}
    universe = exp_cfg.get("universe", ["SPY"])
    if ticker:
        tickers: List[str] = [ticker]
    elif asset_class == "stocks":
        tickers = [universe[0]]
    else:
        tickers = universe

    # Determine the test window from the configuration.  Defaults to 10 days
    # if the nested keys are absent.
    days = exp_cfg.get("backtest", {}).get("walk_forward", {}).get("test_days", 10)

    if source == "real":
        symbols: List[str] = list(dict.fromkeys(tickers + [benchmark]))
        prices = fetch_prices(symbols, period="1mo", days=days)
        strat_returns = prices[tickers[0]].pct_change().dropna().tolist()
        bench_returns = prices[benchmark].pct_change().dropna().tolist()
        days = min(len(strat_returns), len(bench_returns))
        returns = strat_returns[:days]
        benchmark_returns = bench_returns[:days]
    else:
        benchmark_returns = [random.gauss(mu, sigma) for _ in range(days)]
        if method == "quantum":
            if (
                QuantumCircuit is None
                or Estimator is None
                or SparsePauliOp is None
            ):
                # If qiskit is missing fall back to classical randomness
                logger.warning(
                    "Quantum backtest unavailable; using classical random returns.",
                )
                returns = [random.gauss(mu, sigma) for _ in range(days)]
            else:
                # Map classical Gaussian draws to quantum expectation values.
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
    bench_pnl = float(sum(benchmark_returns))
    return {"days": days, "pnl": pnl, "benchmark": bench_pnl}
