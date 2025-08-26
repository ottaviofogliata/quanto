# AGENTS

## Goals
- Build a quantum-enhanced trading toolkit that works with options, stocks, and ETFs.
- Strategies should aim to beat benchmark market returns ("win the market").

## Documentation
- Maintain `README.md` and `README_IT.md` as 1:1 translations.
- Any change in one README must be mirrored in the other, and each README must link to the other.
- Note in the English README that the Italian version is a complete translation.
- Whenever showcasing CLI command output in the READMEs, explain what each field in the output represents.
- Keep the documentation under `doc/` updated in both English and Italian, providing matched content for each language.

## Notebooks
- Provide a Jupyter notebook for every CLI experiment, including plots and any additional visuals that help interpret results.

## Testing
- Run `pytest`.
- Run representative CLI commands to verify behavior, e.g.:
  - `PYTHONPATH=src python -m quanto.cli backtest --config examples/config.yaml`
  - `PYTHONPATH=src python -m quanto.cli entangle --tickers SPY,QQQ,IWM --config examples/config.yaml`
- Include tests for new features whenever possible.

## Development
- Implement algorithms abstractly so they apply to options, stocks, and ETFs.
- Explore and integrate quantum techniques (such as entanglement-based analysis) for pricing, backtesting, and prediction.
- Run tests and linters for every code change
- For each change, remember to run the main commands and keep the notebooks that use those libraries up to date.
- Keep this `AGENTS.md` up to date as project goals evolve.
