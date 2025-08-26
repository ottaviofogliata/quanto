"""Typer-based command line interface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import numpy as np

from .config import load_config
from .pricing import monte_carlo, quantum_qae
from .optimize import milp, qaoa
from .portfolio import hilbert
from .entangle import run_entanglement_backtest
from .utils.logging import get_logger

app = typer.Typer(add_completion=False)
logger = get_logger(__name__)


@app.command()
def price(
    asset_class: str = typer.Option("options", help="options|stocks"),
    ticker: str = typer.Option("", help="Ticker symbol"),
    dte: int = typer.Option(0, help="Days to expiry"),
    strike: str = typer.Option("", help="Strike expression e.g. -5%"),
    method: str = typer.Option("classical", help="classical|quantum"),
    asset_class: Optional[str] = typer.Option(
        None, help="Asset class, e.g. options or stocks"
    ),
    config: Path = typer.Option(Path("examples/config.yaml")),
) -> None:
    cfg = load_config(config)
    cfg.asset_class = asset_class
    if asset_class == "stocks":
        if not ticker:
            raise typer.BadParameter("ticker required for stocks")
        from .data.prices import fetch_prices

        prices = fetch_prices([ticker], period="1d", days=1)
        res = {"price": float(prices[ticker].iloc[-1])}
    else:
        if not ticker:
            ticker = cfg.experiment.get("universe", ["SPY"])[0]
        if not dte:
            dte = cfg.experiment.get("dte_days", [30])[0]
        if not strike:
            strike = cfg.experiment.get("strike_grid", ["ATM"])[0]
        if method == "classical":
            res = monte_carlo.price(ticker, dte, strike, cfg)
        else:
            res = quantum_qae.price(ticker, dte, strike, cfg)
    typer.echo(json.dumps(res, indent=2))


@app.command()
def optimize(
    config: Path = typer.Option(Path("examples/config.yaml")),
    method: str = typer.Option("quantum", help="classical|quantum"),
    asset_class: str = typer.Option("options", help="options|stocks"),
    tickers: str = typer.Option("", help="Comma-separated tickers for stocks"),
) -> None:
    cfg = load_config(config)
    cfg.asset_class = asset_class
    syms = [t.strip() for t in tickers.split(",") if t.strip()]
    if asset_class == "stocks" and not syms:
        raise typer.BadParameter("tickers required for stocks")
    if method == "classical":
        res = milp.optimize(cfg, asset_class=asset_class, tickers=syms)
    else:
        res = qaoa.optimize(cfg)
        if not res:
            res = milp.optimize(cfg, asset_class=asset_class, tickers=syms)
    typer.echo(json.dumps(res, indent=2))


@app.command()
def backtest(
    config: Path = typer.Option(Path("examples/config.yaml")),
    benchmark: str = typer.Option("SPY", help="Benchmark ticker symbol"),
    source: str = typer.Option("random", help="real|random"),
    mu: float = typer.Option(0.0, help="Mean for random.gauss"),
    sigma: float = typer.Option(0.01, help="Std dev for random.gauss"),
    method: str = typer.Option("classical", help="classical|quantum"),
    asset_class: str = typer.Option("options", help="options|stocks"),
    tickers: str = typer.Option("", help="Comma-separated tickers"),
) -> None:
    cfg = load_config(config)
    cfg.asset_class = asset_class
    syms = [t.strip() for t in tickers.split(",") if t.strip()]
    if asset_class == "stocks":
        if not syms:
            raise typer.BadParameter("tickers required for stocks")
        ticker = syms[0]
    else:
        ticker = syms[0] if syms else cfg.experiment.get("universe", ["SPY"])[0]
    from .backtest.engine import run_backtest

    summary = run_backtest(
        cfg,
        source=source,
        ticker=ticker,
        benchmark=benchmark,
        mu=mu,
        sigma=sigma,
        method=method,
        asset_class=asset_class,
    )
    typer.echo(json.dumps(summary, indent=2))


@app.command()
def entangle(
    config: Path = typer.Option(Path("examples/config.yaml")),
    tickers: str = typer.Option("SPY,QQQ", help="Comma-separated tickers"),
    days: int = typer.Option(252, help="Trading days to simulate"),
    source: str = typer.Option("random", help="real|random"),
    asset_class: Optional[str] = typer.Option(
        None, help="Asset class, e.g. options or stocks"
    ),
) -> None:
    """Backtest a toy quantum-inspired entanglement between instruments."""
    cfg = load_config(config)
    cfg.experiment["asset_class"] = asset_class or cfg.experiment.get(
        "asset_class", "options"
    )
    syms = [t.strip() for t in tickers.split(",") if t.strip()]
    res = run_entanglement_backtest(cfg, syms, days=days, source=source)
    typer.echo(json.dumps(res, indent=2))


@app.command(name="hilbert-demo")
def hilbert_demo(
    config: Path = typer.Option(Path("examples/config.yaml")),
    asset_class: Optional[str] = typer.Option(
        None, help="Asset class, e.g. options or stocks"
    ),
) -> None:
    cfg = load_config(config)
    cfg.experiment["asset_class"] = asset_class or cfg.experiment.get(
        "asset_class", "options"
    )
    basis = cfg.experiment["universe"]
    amps = np.full(len(basis), 1.0 / len(basis))
    portfolio = hilbert.HilbertPortfolio(basis, amps)
    typer.echo(portfolio.pretty())


if __name__ == "__main__":  # pragma: no cover
    app()
