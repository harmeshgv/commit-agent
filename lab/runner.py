"""Lab execution helpers for single and batch modes."""

from __future__ import annotations

from typing import Literal

from config.loader import FallbackConfig, LabSingleConfig, ProdConfig, load_lab_config
from core.engine import run_once
from core.types import EngineResult


def _to_prod_config(
    single: LabSingleConfig,
    max_retries: int,
    timeout_seconds: int,
) -> ProdConfig:
    """Convert a single lab run target into production engine config.

    Input contract:
    - `single` is one lab single-run target.
    - `max_retries` and `timeout_seconds` are execution controls.

    Output contract:
    - Returns `ProdConfig` consumable by `core.engine.run_once`.

    Side effects:
    - None.
    """

    return ProdConfig(
        strategy=single.strategy,
        provider=single.provider,
        model=single.model,
        fallback=FallbackConfig(
            provider=single.provider,
            model=single.model,
            strategy=single.strategy,
        ),
        constraints=single.constraints,
        max_retries=max_retries,
        timeout_seconds=timeout_seconds,
    )


def run_single_experiment(
    single_config: LabSingleConfig,
    max_retries: int = 3,
    timeout_seconds: int = 60,
    intent: str | None = None,
    debug: bool = False,
) -> EngineResult:
    """Run one lab experiment target.

    Input contract:
    - `single_config` defines provider/model/strategy/constraints.
    - `max_retries` and `timeout_seconds` are execution controls.
    - `intent` is optional guidance text.
    - `debug` toggles debug logging.

    Output contract:
    - Returns one `EngineResult` for the target.

    Side effects:
    - Executes analyzer/generator/provider/validator through engine.
    """

    prod_config = _to_prod_config(
        single=single_config,
        max_retries=max_retries,
        timeout_seconds=timeout_seconds,
    )
    return run_once(config=prod_config, intent=intent, debug=debug)


def run_single_from_config(
    config_path: str = "config/lab.yaml",
    max_retries: int = 3,
    timeout_seconds: int = 60,
    intent: str | None = None,
    debug: bool = False,
) -> EngineResult:
    """Load lab config and run its configured single mode target.

    Input contract:
    - `config_path` points to lab YAML config.
    - Remaining args override execution controls for this invocation.

    Output contract:
    - Returns one `EngineResult` for `lab.single` target.

    Side effects:
    - Reads lab YAML from disk.
    - Executes engine pipeline.
    """

    lab_config = load_lab_config(config_path)
    return run_single_experiment(
        single_config=lab_config.single,
        max_retries=max_retries,
        timeout_seconds=timeout_seconds,
        intent=intent,
        debug=debug,
    )


def run_mode_from_config(
    mode: Literal["single", "batch"],
    config_path: str = "config/lab.yaml",
    max_retries: int = 3,
    timeout_seconds: int = 60,
    intent: str | None = None,
    debug: bool = False,
) -> EngineResult | list["BatchExperimentResult"]:
    """Load lab config and execute the requested mode.

    Input contract:
    - `mode` selects `single` or `batch` execution.
    - `config_path` points to `lab.yaml`.
    - Remaining args are execution controls.

    Output contract:
    - Returns one `EngineResult` for `single` mode.
    - Returns list of `BatchExperimentResult` rows for `batch` mode.

    Side effects:
    - Reads lab YAML from disk.
    - Executes engine pipeline for selected mode.
    """

    if mode == "single":
        return run_single_from_config(
            config_path=config_path,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            intent=intent,
            debug=debug,
        )

    from lab.batch import BatchExperimentResult, run_batch_from_config

    _ = BatchExperimentResult
    return run_batch_from_config(
        config_path=config_path,
        max_retries=max_retries,
        timeout_seconds=timeout_seconds,
        intent=intent,
        debug=debug,
    )
