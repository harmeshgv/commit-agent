"""Configuration comparison helpers for lab metrics."""

from __future__ import annotations


def _score_metrics(metrics: dict[str, float]) -> float:
    """Compute ranking score from a config metrics dictionary.

    Input contract:
    - `metrics` should include `valid_rate`, `retry_rate`, and `average_latency`.

    Output contract:
    - Returns a float score where higher is better.

    Side effects:
    - None.
    """

    valid_rate = float(metrics.get("valid_rate", 0.0))
    retry_rate = float(metrics.get("retry_rate", 0.0))
    average_latency = float(metrics.get("average_latency", 0.0))

    # Favor correctness first, then efficiency and stability.
    return (valid_rate * 100.0) - (retry_rate * 20.0) - (average_latency / 1000.0)


def compare_configs(metrics_by_config: dict[str, dict]) -> list[tuple[str, float]]:
    """Rank configurations using a composite quality/efficiency score.

    Input contract:
    - `metrics_by_config` maps config IDs to metrics dictionaries.

    Output contract:
    - Returns `(config_id, score)` tuples sorted descending by score.

    Side effects:
    - None.
    """

    scored: list[tuple[str, float]] = []
    for config_id, metrics in metrics_by_config.items():
        scored.append((config_id, _score_metrics(metrics)))

    scored.sort(key=lambda item: (-item[1], item[0]))
    return scored
