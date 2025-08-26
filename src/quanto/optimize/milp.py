"""MILP optimizer baseline using cvxpy."""

from __future__ import annotations

from typing import Any, Dict, List

from ..data.prices import fetch_prices
from ..utils.logging import get_logger

logger = get_logger(__name__)

try:  # cvxpy optional
    import cvxpy as cp  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    cp = None  # type: ignore
def optimize(
    cfg, *, asset_class: str = "options", tickers: List[str] | None = None
) -> Dict[str, Any]:
    """Simple MILP selecting contracts by EV subject to budget."""

    if asset_class == "stocks":
        symbols = tickers or cfg.experiment.get("universe", [])
        if not symbols:
            raise ValueError("tickers required for stock optimization")
        try:
            fetch_prices(symbols, period="1mo", days=5)
        except Exception as exc:  # pragma: no cover - network dependent
            logger.warning(f"price fetch failed: {exc}")

def optimize(cfg, asset_class: str | None = None) -> Dict[str, Any]:
    """Simple MILP selecting contracts by EV subject to budget."""
    exp_cfg = getattr(cfg, "experiment", {}) or {}
    if asset_class in {"stocks", "options"} and not exp_cfg.get("universe"):
        raise ValueError(f"Tickers required for asset_class '{asset_class}'")
    if cp is None:
        logger.warning("cvxpy unavailable; using greedy fallback")
        ev = [5, 4, 3]
        cost = [1000, 800, 500]
        budget = cfg.experiment["constraints"]["budget"]
        selection: List[int] = []
        spent = 0
        for i, c in enumerate(cost):
            if spent + c <= budget:
                selection.append(i)
                spent += c
        return {"selection": selection, "method": "greedy"}

    ev = [5, 4, 3]
    cost = [1000, 800, 500]
    x = cp.Variable(len(ev), boolean=True)
    budget = cfg.experiment["constraints"]["budget"]
    objective = cp.Maximize(ev @ x)
    constraints = [cost @ x <= budget]
    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.ECOS_BB)
    selection = [i for i, v in enumerate(x.value) if v > 0.5]
    return {"selection": selection, "method": "milp"}
