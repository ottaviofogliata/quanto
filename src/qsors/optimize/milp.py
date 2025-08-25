"""MILP optimizer baseline using cvxpy."""

from __future__ import annotations

from typing import Dict, List

from ..utils.logging import get_logger

logger = get_logger(__name__)

try:  # cvxpy optional
    import cvxpy as cp
except Exception:  # pragma: no cover
    cp = None  # type: ignore


def optimize(cfg) -> Dict[str, float]:
    """Simple MILP selecting contracts by EV subject to budget."""
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
