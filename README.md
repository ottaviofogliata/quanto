# Quanto
[Leggi la traduzione completa in italiano](README_IT.md)

Experimental trading laboratory for classical vs quantum-simulated methods across
options, stocks, and ETFs.

## Project Overview

Quanto is a research playground that investigates how quantum
algorithms might accelerate the mathematics of derivatives trading as
well as more traditional stock and ETF strategies.
The codebase pairs well-understood classical techniques with
quantum-inspired counterparts so their costs and accuracy can be
compared side by side. At its core, Quanto prices options by
estimating discounted expected payoffs,

$$
V_0 = e^{-rT} \mathbb{E}[f(S_T)],
$$

and explores whether amplitude-estimation style routines can reduce the
sample complexity from $O(1/\epsilon^2)$ to $O(1/\epsilon)$ for a
target error $\epsilon$. Beyond pricing, the project aims to prototype
portfolio optimization, risk backtesting, and other tasks relevant to
systematic options strategies, laying the groundwork for future
experiments on real quantum hardware.

## Installation and Setup

These commands install dependencies and launch the tools locally. The project
uses [Poetry](https://python-poetry.org/) for dependency management; ensure
Python 3.11+ and Poetry are available on your system.

```bash
# clone the repository and enter it
git clone https://github.com/your-org/quanto.git
cd quanto

# install main and development dependencies
poetry install --with dev

# optional extras for quantum algorithms
poetry install -E quantum

# run the test suite to verify the installation
poetry run pytest

# explore the command line interface
poetry run quanto --help

# launch JupyterLab to run the example notebooks
poetry run jupyter lab

```

Optional features:

- GPU (MPS) acceleration: install `torch` with an MPS build. The code
  automatically selects the `mps` device when available.
- Quantum tooling: the `-E quantum` extra installs Qiskit-based primitives. When
  absent, graceful fallbacks are used.

## Jupyter notebooks

A collection of notebooks in the `notebooks/` directory mirrors the CLI
commands and offers visual explorations. Each notebook loads the example
configuration and produces charts or tables helpful for interactive
analysis.

## Comprehensive Guide to the `quanto` CLI

This section is a friendly, self-contained tour of the `quanto` command line
interface. It aims to give newcomers enough background to understand both the
commands themselves and the financial or computational ideas they use. All
examples assume that dependencies were installed with `poetry install` and that
commands are executed from the root of the repository.  Every command can be
applied to option contracts or directly to stocks and ETFs depending on the
ticker symbols supplied.

The project reads its settings from a YAML configuration file—this repository
ships an example at `examples/config.yaml`. The configuration specifies things
like the list of option tickers to consider (the *universe*), numerical
parameters for simulations, and where data files should be stored. Every command
below references that file with `--config examples/config.yaml`.

### Pricing an option with the classical engine

Classical pricing estimates the fair value of a derivative using the familiar
Monte Carlo technique. For a European option with payoff function $f(S_T)$, time
to maturity $T$, and risk-free rate $r$, a basic Monte Carlo price uses

$$
V_0 = e^{-rT} \frac{1}{N}\sum_{i=1}^{N} f(S_T^{(i)}),
$$

where $S_T^{(i)}$ are simulated terminal prices. More paths $N$ yield better
accuracy at the cost of computation time.

The command below prices a SPY put option that is five percent out of the money
(`--strike -5%`) with thirty days to expiration (`--dte 30`). The default
pricing model draws random paths under a geometric Brownian motion assumption.

```bash
poetry run quanto price --ticker SPY --dte 30 --strike -5% --method classical --config examples/config.yaml
```

### Pricing an option with the quantum-simulated engine

Quantum amplitude estimation can quadratically speed up Monte Carlo by reducing
the number of paths needed to estimate the expected payoff. Instead of running
on actual quantum hardware, `quanto` uses a simulator so it will work on any
machine. Conceptually, the algorithm prepares a superposition encoding all
possible price paths, applies the payoff function, and then uses the quantum
phase estimation routine to estimate the mean value $\mu$ with error on the
order of $1/M$ rather than $1/\sqrt{M}$ for $M$ evaluations.

The following command repeats the earlier pricing task using the quantum
simulation engine. Comparing its output with the classical engine illustrates
how quantum techniques might improve efficiency in future hardware generations.

```bash
poetry run quanto price --ticker SPY --dte 30 --strike -5% --method quantum --config examples/config.yaml
```

### Portfolio optimization

Once individual options can be priced, the next question is how to assemble them
into an attractive portfolio. The `optimize` command performs a simple mean-
variance optimization reminiscent of Markowitz portfolio theory. If $w$ is a
vector of position weights, $\mu$ are expected returns, and $\Sigma$ is a
covariance matrix, a common objective is

$$
\min_w \; w^\top \Sigma w - \lambda w^\top \mu,
$$

where $\lambda$ trades off risk versus reward. The optimizer explores the
universe of tickers defined in `config.yaml` and searches for the combination of
weights that best satisfies the chosen objective and any side constraints.

```bash
poetry run quanto optimize --config examples/config.yaml
```

### Backtesting the strategy

Backtesting replays a strategy on historical data to see how it would have
performed. Given an option-pricing model $P$ and a trading rule $R$, the engine
iterates through past market states $\{S_t\}$ and records hypothetical profit
and loss

$$
\text{PnL} = \sum_t R(S_t) - P(S_t).
$$

The resulting metrics—total return, volatility, drawdowns—give an indication of
robustness before deploying real capital. The example command runs a backtest
using the settings defined in the configuration file and compares the results
against a market benchmark.

```bash
poetry run quanto backtest --config examples/config.yaml --ticker QQQ --benchmark SPY
```

Add `--source real` to pull historical prices. The engine first queries Yahoo
Finance and then retries through Stooq before raising an error if both
sources fail. A browser-style User-Agent is sent to Yahoo Finance to reduce
403 errors. The JSON output includes a `benchmark` field showing the cumulative
return of the reference index over the same period:

```json
{
  "days": 10,
  "pnl": 0.0123,
  "benchmark": 0.0087
}
```

Where:

- `days` is the number of trading days simulated.
- `pnl` is the strategy's cumulative return over the period.
- `benchmark` is the cumulative return of the chosen market index.

### Quantum entanglement backtest

Some market dynamics appear linked in ways that resemble quantum
entanglement: movement in one instrument can foreshadow moves in
another. The `entangle` command runs a quantum-inspired algorithm that
either simulates these linkages or pulls real price data for stocks and
ETFs. A configurable correlation strength is applied in simulation mode,
and the routine generates a simple trading rule based on the most
"entangled" ticker.

```bash
poetry run quanto entangle --tickers SPY,QQQ,IWM --source real --config examples/config.yaml
```

Passing `--source real` fetches historical data for the supplied tickers. The
routine queries Yahoo Finance and then Stooq before raising an error if both
sources are unreachable. A browser-style User-Agent is sent to Yahoo Finance to
help avoid 403 blocks. With `--source random`, the configuration file's
`experiment.entanglement.strength` controls the off‑diagonal correlations of the
synthetic price paths. The command returns a JSON summary such as:

```json
{
  "tickers": ["SPY", "QQQ", "IWM"],
  "chosen": "SPY",
  "entanglement": 0.714,
  "pnl": 0.839,
  "benchmark": 0.467,
  "correlation_matrix": [
    [1.0, 0.716, 0.725],
    [0.716, 1.0, 0.700],
    [0.725, 0.700, 1.0]
  ]
}
```

Here:

- `tickers` lists the instruments analyzed.
- `chosen` is the symbol with the highest average correlation to the others.
- `entanglement` is the mean absolute off-diagonal correlation.
- `pnl` is the cumulative return from investing solely in the `chosen` ticker.
- `benchmark` is the return of an equal-weight portfolio of all tickers.
- `correlation_matrix` contains the pairwise correlations between simulated
  returns for each ticker; values near ±1 indicate strong linkage and drive the
  entanglement heuristic.

The accompanying notebook in
`notebooks/entanglement_backtest.ipynb` visualizes the correlation matrix
as a heatmap and plots strategy vs. benchmark performance for further
exploration.

### Hilbert curve demonstration

The Hilbert curve is a space-filling fractal that maps a one-dimensional index
onto a two-dimensional grid while preserving locality: points that are close on
the curve remain near each other in the plane. It is built recursively. Let
$H_1$ be a simple path through four quadrants. To construct $H_{n+1}$, rotate
and connect four copies of $H_n$, yielding a path that visits each of the
$2^{2(n+1)}$ grid cells exactly once. As $n \to \infty$ the curve fills the
entire unit square.

This property makes Hilbert curves useful for indexing multidimensional data.
`quanto` includes a small demo that shows how a point $(x, y)$ in the unit square
is mapped to its Hilbert index $h$. The reverse mapping—recovering $(x, y)$ from
$h$—is also illustrated, emphasizing how locality is largely preserved despite
the dimensionality reduction.

```bash
poetry run quanto hilbert-demo --config examples/config.yaml
```

Running the demo prints a table of coordinates alongside their Hilbert indices
and, in some configurations, plots the curve for visual intuition.

---

This guide has only scratched the surface, but it should equip a newcomer with
the intuition needed to explore the command line interface and the mathematics
behind each feature. Consult the source code and comments for more detailed
information, and experiment with different tickers or model parameters by
editing the configuration file.

