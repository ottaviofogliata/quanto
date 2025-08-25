"""Simulated QAOA optimizer stub."""

from __future__ import annotations

from typing import Dict

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None  # type: ignore

from ..utils.logging import get_logger

logger = get_logger(__name__)

try:  # optional quantum packages
    from qiskit_optimization.algorithms import MinimumEigenOptimizer
    from qiskit_optimization.applications import PortfolioOptimization
    from qiskit.algorithms.optimizers import COBYLA
    from qiskit.primitives import Sampler
    from qiskit.algorithms import QAOA
except Exception:  # pragma: no cover
    MinimumEigenOptimizer = None  # type: ignore


def optimize(cfg) -> Dict[str, float]:
    """Run a toy QAOA optimization or annealing fallback."""
    if MinimumEigenOptimizer is None or np is None:
        logger.warning("QAOA unavailable; using simulated annealing fallback")
        if np is None:
            return {"selection": [], "method": "annealing"}
        profits = np.array([5, 4, 3])
        costs = np.array([1000, 800, 500])
        budget = cfg.experiment["constraints"]["budget"]
        x = np.zeros(len(profits))
        temp = 1.0
        for _ in range(1000):
            i = np.random.randint(len(x))
            x_new = x.copy()
            x_new[i] = 1 - x_new[i]
            if costs @ x_new <= budget:
                delta = profits @ (x_new - x)
                if delta > 0 or np.random.rand() < np.exp(delta / temp):
                    x = x_new
            temp *= 0.99
        selection = [i for i, v in enumerate(x) if v > 0.5]
        return {"selection": selection, "method": "annealing"}
    # simple QAOA portfolio optimization
    profits = [5, 4, 3]
    costs = [1000, 800, 500]
    budget = cfg.experiment["constraints"]["budget"]
    mu = profits
    sigma = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    q = PortfolioOptimization(mu, sigma, budget)
    qp = q.to_quadratic_program()
    sampler = Sampler()
    qaoa = QAOA(sampler, reps=1, optimizer=COBYLA())
    optimizer = MinimumEigenOptimizer(qaoa)
    res = optimizer.solve(qp)
    selection = [i for i, v in enumerate(res.x) if v > 0.5]
    return {"selection": selection, "method": "qaoa"}
