"""QAOA portfolio optimizer with annealing fallback."""

from __future__ import annotations

from typing import Any, Dict

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None  # type: ignore

from ..utils.logging import get_logger

logger = get_logger(__name__)

try:  # optional quantum packages
    from qiskit_optimization import QuadraticProgram  # type: ignore[import-untyped]
    from qiskit_optimization.algorithms import MinimumEigenOptimizer  # type: ignore[import-untyped]
    from qiskit_algorithms.optimizers import COBYLA  # type: ignore[import-untyped]
    from qiskit_algorithms.minimum_eigensolvers import QAOA  # type: ignore[import-untyped]
    from qiskit.primitives import Sampler  # type: ignore[import-untyped]
except Exception:  # pragma: no cover
    MinimumEigenOptimizer = None  # type: ignore


def optimize(cfg) -> Dict[str, Any]:
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
    assert np is not None
    profits = [5.0, 4.0, 3.0]
    costs = [1000.0, 800.0, 500.0]
    budget = cfg.experiment["constraints"]["budget"]
    qp = QuadraticProgram()
    for i in range(len(profits)):
        qp.binary_var(name=f"x{i}")
    qp.maximize(linear=profits)
    qp.linear_constraint(linear=costs, sense="<=", rhs=float(budget), name="budget")
    sampler = Sampler()
    qaoa = QAOA(sampler=sampler, reps=1, optimizer=COBYLA(maxiter=5))
    optimizer = MinimumEigenOptimizer(qaoa)
    res = optimizer.solve(qp)
    assert res.x is not None
    selection = [i for i, v in enumerate(res.x) if v > 0.5]
    return {"selection": selection, "method": "qaoa"}
