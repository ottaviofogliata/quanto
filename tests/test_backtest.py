from qsors.backtest.engine import run_backtest
from qsors.config import ExperimentConfig


def test_backtest_smoke():
    cfg = ExperimentConfig.model_validate({"experiment": {}})
    res = run_backtest(cfg)
    assert res["days"] == 10
