"""YAML configuration loader for production and lab execution modes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class ConstraintConfig:
    """Word-count constraint bounds.

    Input contract:
    - `min` and `max` are non-negative integer bounds.

    Output contract:
    - Immutable bound object used by engine and lab runners.

    Side effects:
    - None.
    """

    min: int
    max: int


@dataclass(slots=True)
class FallbackConfig:
    """Fallback generation target used by production engine mode.

    Input contract:
    - `provider`, `model`, and `strategy` identify a complete fallback target.

    Output contract:
    - Structured fallback target for engine orchestration.

    Side effects:
    - None.
    """

    provider: str
    model: str
    strategy: str


@dataclass(slots=True)
class ProdConfig:
    """Production runtime configuration.

    Input contract:
    - Fields must come from `config/prod.yaml`.

    Output contract:
    - Single object passed to production engine execution.

    Side effects:
    - None.
    """

    strategy: str
    provider: str
    model: str
    fallback: FallbackConfig
    constraints: ConstraintConfig
    max_retries: int
    timeout_seconds: int


@dataclass(slots=True)
class LabSingleConfig:
    """Single experiment configuration.

    Input contract:
    - `provider`, `model`, `strategy`, and `constraints` define one run target.

    Output contract:
    - Structured config for single-run lab execution.

    Side effects:
    - None.
    """

    provider: str
    model: str
    strategy: str
    constraints: ConstraintConfig


@dataclass(slots=True)
class LabBatchConfig:
    """Batch experiment matrix definition.

    Input contract:
    - `providers` maps provider names to model identifier lists.
    - `strategies` lists prompt strategies to combine.
    - `constraints` maps labels to constraint bounds.

    Output contract:
    - Structured matrix config consumed by batch runner.

    Side effects:
    - None.
    """

    providers: dict[str, list[str]]
    strategies: list[str]
    constraints: dict[str, ConstraintConfig]


@dataclass(slots=True)
class LabConfig:
    """Top-level lab configuration container.

    Input contract:
    - `single` and `batch` sections must be present in `config/lab.yaml`.

    Output contract:
    - Structured object used by lab execution entrypoints.

    Side effects:
    - None.
    """

    single: LabSingleConfig
    batch: LabBatchConfig


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load one YAML object from disk.

    Input contract:
    - `path` points to a YAML file containing a mapping at root.

    Output contract:
    - Returns root mapping as dictionary.

    Side effects:
    - Reads file contents from disk.
    """

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return payload


def _parse_constraint_config(raw: dict[str, Any]) -> ConstraintConfig:
    """Convert raw mapping into `ConstraintConfig`.

    Input contract:
    - `raw` contains integer-like `min` and `max` keys.

    Output contract:
    - Returns validated `ConstraintConfig` instance.

    Side effects:
    - None.
    """

    return ConstraintConfig(min=int(raw["min"]), max=int(raw["max"]))


def load_prod_config(path: str = "config/prod.yaml") -> ProdConfig:
    """Load production config from YAML file.

    Input contract:
    - `path` points to production YAML schema.

    Output contract:
    - Returns validated `ProdConfig` object.

    Side effects:
    - Reads YAML file from disk.
    """

    payload = _load_yaml(Path(path))
    fallback_raw = payload["fallback"]
    constraints_raw = payload["constraints"]

    if not isinstance(fallback_raw, dict) or not isinstance(constraints_raw, dict):
        raise ValueError("`fallback` and `constraints` sections must be mappings")

    return ProdConfig(
        strategy=str(payload["strategy"]),
        provider=str(payload["provider"]),
        model=str(payload["model"]),
        fallback=FallbackConfig(
            provider=str(fallback_raw["provider"]),
            model=str(fallback_raw["model"]),
            strategy=str(fallback_raw["strategy"]),
        ),
        constraints=_parse_constraint_config(constraints_raw),
        max_retries=int(payload["max_retries"]),
        timeout_seconds=int(payload["timeout_seconds"]),
    )


def load_lab_config(path: str = "config/lab.yaml") -> LabConfig:
    """Load lab configuration from YAML file.

    Input contract:
    - `path` points to lab YAML schema.

    Output contract:
    - Returns validated `LabConfig` object.

    Side effects:
    - Reads YAML file from disk.
    """

    payload = _load_yaml(Path(path))
    single_raw = payload["single"]
    batch_raw = payload["batch"]

    if not isinstance(single_raw, dict) or not isinstance(batch_raw, dict):
        raise ValueError("`single` and `batch` sections must be mappings")

    single_constraints_raw = single_raw["constraints"]
    if not isinstance(single_constraints_raw, dict):
        raise ValueError("`single.constraints` must be a mapping")

    providers_raw = batch_raw["providers"]
    strategies_raw = batch_raw["strategies"]
    constraints_raw = batch_raw["constraints"]

    if not isinstance(providers_raw, dict):
        raise ValueError("`batch.providers` must be a mapping")
    if not isinstance(strategies_raw, list):
        raise ValueError("`batch.strategies` must be a list")
    if not isinstance(constraints_raw, dict):
        raise ValueError("`batch.constraints` must be a mapping")

    providers: dict[str, list[str]] = {}
    for provider_name, models_raw in providers_raw.items():
        if not isinstance(models_raw, list):
            raise ValueError("Each provider model list must be a list")
        providers[str(provider_name)] = [str(model) for model in models_raw]

    strategies = [str(strategy) for strategy in strategies_raw]

    batch_constraints: dict[str, ConstraintConfig] = {}
    for label, bounds_raw in constraints_raw.items():
        if not isinstance(bounds_raw, dict):
            raise ValueError("Each batch constraint entry must be a mapping")
        batch_constraints[str(label)] = _parse_constraint_config(bounds_raw)

    return LabConfig(
        single=LabSingleConfig(
            provider=str(single_raw["provider"]),
            model=str(single_raw["model"]),
            strategy=str(single_raw["strategy"]),
            constraints=_parse_constraint_config(single_constraints_raw),
        ),
        batch=LabBatchConfig(
            providers=providers,
            strategies=strategies,
            constraints=batch_constraints,
        ),
    )
