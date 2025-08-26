from pathlib import Path
import sys
import types
from pathlib import Path
import sys
import types
import pandas as pd
import pytest

from quanto.config import load_config
from quanto.entangle import run_entanglement_backtest


def test_entanglement_backtest_returns_summary():
    cfg = load_config(Path("examples/config.yaml"))
    res = run_entanglement_backtest(
        cfg, ["SPY", "QQQ"], days=30, source="random",
    )
    assert "entanglement" in res
    assert len(res["correlation_matrix"]) == 2
    assert "pnl" in res and "benchmark" in res
    # With the synthetic drift the strategy should outperform the benchmark
    assert res["pnl"] > res["benchmark"]


def test_entanglement_backtest_real_data_stooq(monkeypatch):
    cfg = load_config(Path("examples/config.yaml"))

    def fail_download(*args, **kwargs):
        raise RuntimeError("network down")

    fake_yf = types.SimpleNamespace(download=fail_download)
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)

    dates = pd.date_range("2023-01-01", periods=5, freq="D")
    fake_df = pd.DataFrame({"Date": dates, "Close": [1, 1.01, 1.02, 1.03, 1.04]})

    def fake_read_csv(*args, **kwargs):
        return fake_df

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)

    res = run_entanglement_backtest(
        cfg, ["SPY", "QQQ"], days=3, source="real",
    )
    assert res["tickers"] == ["SPY", "QQQ"]


def test_entanglement_backtest_real_data_failure(monkeypatch):
    cfg = load_config(Path("examples/config.yaml"))

    def fail_download(*args, **kwargs):
        raise RuntimeError("network down")

    fake_yf = types.SimpleNamespace(download=fail_download)
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)

    def fail_read_csv(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr(pd, "read_csv", fail_read_csv)

    with pytest.raises(RuntimeError):
        run_entanglement_backtest(
            cfg, ["SPY", "QQQ"], days=3, source="real",
        )


def test_entanglement_sets_user_agent(monkeypatch):
    cfg = load_config(Path("examples/config.yaml"))

    captured = {}

    def fake_download(*args, **kwargs):
        captured["ua"] = kwargs["session"].headers.get("User-Agent")
        dates = pd.date_range("2023-01-01", periods=4, freq="D")
        tuples = [("Adj Close", "SPY"), ("Adj Close", "QQQ")]
        index = pd.MultiIndex.from_tuples(tuples)
        data = pd.DataFrame(
            [[1, 1], [1.01, 1.02], [1.02, 1.04], [1.03, 1.06]],
            index=dates,
            columns=index,
        )
        return data

    fake_yf = types.SimpleNamespace(download=fake_download)
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)

    run_entanglement_backtest(
        cfg, ["SPY", "QQQ"], days=3, source="real",
    )
    assert captured["ua"].startswith("Mozilla/")


