# Example CLI Commands

This guide shows how to run the `quanto` command line interface step by step.
It assumes you have installed the project with `poetry install` and are
running commands from the repository root.  The sample configuration lives in
`examples/config.yaml` and lists a small universe of optionable tickers.

> **Note**
> The `price` command accepts any ticker symbol.  Other commands pull their
> tickers from the `universe` field of the configuration file unless you edit
> it to include additional symbols.

## Classical Monte Carlo Pricing

Estimate the value of an option by simulating many random price paths and
averaging the discounted payoff
\(V_0 = e^{-rT}\,\mathbb{E}[f(S_T)]\).

```bash
poetry run quanto price --ticker SPY --dte 30 --strike "-5%" --method classical
```

The JSON output shows the option price and the statistical error from the
simulations.

## Quantum-Simulated Pricing

Replace the classical Monte Carlo with a quantum amplitude-estimation routine
that, if run on quantum hardware, could reduce the required number of samples
from \(O(1/\epsilon^2)\) to \(O(1/\epsilon)\) for target error \(\epsilon\).
Here we simulate the quantum algorithm on a classical machine.

```bash
poetry run quanto price --ticker SPY --dte 30 --strike "-5%" --method quantum
```

## Portfolio Optimization

Search for the portfolio weights that balance expected return against risk.
The command first attempts a quantum-approximate optimization algorithm (QAOA)
implementation; if that is unavailable it falls back to a classical mixed
integer linear program.

```bash
poetry run quanto optimize
```

## Backtesting

Replay a simple buy-and-hold strategy to generate profit and loss (PnL)
statistics.  By default the price series is generated from random draws, but
passing `--source real` would use real market data when available.
The PnL for each step is computed as
\(\text{PnL} = \Delta S - \text{Premium}\).

```bash
poetry run quanto backtest --ticker SPY
```

## Hilbert Curve Demo

A Hilbert curve is a space-filling fractal that maps multi-dimensional points
onto a one-dimensional path while keeping nearby points close together.  The
command below prints a toy portfolio laid out along a Hilbert curve to
illustrate how such mappings preserve locality.

```bash
poetry run quanto hilbert-demo
```
