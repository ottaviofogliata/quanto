import pytest

from quanto.optimize import milp, qaoa
from quanto.config import ExperimentConfig

CFG = ExperimentConfig.model_validate({"experiment": {"constraints": {"budget": 1500}}})


def test_milp():
    res = milp.optimize(CFG)
    assert isinstance(res["selection"], list)


def test_milp_stocks(monkeypatch):
    cfg = ExperimentConfig.model_validate({"experiment": {"constraints": {"budget": 1500}}})

    def fake_fetch(symbols, period, days, sources=None):
        import pandas as pd

        data = {sym: [1.0, 1.1] for sym in symbols}
        return pd.DataFrame(data)

    monkeypatch.setattr(milp, "fetch_prices", fake_fetch)
    res = milp.optimize(cfg, asset_class="stocks", tickers=["AAPL"])
    assert isinstance(res["selection"], list)


def test_qaoa():
    res = qaoa.optimize(CFG)
    assert isinstance(res["selection"], list)


def test_milp_missing_tickers_stocks():
    with pytest.raises(ValueError):
        milp.optimize(CFG, asset_class="stocks")


def test_milp_missing_tickers_options():
    with pytest.raises(ValueError):
        milp.optimize(CFG, asset_class="options")
