"""Batch experiment execution helpers for lab mode."""

from __future__ import annotations

from dataclasses import dataclass

from config.loader import LabBatchConfig, LabSingleConfig, load_lab_config
from core.logger import RunLogger
from core.types import EngineResult
from lab.runner import run_single_experiment


@dataclass(slots=True)
class BatchExperimentResult:
    """One executed batch experiment result row.

    Input contract:
    - `config_id` uniquely identifies one generated combination.
    - `provider`, `model`, `strategy`, and `constraint_label` describe that row.
    - `result` is the engine output for that row.

    Output contract:
    - Structured row used by metrics/reporting layers.

    Side effects:
    - None.
    """

    config_id: str
    provider: str
    model: str
    strategy: str
    constraint_label: str
    result: EngineResult


def _expand_batch_matrix(batch_config: LabBatchConfig) -> list[tuple[str, LabSingleConfig]]:
    """Expand batch matrix into concrete single-run configurations.

    Input contract:
    - `batch_config` contains providers/models, strategies, and constraints.

    Output contract:
    - Returns list of `(constraint_label, LabSingleConfig)` combinations.

    Side effects:
    - None.
    """

    expanded: list[tuple[str, LabSingleConfig]] = []
    for provider, models in batch_config.providers.items():
        for model in models:
            for strategy in batch_config.strategies:
                for constraint_label, constraint in batch_config.constraints.items():
                    expanded.append(
                        (
                            constraint_label,
                            LabSingleConfig(
                                provider=provider,
                                model=model,
                                strategy=strategy,
                                constraints=constraint,
                            ),
                        )
                    )
    return expanded


def run_batch_experiments(
    batch_config: LabBatchConfig,
    max_retries: int = 3,
    timeout_seconds: int = 60,
    intent: str | None = None,
    debug: bool = False,
) -> list[BatchExperimentResult]:
    """Run all generated batch combinations and log each run.

    Input contract:
    - `batch_config` defines matrix values for providers/models/strategies/constraints.
    - `max_retries`, `timeout_seconds`, `intent`, and `debug` are execution controls.

    Output contract:
    - Returns ordered list of `BatchExperimentResult` rows.

    Side effects:
    - Executes core engine per generated combination.
    - Appends machine-readable run logs via `RunLogger`.
    """

    logger = RunLogger()
    rows: list[BatchExperimentResult] = []

    for index, (constraint_label, single_config) in enumerate(_expand_batch_matrix(batch_config), start=1):
        result = run_single_experiment(
            single_config=single_config,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            intent=intent,
            debug=debug,
        )
        logger.log_run(result)

        row = BatchExperimentResult(
            config_id=(
                f"{index}:{single_config.provider}:{single_config.model}:"
                f"{single_config.strategy}:{constraint_label}"
            ),
            provider=single_config.provider,
            model=single_config.model,
            strategy=single_config.strategy,
            constraint_label=constraint_label,
            result=result,
        )
        rows.append(row)

    return rows


def run_batch_from_config(
    config_path: str = "config/lab.yaml",
    max_retries: int = 3,
    timeout_seconds: int = 60,
    intent: str | None = None,
    debug: bool = False,
) -> list[BatchExperimentResult]:
    """Load lab config and run batch mode combinations.

    Input contract:
    - `config_path` points to lab YAML config file.
    - Remaining args override execution controls.

    Output contract:
    - Returns structured list of `BatchExperimentResult` rows.

    Side effects:
    - Reads lab YAML from disk.
    - Executes and logs all batch combinations.
    """

    lab_config = load_lab_config(config_path)
    return run_batch_experiments(
        batch_config=lab_config.batch,
        max_retries=max_retries,
        timeout_seconds=timeout_seconds,
        intent=intent,
        debug=debug,
    )
