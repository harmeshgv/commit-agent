"""Metric computation helpers for lab experiment results."""

from __future__ import annotations

from typing import TypedDict

from core.types import EngineResult


class MetricsSummary(TypedDict):
    """Output schema for computed experiment metrics."""

    valid_rate: float
    average_latency: float
    retry_rate: float
    average_word_count: float
    violation_frequency: dict[str, int]


def compute_metrics(results: list[EngineResult]) -> dict[str, object]:
    """Compute aggregate metrics from a list of engine results.

    Input contract:
    - `results` is a list of `EngineResult` items from lab runs.

    Output contract:
    - Returns a metrics dictionary containing:
      `valid_rate`, `average_latency`, `retry_rate`, `average_word_count`,
      and `violation_frequency`.

    Side effects:
    - None.
    """

    if not results:
        return {
            "valid_rate": 0.0,
            "average_latency": 0.0,
            "retry_rate": 0.0,
            "average_word_count": 0.0,
            "violation_frequency": {},
        }

    total_runs = len(results)
    valid_runs = sum(1 for result in results if not result.violations and result.error is None)
    average_latency = sum(result.latency_ms for result in results) / total_runs
    retried_runs = sum(1 for result in results if result.retries > 0)
    retry_rate = retried_runs / total_runs

    word_counts = [
        result.commit.word_count
        for result in results
        if result.commit is not None and result.commit.word_count is not None
    ]
    average_word_count = (
        float(sum(word_counts)) / len(word_counts) if word_counts else 0.0
    )

    violation_frequency: dict[str, int] = {}
    for result in results:
        for violation in result.violations:
            violation_frequency[violation] = violation_frequency.get(violation, 0) + 1

    summary: MetricsSummary = {
        "valid_rate": valid_runs / total_runs,
        "average_latency": average_latency,
        "retry_rate": retry_rate,
        "average_word_count": average_word_count,
        "violation_frequency": violation_frequency,
    }
    return summary
