"""Engine orchestration layer.

This module coordinates analyzer -> generator -> validator and returns a single
`EngineResult`. It receives structured runtime config and applies fallback logic
without performing any config parsing.
"""

from __future__ import annotations

import time
from typing import Any

from config.loader import ConstraintConfig, ProdConfig
from core.analyzer import read_git_context
from core.generator import generate_commit
from core.logger import debug_log, info_log
from core.types import DiffContext, EngineResult
from core.validator import validate_commit


def _constraints_to_dict(constraints: ConstraintConfig) -> dict[str, int]:
    """Convert typed constraints into validator mapping.

    Input contract:
    - `constraints` is a `ConstraintConfig` dataclass.

    Output contract:
    - Returns dictionary with `min` and `max` integer bounds.

    Side effects:
    - None.
    """

    return {"min": constraints.min, "max": constraints.max}


def _run_target(
    context: DiffContext,
    strategy: str,
    provider: str,
    model: str,
    intent: str | None,
    constraints: dict[str, Any],
    max_retries: int,
    debug: bool,
) -> EngineResult:
    """Run one configured provider/model/strategy target with retries.

    Input contract:
    - `context` is preloaded diff context.
    - `strategy`, `provider`, `model` identify a concrete generation target.
    - `constraints` is validator-compatible bounds mapping.
    - `max_retries` is a non-negative retry cap.

    Output contract:
    - Returns `EngineResult` for this target only.

    Side effects:
    - Calls generator/provider and validator repeatedly until success/exhaustion.
    """

    started_at = time.perf_counter()
    retries = 0
    last_error: str | None = None
    last_violations: list[str] = []
    last_meta: dict[str, Any] = {}

    while retries <= max_retries:
        generated = generate_commit(
            context=context,
            prompt_strategy=strategy,
            provider_name=provider,
            model=model,
            intent=intent,
            constraints=constraints,
            feedback=None,
            debug=debug,
        )

        if generated.commit is None:
            last_error = generated.error or "unknown"
            last_meta = generated.meta
        else:
            validation = validate_commit(generated.commit, constraints)
            generated.commit.word_count = validation.word_count
            if not validation.violations:
                latency_ms = int((time.perf_counter() - started_at) * 1000)
                return EngineResult(
                    commit=generated.commit,
                    violations=[],
                    retries=retries,
                    latency_ms=latency_ms,
                    error=None,
                    meta={
                        "provider": provider,
                        "model": model,
                        "strategy": strategy,
                        **generated.meta,
                    },
                )
            last_violations = list(validation.violations)
            last_error = "validation_failed"

        retries += 1

    meta: dict[str, Any] = {"provider": provider, "model": model, "strategy": strategy}
    meta.update(last_meta)

    latency_ms = int((time.perf_counter() - started_at) * 1000)
    return EngineResult(
        commit=None,
        violations=last_violations,
        retries=max_retries,
        latency_ms=latency_ms,
        error=last_error,
        meta=meta,
    )


def run_once(config: ProdConfig, intent: str | None = None, debug: bool = False) -> EngineResult:
    """Run production generation with automatic fallback target handling.

    Input contract:
    - `config` is a fully-loaded `ProdConfig` object.
    - `intent` is optional user guidance text.
    - `debug` toggles debug logging forwarded to generation path.

    Output contract:
    - Returns `EngineResult` from primary target or fallback target.

    Side effects:
    - Reads git context once.
    - Calls provider-backed generation and validation.
    """

    constraints = _constraints_to_dict(config.constraints)
    info_log("Reading git context...", color="cyan")
    context = read_git_context(debug=debug)

    info_log(
        "Calling primary provider...",
        payload={"provider": config.provider, "model": config.model},
        color="cyan",
    )
    primary = _run_target(
        context=context,
        strategy=config.strategy,
        provider=config.provider,
        model=config.model,
        intent=intent,
        constraints=constraints,
        max_retries=config.max_retries,
        debug=debug,
    )
    primary.meta["timeout_seconds"] = config.timeout_seconds
    primary.meta["fallback_used"] = False

    if primary.commit is not None:
        info_log("Commit generated successfully.", color="green")
        return primary

    debug_log(debug, "primary_failed", {"error": primary.error, "meta": primary.meta})

    if primary.error == "provider_error" and "GROQ_API_KEY" in primary.meta.get(
        "reason", ""
    ):
        info_log(
            "GROQ_API_KEY is not set. Please set the GROQ_API_KEY environment variable.",
            color="red",
        )
        primary.error = "GROQ_API_KEY is not set."
        return primary

    info_log(
        "Primary provider failed. Falling back to fallback provider...",
        payload={"provider": config.fallback.provider, "model": config.fallback.model},
        color="yellow",
    )
    fallback = _run_target(
        context=context,
        strategy=config.fallback.strategy,
        provider=config.fallback.provider,
        model=config.fallback.model,
        intent=intent,
        constraints=constraints,
        max_retries=config.max_retries,
        debug=debug,
    )
    fallback.meta["timeout_seconds"] = config.timeout_seconds
    fallback.meta["fallback_used"] = True
    fallback.meta["primary_error"] = primary.error
    fallback.meta["primary_retries"] = primary.retries

    if fallback.commit is not None:
        info_log("Commit generated successfully with fallback provider.", color="green")
    else:
        info_log("Fallback provider also failed.", color="red")

    return fallback
