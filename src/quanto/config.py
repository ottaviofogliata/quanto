"""Configuration loader using Pydantic and YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from ast import literal_eval

try:
    import yaml  # type: ignore[import-untyped]
except Exception:  # pragma: no cover
    yaml = None  # type: ignore

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover

    class BaseModel:  # type: ignore
        def __init__(self, **data):
            for k, v in data.items():
                setattr(self, k, v)

        @classmethod
        def model_validate(cls, data):
            return cls(**data)

    def Field(default, **kwargs):  # type: ignore
        return default


class ExperimentConfig(BaseModel):
    experiment: Dict[str, Any] = Field(..., description="Experiment configuration")


def load_config(path: str | Path) -> ExperimentConfig:
    """Load a YAML configuration file."""
    text = Path(path).read_text()
    data: Dict[str, Any]
    if yaml:
        data = yaml.safe_load(text)
    else:  # naive fallback for simple key: value pairs
        data = {}
        for line in text.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                v = v.strip()
                if not v:
                    data[k.strip()] = None
                    continue
                try:
                    # ``literal_eval`` avoids executing arbitrary code while still
                    # handling basic Python literals in the fallback parser.
                    data[k.strip()] = literal_eval(v)
                except Exception:
                    data[k.strip()] = v
    return ExperimentConfig.model_validate(data)
