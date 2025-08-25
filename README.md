# Quanto

Experimental options-trading laboratory for classical vs quantum-simulated methods.

## Quickstart (macOS M3 Pro)

```bash
# clone repository
poetry install --with dev
poetry run quanto --help
```

Optional features:

- GPU (MPS) acceleration: install `torch` with MPS build. The code automatically
  selects the `mps` device when available.
- Quantum tooling: install extras `poetry install -E quantum` to enable
  Qiskit-based primitives. When absent, graceful fallbacks are used.

See [examples/run_commands.md](examples/run_commands.md) for CLI samples.
