"""Typer-based command line interface."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from .config import load_config
from .pricing import monte_carlo, quantum_qae
from .optimize import milp, qaoa
from .portfolio import hilbert
from .utils.logging import get_logger

app = typer.Typer(add_completion=False)
logger = get_logger(__name__)


@app.command()
def price(
    ticker: str = typer.Option(...),
    dte: int = typer.Option(..., help="Days to expiry"),
    strike: str = typer.Option(..., help="Strike expression e.g. -5%"),
    method: str = typer.Option("classical", help="classical|quantum"),
    config: Path = typer.Option(Path("examples/config.yaml")),
) -> None:
    cfg = load_config(config)
    if method == "classical":
        res = monte_carlo.price(ticker, dte, strike, cfg)
    else:
        res = quantum_qae.price(ticker, dte, strike, cfg)
    typer.echo(json.dumps(res, indent=2))


@app.command()
def optimize(
    config: Path = typer.Option(Path("examples/config.yaml")),
) -> None:
    cfg = load_config(config)
    res = qaoa.optimize(cfg)
    if not res:
        res = milp.optimize(cfg)
    typer.echo(json.dumps(res, indent=2))


@app.command()
def backtest(
    config: Path = typer.Option(Path("examples/config.yaml")),
    ticker: str = typer.Option("SPY", help="Ticker symbol to backtest"),
    source: str = typer.Option("random", help="real|random"),
    mu: float = typer.Option(0.0, help="Mean for random.gauss"),
    sigma: float = typer.Option(0.01, help="Std dev for random.gauss"),
) -> None:
    cfg = load_config(config)
    from .backtest.engine import run_backtest

    summary = run_backtest(cfg, source=source, ticker=ticker, mu=mu, sigma=sigma)
    typer.echo(json.dumps(summary, indent=2))


@app.command(name="hilbert-demo")
def hilbert_demo(
    config: Path = typer.Option(Path("examples/config.yaml")),
) -> None:
    cfg = load_config(config)
    basis = cfg.experiment["universe"]
    amps = [1.0 / len(basis)] * len(basis)
    portfolio = hilbert.HilbertPortfolio(basis, amps)
    typer.echo(portfolio.pretty())


if __name__ == "__main__":  # pragma: no cover
    app()
