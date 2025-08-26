import sys
import types
import pandas as pd
import pytest

from quanto.backtest.engine import run_backtest
from quanto.config import ExperimentConfig


def test_backtest_smoke():
    cfg = ExperimentConfig.model_validate({"experiment": {}})
    res = run_backtest(cfg, source="random")
    assert res["days"] == 10
    assert isinstance(res["pnl"], float)
    assert isinstance(res["benchmark"], float)


def test_backtest_quantum():
    cfg = ExperimentConfig.model_validate({"experiment": {}})
    res = run_backtest(cfg, source="random", method="quantum")
    assert res["days"] == 10
    assert isinstance(res["pnl"], float)
    assert isinstance(res["benchmark"], float)


def test_backtest_real_data_stooq(monkeypatch):
    cfg = ExperimentConfig.model_validate({"experiment": {"universe": ["SPY"]}})

    def fail_download(*args, **kwargs):
        raise RuntimeError("network down")

    fake_yf = types.SimpleNamespace(download=fail_download)
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)

    dates = pd.date_range("2023-01-01", periods=5, freq="D")
    fake_df = pd.DataFrame({"Date": dates, "Close": [1, 1.01, 1.02, 1.03, 1.04]})

    def fake_read_csv(*args, **kwargs):
        return fake_df

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)

    res = run_backtest(cfg, source="real", benchmark="QQQ")
    assert "pnl" in res


def test_backtest_real_data_failure(monkeypatch):
    cfg = ExperimentConfig.model_validate({"experiment": {"universe": ["SPY"]}})

    def fail_download(*args, **kwargs):
        raise RuntimeError("network down")

    fake_yf = types.SimpleNamespace(download=fail_download)
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)

    def fail_read_csv(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr(pd, "read_csv", fail_read_csv)

    with pytest.raises(RuntimeError):
        run_backtest(cfg, source="real", benchmark="QQQ")


def test_backtest_sets_user_agent(monkeypatch):
    cfg = ExperimentConfig.model_validate(
        {
            "experiment": {
                "universe": ["SPY"],
                "backtest": {"walk_forward": {"test_days": 2}},
            }
        }
    )

    captured = {}

    def fake_download(*args, **kwargs):
        captured["ua"] = kwargs["session"].headers.get("User-Agent")
        dates = pd.date_range("2023-01-01", periods=3, freq="D")
        tuples = [("Adj Close", "SPY"), ("Adj Close", "QQQ")]
        index = pd.MultiIndex.from_tuples(tuples)
        data = pd.DataFrame(
            [[1, 1], [1.01, 1.02], [1.02, 1.04]], index=dates, columns=index
        )
        return data

    fake_yf = types.SimpleNamespace(download=fake_download)
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)

    res = run_backtest(cfg, source="real", benchmark="QQQ")
    assert res["days"] == 2
    assert captured["ua"].startswith("Mozilla/")


@pytest.mark.parametrize("asset_class", ["stocks", "options"])
def test_backtest_random_asset_class(asset_class):
    cfg = ExperimentConfig.model_validate({"experiment": {"universe": ["SPY"]}})
    res = run_backtest(cfg, source="random", asset_class=asset_class)
    assert res["days"] == 10
    assert isinstance(res["pnl"], float)


@pytest.mark.parametrize("asset_class", ["stocks", "options"])
def test_backtest_real_asset_class(monkeypatch, asset_class):
    cfg = ExperimentConfig.model_validate({"experiment": {"universe": ["SPY"]}})

    def fake_download(*args, **kwargs):
        dates = pd.date_range("2023-01-01", periods=5, freq="D")
        tuples = [("Adj Close", "SPY"), ("Adj Close", "QQQ")]
        index = pd.MultiIndex.from_tuples(tuples)
        data = pd.DataFrame(
            [[1, 1], [1.01, 1.02], [1.02, 1.04], [1.03, 1.06], [1.04, 1.08]],
            index=dates,
            columns=index,
        )
        return data

    fake_yf = types.SimpleNamespace(download=fake_download)
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)

    res = run_backtest(cfg, source="real", benchmark="QQQ", asset_class=asset_class)
    assert "pnl" in res
